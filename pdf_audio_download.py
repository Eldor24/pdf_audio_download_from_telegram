"""
Telegram kanalidan PDF, audio va ovozli xabarlarni yuklab oladi.

Fayllar kanalga yuborilgan asl nom bilan saqlanadi. Yuklangan faylning
o'zgartirilgan sanasi xabar yuborilgan vaqtga moslanadi. Natijalar papkasida
_royxat.csv hisoboti yaratiladi.

Faqat o'zingizga tegishli yoki yuklab olishga ruxsatingiz bo'lgan kanallarda ishlating.

O'rnatish:        pip install -r requirements.txt
Ishga tushirish:  python pdf_audio_download.py
"""

import asyncio
import csv
import os
import re
from dataclasses import dataclass, field
from datetime import timezone
from typing import Literal, TypedDict

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.custom import Message
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeFilename


# Telegram API ma'lumotlarini my.telegram.org saytidan oling.
API_ID = 1234
API_HASH = "api_hash"

# Kanal ID'sini yoki ochiq kanalning @username qiymatini kiriting.
CHANNEL: int | str = -1003768657126

# Yuklangan fayllar va CSV hisoboti shu papkaga yoziladi.
SAVE_DIR = "cefr"

# Bir vaqtda yuklanadigan fayllar soni. Odatda 2-4 oralig'i tavsiya qilinadi.
PARALLEL_DOWNLOADS = 3

# Qaysi turdagi fayllar yuklanishini tanlang.
DOWNLOAD_PDF = True
DOWNLOAD_AUDIO = True
DOWNLOAD_VOICE = True
DOWNLOAD_OTHER_DOCS = False

SESSION_NAME = "session_channel"
MAX_DOWNLOAD_ATTEMPTS = 5
TASKS_PER_BATCH = 50
RETRY_DELAY_SECONDS = 3

MediaKind = Literal["pdf", "audio", "voice", "doc"]

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


class ReportRow(TypedDict):
    tartib: int
    xabar_id: int
    sana_UTC: str
    turi: str
    file: str
    izoh: str


@dataclass
class DownloadStats:
    downloaded: int = 0
    skipped: int = 0
    failed_message_ids: list[int] = field(default_factory=list)


def safe_filename(text: str) -> str:
    """Windows fayl nomida ishlatilmaydigan belgilarni bo'shliq bilan almashtiradi."""
    cleaned = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", text)
    cleaned = cleaned.strip().rstrip(".")
    return cleaned[:150] or "fayl"


def classify_message(message: Message) -> MediaKind | None:
    """Xabardagi hujjat turini aniqlaydi va sozlamaga mosligini tekshiradi."""
    if not message.document:
        return None

    if message.voice:
        return "voice" if DOWNLOAD_VOICE else None

    if message.audio:
        return "audio" if DOWNLOAD_AUDIO else None

    mime_type = (message.file.mime_type or "").lower()
    extension = (message.file.ext or "").lower()

    if mime_type == "application/pdf" or extension == ".pdf":
        return "pdf" if DOWNLOAD_PDF else None

    return "doc" if DOWNLOAD_OTHER_DOCS else None


def get_file_extension(message: Message, kind: MediaKind) -> str:
    """Telegram bergan kengaytmani, u bo'lmasa turga mos kengaytmani qaytaradi."""
    if message.file.ext:
        return message.file.ext

    default_extensions = {
        "voice": ".ogg",
        "audio": ".mp3",
        "pdf": ".pdf",
        "doc": ".pdf",
    }
    return default_extensions[kind]


def get_original_filename_parts(
    message: Message, kind: MediaKind
) -> tuple[str, str]:
    """Xabar atributlaridan faylning asosiy nomi va kengaytmasini tayyorlaydi."""
    original_filename = None
    audio_title = None
    audio_performer = None

    for attribute in message.document.attributes:
        if isinstance(attribute, DocumentAttributeFilename):
            original_filename = attribute.file_name
        elif isinstance(attribute, DocumentAttributeAudio):
            audio_title = attribute.title
            audio_performer = attribute.performer

    file_extension = get_file_extension(message, kind)

    if original_filename:
        base_name, extension = os.path.splitext(original_filename)
        has_real_extension = (
            extension[1:].isalnum() and 1 <= len(extension[1:]) <= 5
        )
        if not has_real_extension:
            # Masalan, "4.11.2026 Aprel" nomiga haqiqiy kengaytmani qo'shadi.
            base_name = original_filename
            extension = file_extension
        return base_name, extension

    if audio_title:
        if audio_performer:
            return f"{audio_performer} - {audio_title}", file_extension
        return audio_title, file_extension

    fallback_names = {
        "voice": "ovozli_xabar",
        "audio": "audio",
        "pdf": "hujjat",
        "doc": "fayl",
    }
    return fallback_names[kind], file_extension


