# Telegram PDF va audio yuklab oluvchi

Ushbu Python skripti Telegram kanalidagi xabarlarni eng eskisidan boshlab ko'rib chiqadi va sozlamalarga qarab PDF, audio hamda ovozli xabarlarni kompyuterga yuklab oladi.

> **Muhim:** skriptni faqat o'zingizga tegishli yoki yuklab olishga ruxsatingiz bo'lgan kanallarda ishlating. Yuklangan materiallarni tarqatishdan oldin mualliflik huquqi va kanal qoidalarini tekshiring.

## Nimalar qiladi?

- Kanal xabarlarini birinchi xabardan boshlab ko'rib chiqadi.
- PDF, audio, ovozli xabarlarni yuklaydi; xohishga ko'ra boshqa hujjat turlarini ham yoqish mumkin.
- Fayllarni kanal yuborgan asl nom bilan saqlashga harakat qiladi. Bir xil nom takrorlansa, nomiga `(2)`, `(3)` kabi qo'shimcha qo'shadi.
- Yuklangan faylning o'zgartirilgan sanasini kanalga yuborilgan vaqtga moslaydi.
- Natijalarni `SAVE_DIR` bilan belgilangan papkaga yozadi va shu papkada Excel'da ochish mumkin bo'lgan `_royxat.csv` jadvalini yaratadi.
- Skriptni qayta ishga tushirganda mavjud fayllarni o'tkazib yuboradi; muvaffaqiyatsiz yuklamalarni qayta urinib ko'rish mumkin.

## Talablar

- Python 3.10 yoki undan yangi versiya
- Telegram akkaunti
- Telegram API uchun `API_ID` va `API_HASH`
- Yuklab olish uchun yetarli disk joyi

## O'rnatish va sozlash

### 1. Python va Git'ni tekshirish

Windows'da PowerShell yoki Terminal ochib quyidagilarni bajaring:

```powershell
python --version
git --version
```

