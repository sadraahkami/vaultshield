"""
Internationalization (i18n) module supporting Persian (RTL) and English (LTR).
"""

from typing import Dict, Optional

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "app_title": {
        "fa": "استودیوی امنیت، پاک‌سازی متادیتا و پنهان‌نگاری | VaultShield",
        "en": "VaultShield - Metadata Wiper, AES Steganography & Shredder"
    },
    "lang_toggle_btn": {
        "fa": "English",
        "en": "فارسی"
    },
    # Tabs
    "tab_wipe": {
        "fa": "🛡️ پاک‌سازی متادیتا (EXIF Wiper)",
        "en": "🛡️ Metadata Wiper"
    },
    "tab_hide": {
        "fa": "🔐 مخفی‌سازی در تصویر (Hide Payload)",
        "en": "🔐 Hide in Image (AES-256)"
    },
    "tab_extract": {
        "fa": "🔓 استخراج از تصویر (Extract)",
        "en": "🔓 Extract from Image"
    },
    "tab_shred": {
        "fa": "💥 امحای امن فایل‌ها (Shredder)",
        "en": "💥 Secure Shredder"
    },
    # Wipe Tab
    "wipe_drop_text": {
        "fa": "تصاویر یا اسناد PDF را اینجا رها کنید",
        "en": "Drag & drop images (JPG, PNG, WebP) or PDF files here"
    },
    "btn_select_wipe_file": {
        "fa": "انتخاب فایل برای پاک‌سازی...",
        "en": "Select File to Scrub..."
    },
    "btn_start_wipe": {
        "fa": "پاک‌سازی کامل متادیتا و ردهای دیجیتال",
        "en": "Scrub All Metadata & EXIF"
    },
    # Hide Tab
    "carrier_img_label": {
        "fa": "تصویر حامل (Cover Image):",
        "en": "Cover Image (PNG / BMP):"
    },
    "secret_data_label": {
        "fa": "پیام یا فایل محرمانه برای مخفی‌سازی:",
        "en": "Secret Payload (Text or File):"
    },
    "secret_text_placeholder": {
        "fa": "متن محرمانه خود را اینجا تایپ کنید یا فایلی را برای کپسوله‌سازی انتخاب کنید...",
        "en": "Type confidential text or choose a file to embed..."
    },
    "passphrase_label": {
        "fa": "رمز عبور رمزنگاری (AES-256-GCM):",
        "en": "Encryption Passphrase (AES-256-GCM):"
    },
    "passphrase_placeholder": {
        "fa": "یک رمز عبور قوی وارد کنید...",
        "en": "Enter a strong secret password..."
    },
    "btn_hide_payload": {
        "fa": "رمزنگاری و تزریق نامرئی به تصویر",
        "en": "Encrypt & Embed into Image"
    },
    # Extract Tab
    "stego_img_label": {
        "fa": "تصویر حاوی داده پنهان (Stego Image):",
        "en": "Stego Image with Hidden Data:"
    },
    "extract_pass_label": {
        "fa": "رمز عبور جهت رمزگشایی:",
        "en": "Decryption Passphrase:"
    },
    "btn_extract_payload": {
        "fa": "استخراج و رمزگشایی داده محرمانه",
        "en": "Extract & Decrypt Payload"
    },
    # Shredder Tab
    "shred_warning": {
        "fa": "⚠️ هشدار: فایل‌های امحاشده توسط این ابزار با استانداردهای نظامی بازنویسی شده و حتی با نرم‌افزارهای ریکاوری تخصصی غیرقابل بازیابی خواهند بود.",
        "en": "⚠️ Warning: Files shredded here are multi-pass overwritten and completely unrecoverable."
    },
    "shred_passes_label": {
        "fa": "تعداد مراحل رونویسی دیسک:",
        "en": "Overwriting Passes:"
    },
    "pass_3": {
        "fa": "۳ مرحله (استاندارد نظامی DoD 5220.22-M - پیشنهادی)",
        "en": "3 Passes (DoD 5220.22-M Standard - Recommended)"
    },
    "pass_1": {
        "fa": "۱ مرحله (سریع - با بایت‌های تصادفی)",
        "en": "1 Pass (Fast - Random Bytes)"
    },
    "pass_7": {
        "fa": "۷ مرحله (حداکثر امنیت - DoD 5220.22-M ECE)",
        "en": "7 Passes (Ultra Secure - DoD ECE)"
    },
    "btn_shred": {
        "fa": "امحای قطعی و نابودی فایل",
        "en": "Permanently Shred File"
    },
    # Common
    "status_ready": {
        "fa": "آماده به کار",
        "en": "Ready"
    },
    "status_processing": {
        "fa": "در حال پردازش امنیتی...",
        "en": "Processing security task..."
    },
    "status_success": {
        "fa": "عملیات با موفقیت انجام شد!",
        "en": "Operation completed successfully!"
    },
    "error_title": {
        "fa": "خطا",
        "en": "Error"
    },
    "msg_copied": {
        "fa": "محتوا با موفقیت در کلیپ‌بورد کپی شد!",
        "en": "Copied to clipboard successfully!"
    }
}

_current_language: str = "fa"


def get_current_language() -> str:
    return _current_language


def set_current_language(lang: str) -> None:
    global _current_language
    if lang in ("fa", "en"):
        _current_language = lang


def tr(key: str, lang: Optional[str] = None, **kwargs) -> str:
    active_lang = lang or _current_language
    item = TRANSLATIONS.get(key, {})
    val = item.get(active_lang, item.get("en", key))
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val