def build_filename(
    message: Message, kind: MediaKind, used_names: set[str]
) -> str:
    """Asl nomni saqlaydi va takroriy nomlarga (2), (3) kabi qo'shimcha qo'shadi."""
    base_name, extension = get_original_filename_parts(message, kind)
    safe_base_name = safe_filename(base_name)
    filename = f"{safe_base_name}{extension}"

    duplicate_number = 2
    while filename.lower() in used_names:
        filename = f"{safe_base_name} ({duplicate_number}){extension}"
        duplicate_number += 1

    used_names.add(filename.lower())
    return filename


def make_report_row(
    message: Message, order: int, kind: MediaKind, filename: str
) -> ReportRow:
    """CSV hisobotiga yoziladigan xabar ma'lumotlarini yig'adi."""
    return {
        "tartib": order,
        "xabar_id": message.id,
        "sana_UTC": message.date.astimezone(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "turi": kind,
        "file": filename,
        "izoh": (message.message or "").replace("\n", " ").strip(),
    }


async def download_file(
    message: Message,
    filename: str,
    semaphore: asyncio.Semaphore,
    stats: DownloadStats,
    report_row: ReportRow,
) -> None:
    """Bitta faylni parallel yuklashni cheklagan holda yuklab oladi."""
    async with semaphore:
        final_path = os.path.join(SAVE_DIR, filename)
        temporary_path = f"{final_path}.part"

        if os.path.exists(final_path):
            stats.skipped += 1
            return

        for attempt in range(1, MAX_DOWNLOAD_ATTEMPTS + 1):
            try:
                await client.download_media(message, file=temporary_path)
                os.replace(temporary_path, final_path)

                sent_timestamp = message.date.timestamp()
                os.utime(final_path, (sent_timestamp, sent_timestamp))

                stats.downloaded += 1
                print(f"[OK] {filename}")
                return
            except FloodWaitError as error:
                print(
                    f"[KUTISH] Telegram {error.seconds} soniya kutishni so'radi..."
                )
                await asyncio.sleep(error.seconds + 1)
            except Exception as error:
                print(
                    f"[XATO] ID {message.id}, "
                    f"urinish {attempt}/{MAX_DOWNLOAD_ATTEMPTS}: {error}"
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)

        report_row["file"] = "YUKLANMADI"
        stats.failed_message_ids.append(message.id)


async def process_channel_messages(
    semaphore: asyncio.Semaphore,
    stats: DownloadStats,
) -> tuple[list[ReportRow], int]:
    """Kanalni eng eski xabardan boshlab ko'rib chiqib, mos fayllarni yuklaydi."""
    await client.get_dialogs()
    channel = await client.get_entity(CHANNEL)

    print(f"Kanal: {getattr(channel, 'title', CHANNEL)}")
    print("Birinchi xabardan boshlab skanerlanmoqda...\n")

    report_rows: list[ReportRow] = []
    used_names: set[str] = set()
    pending_tasks: list[asyncio.Task[None]] = []
    file_order = 0

    async for message in client.iter_messages(channel, reverse=True):
        kind = classify_message(message)
        if kind is None:
            continue

        file_order += 1
        filename = build_filename(message, kind, used_names)
        report_row = make_report_row(message, file_order, kind, filename)
        report_rows.append(report_row)

        pending_tasks.append(
            asyncio.create_task(
                download_file(message, filename, semaphore, stats, report_row)
            )
        )

        if len(pending_tasks) >= TASKS_PER_BATCH:
            await asyncio.gather(*pending_tasks)
            pending_tasks.clear()

    if pending_tasks:
        await asyncio.gather(*pending_tasks)

    return report_rows, file_order


def write_csv_report(report_rows: list[ReportRow]) -> str:
    """Tartiblangan xabarlar ro'yxatini Excel ochishi mumkin bo'lgan CSV'ga yozadi."""
    report_path = os.path.join(SAVE_DIR, "_royxat.csv")
    columns = ["tartib", "xabar_id", "sana_UTC", "turi", "file", "izoh"]

    with open(report_path, "w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(report_rows)

    return report_path


def print_summary(file_count: int, stats: DownloadStats, report_path: str) -> None:
    """Yuklab olish yakunini terminalda ko'rsatadi."""
    print("\n=============== YAKUN ===============")
    print(f"Topilgan fayllar:     {file_count}")
    print(f"Yangi yuklandi:       {stats.downloaded}")
    print(f"Avval yuklangan:      {stats.skipped}")
    print(f"Xato:                 {len(stats.failed_message_ids)}")

    if stats.failed_message_ids:
        print("Xato bergan xabar ID lari:", stats.failed_message_ids)
        print("Skriptni qayta ishga tushiring, yuklanmaganlari qayta uriniladi.")

    print(f"Tartib jadvali:       {report_path}")


async def main() -> None:
    """Dastur ishini sozlaydi va yuklab olish jarayonini boshqaradi."""
    os.makedirs(SAVE_DIR, exist_ok=True)

    semaphore = asyncio.Semaphore(PARALLEL_DOWNLOADS)
    stats = DownloadStats()

    async with client:
        report_rows, file_count = await process_channel_messages(semaphore, stats)

    report_path = write_csv_report(report_rows)
    print_summary(file_count, stats, report_path)


if __name__ == "__main__":
    asyncio.run(main())
