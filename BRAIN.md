# VaultShield | Deep Metadata Wiper, AES Steganography & Secure Shredder
## Architecture & Blueprint (مغز سیستم و نقشه راه)

### ۱. چشم‌انداز محصول (Product Vision)
**VaultShield** یک استودیوی جامع و ۱۰۰٪ آفلاین برای حفظ حریم خصوصی کاربران است که شامل پاک‌سازی عمیق متادیتا و ردهای دیجیتال از تصاویر، اسناد و ویدیوها، پنهان‌نگاری پیشرفته فایل‌ها درون تصاویر با رمزگذاری **AES-256-GCM**، و امحای ایمن و غیرقابل بازیابی فایل‌ها با استانداردهای نظامی (DoD 5220.22-M) می‌باشد.

### ۲. دردهای بازار (User Pains)
1. افشای ناخواسته موقعیت مکانی (GPS)، مدل دستگاه، زمان ثبت و اطلاعات هویتی همراه با فایل‌های ارسالی.
2. نیاز به انتقال امن فایل‌های محرمانه در کانال‌های عمومی بدون جلب توجه ناظران یا فایروال‌ها.
3. خطرات بازیابی اطلاعات حساس پس از حذف معمولی در ویندوز.

### ۳. پشته فنی (Technology Stack)
- **Metadata Scrubbing:** `Pillow` (Raw pixel reconstruct), `pypdf` (Info dictionary purge), `mutagen` (Media tag stripper).
- **Steganography:** LSB (Least Significant Bit) manipulation on 24-bit RGB with `cryptography` (AES-256-GCM + PBKDF2-HMAC-SHA256).
- **File Shredder:** Multi-pass cryptographic overwriting (Zeros, Ones, Random bytes).
- **Interface:** Desktop GUI (PyQt6), CLI Runner, Standalone `.exe`.

### ۴. ماژول‌های اصلی (Core Modules)
- **Zero-Trace EXIF Stripper:** بازتولید تصویر بدون متادیتا برای حذف تضمینی اطلاعات محرمانه.
- **Steganography Vault:** کپسوله‌سازی فایل‌های فشرده درون عکس‌ها با پسورد، طوری که تصویر اصلی تغییری نکند.
- **Permanent Shredder:** نابودی فیزیکی بایت‌های فایل روی هارد دیسک پیش از حذف اشاره‌گر سیستم‌عامل.