`python` buyrug'i topilmasa, Python'ni [python.org](https://www.python.org/downloads/) saytidan o'rnating va o'rnatish vaqtida **Add Python to PATH** bandini belgilang. Git topilmasa, [git-scm.com](https://git-scm.com/downloads) saytidan o'rnating.

### 2. Loyihani yuklab olish

GitHub'dagi repo manzilingizni quyidagi misoldagi manzil o'rniga yozing:

```powershell
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

Repo hali GitHub'da bo'lmasa, `pdf_audio_download.py` faylini kompyuteringizdagi loyiha papkasida qoldirib, keyingi sozlash bosqichiga o'ting.

### 3. Virtual muhit va kutubxonani o'rnatish (tavsiya etiladi)

Loyiha papkasida:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

PowerShell virtual muhit skriptini ishga tushirishga ruxsat bermasa, shu oynada quyidagini bir marta bajaring va aktivatsiyani qaytaring:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Virtual muhitdan foydalanmasangiz, kutubxonani `python -m pip install -r requirements.txt` buyrug'i bilan o'rnatishingiz mumkin.

### 4. Telegram API ma'lumotlarini olish

1. [my.telegram.org](https://my.telegram.org) sahifasiga Telegram telefon raqamingiz bilan kiring.
2. **API development tools** bo'limida ilova yarating.
3. Ko'rsatilgan `api_id` va `api_hash` qiymatlarini oling.
4. `pdf_audio_download.py` faylini matn muharririda ochib, sozlamalarni to'ldiring:

```python
API_ID = 1234                       # O'zingizning api_id raqamingiz
API_HASH = "api_hash"               # O'zingizning api_hash qiymatingiz
CHANNEL = -1003768657126            # Kanal ID raqami yoki @username
SAVE_DIR = "cefr"                   # Natijalar saqlanadigan papka
PARALLEL_DOWNLOADS = 3              # Bir vaqtda yuklanadigan fayllar soni
```

`API_ID` namunadagi `1234` bilan qolmasin: haqiqiy raqamni kiriting. `API_HASH` uchun haqiqiy qiymatingizni qo'shtirnoq ichiga yozing. `CHANNEL` o'rniga kanalning raqamli ID'sini yoki ochiq kanalning `@username` qiymatini kiriting. Shaxsiy kanal uchun hisobingiz o'sha kanalga a'zo bo'lishi kerak. `SAVE_DIR` qiymatini xohlagan papka nomiga o'zgartiring.

> **Xavfsizlik:** `API_HASH` va `session_channel.session` fayli shaxsiy ma'lumot hisoblanadi. Ularni GitHub'ga, chatga yoki boshqalarga yubormang. Repo'ni ommaga chiqarishdan avval `API_ID` va `API_HASH` kodda faqat namunaviy qiymatlar ekanini tekshiring. Agar haqiqiy kalit GitHub'ga chiqib ketgan bo'lsa, uni my.telegram.org'da bekor qiling/almashtiring.

### 5. Yuklab olishni boshlash

Loyiha papkasida virtual muhit faolligini tekshirib, ishga tushiring:

```powershell
python pdf_audio_download.py
```

Birinchi ishga tushirishda Telegram telefon raqamingiz, Telegram'dan kelgan tasdiqlash kodi va akkauntingizda ikki bosqichli parol yoqilgan bo'lsa, shu parol so'raladi. Muvaffaqiyatli kirishdan keyin `session_channel.session` fayli yaratiladi; keyingi ishga tushirishlarda kodni qayta kiritish talab qilinmasligi mumkin. Bu faylni himoyalang va hech qachon repozitoriyga qo'shmang.

## Yuklab olish sozlamalari

`pdf_audio_download.py` faylining yuqori qismidagi sozlamalarni o'zgartiring:

| Sozlama | Vazifasi |
|---|---|
| `DOWNLOAD_PDF` | PDF fayllarni yuklash |
| `DOWNLOAD_AUDIO` | Audio/musiqa fayllarni yuklash |
| `DOWNLOAD_VOICE` | Ovozli xabarlarni yuklash |
| `DOWNLOAD_OTHER_DOCS` | DOCX, ZIP va boshqa hujjatlarni ham yuklash |
| `PARALLEL_DOWNLOADS` | Bir vaqtda yuklanadigan fayllar soni; odatda 2–4 tavsiya qilinadi |
| `SAVE_DIR` | Yuklamalar va `_royxat.csv` saqlanadigan papka |

Yoqish uchun `True`, o'chirish uchun `False` qiymatini yozing.

## Natijalar

Odatiy holatda fayllar `cefr` papkasiga tushadi:

- Yuklangan PDF, audio va ovozli xabar fayllari
- `_royxat.csv` — tartib raqami, Telegram xabar ID'si, UTC sana, fayl turi, fayl nomi va izoh

`_royxat.csv` faylini Excel'da ochish mumkin. Yuklab olish tugagach, terminalda topilgan, yangi yuklangan, o'tkazib yuborilgan va xatolik bergan fayllar soni ko'rsatiladi.

## Muammolarni bartaraf etish

- **`API_ID` yoki `API_HASH` xatosi:** my.telegram.org'dagi qiymatlarni tekshiring; `API_ID` son, `API_HASH` qo'shtirnoq ichidagi matn bo'lishi kerak.
- **Kanal topilmadi yoki kirish taqiqlangan:** kanal manzilini tekshiring va Telegram akkauntingiz kanalga a'zo ekanini tasdiqlang. Xususiy kanalga raqamli ID kerak bo'lishi mumkin.
- **`telethon` topilmadi:** loyiha virtual muhiti faolligini tekshirib, `pip install -r requirements.txt` buyrug'ini bajaring.
- **Telegram tasdiqlash kodi/paroli so'raldi:** kodni faqat o'zingizning skriptni ishga tushirgan terminalingizga kiriting; hech kimga yubormang.
- **Telegram kutishni so'radi (`FloodWait`):** skript ko'rsatilgan muddat kutadi. Bir vaqtdagi yuklamalar ko'p bo'lsa, `PARALLEL_DOWNLOADS` qiymatini kamaytiring.
- **Ayrim fayllar yuklanmadi:** terminaldagi xabar ID'larini tekshiring va skriptni yana ishga tushiring. Qisman yuklangan `.part` fayl qolgan bo'lsa, uni tekshirib, kerak bo'lsa qo'lda o'chiring.

## GitHub'ga joylash tartibi

### GitHub sayti orqali repo yaratish

1. [github.com](https://github.com) saytiga kiring yoki akkaunt yarating.
2. Yuqoridagi **+** tugmasidan **New repository** ni tanlang.
3. Repo nomini kiriting, masalan `telegram-pdf-audio-download`.
4. Ochiq repo uchun **Public**, faqat o'zingiz/hamkorlaringiz ko'rishi uchun **Private** ni tanlang.
5. **Add a README file** bandini belgilanmagan holda qoldiring, chunki loyiha papkasida README bor.
6. **Create repository** tugmasini bosing.

### Windows terminali orqali fayllarni yuborish

PowerShell'da loyiha papkasiga o'ting. Masalan:

```powershell
cd "C:\Users\User\Desktop\otchyot\telegram_pdf_audi_dowload"
```

Repo'ni boshlang'ich sozlab, kerakli fayllarni qo'shing. `git status` natijasini tekshirib, keyin commit va push qiling:

```powershell
git init
git add README.md .gitignore requirements.txt pdf_audio_download.py
git status
git commit -m "Add Telegram PDF and audio downloader"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

`USERNAME` va `REPOSITORY` o'rniga GitHub foydalanuvchi nomingiz va yuqorida yaratgan repo nomini yozing. `git status` natijasini diqqat bilan tekshirib, `session_channel.session`, yuklangan materiallar papkasi yoki API maxfiy qiymatlari commit/push qilinmasligiga ishonch hosil qiling. GitHub'ga kirish uchun brauzer oynasi ochilishi mumkin. GitHub parolingizni terminalga kiritmang; so'ralsa, GitHub'ning rasmiy autentifikatsiya usulidan foydalaning.

Agar GitHub repo'ni README bilan oldindan yaratgan bo'lsangiz, avval repo'ni clone qilib, loyiha fayllarini clone qilingan papkaga ko'chiring yoki remote'dagi mavjud o'zgarishlarni xavfsiz birlashtiring. `origin` remote avvaldan mavjud bo'lsa, `git remote add` ni qayta bajarmasdan `git remote -v` bilan tekshiring.

Keyingi yangilanishlarni yuborish uchun:

```powershell
git add README.md .gitignore requirements.txt pdf_audio_download.py
git status
git commit -m "Describe your change"
git push
```

## Litsenziya

Agar boshqalar koddan qanday foydalanishi, uni o'zgartirishi va tarqatishi mumkinligini belgilamoqchi bo'lsangiz, repo yaratishda yoki keyin mos `LICENSE` faylini qo'shing. Litsenziyasiz boshqa foydalanuvchilarning huquqlari aniq belgilanmagan bo'ladi.
#   p d f _ a u d i o _ d o w n l o a d _ f r o m _ t e l e g r a m  
 