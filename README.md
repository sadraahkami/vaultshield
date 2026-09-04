# 🛡️ VaultShield | Deep Metadata Wiper, AES Steganography & Shredder
### استودیوی امنیت، پاک‌سازی عمیق متادیتا، پنهان‌نگاری با AES-256 و امحای امن فایل‌ها

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![GUI: PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg)](https://pypi.org/project/PyQt6/)
[![Encryption: AES-256-GCM](https://img.shields.io/badge/Cipher-AES--256--GCM-critical.svg)](src/core/steganography.py)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](.github/workflows/build-release.yml)

An all-in-one, 100% offline privacy and cybersecurity suite. Features zero-trace EXIF and PDF metadata scrubbing via raw canvas reconstruction, military-grade **AES-256-GCM authenticated steganography** embedded into image LSB bitstreams, and physical multi-pass file destruction compliant with **DoD 5220.22-M**. Includes a cyber-styled PyQt6 desktop GUI, web SPA, and CLI runner.

یک استودیوی جامع و ۱۰۰٪ آفلاین برای حفاظت از امنیت اطلاعات و حریم خصوصی: پاک‌سازی ریشه‌ای متادیتا و مشخصات مکانی GPS از تصاویر و اسناد، پنهان‌نگاری پیشرفته فایل‌ها درون عکس با رمزنگاری نظامی **AES-256-GCM**، و امحای قطعی و غیرقابل بازیابی فایل‌ها طبق استاندارد **DoD 5220.22-M**.

---

## 🌟 Highlights / قابلیت‌های شاخص

| Feature / قابلیت | Description / توضیحات |
| :--- | :--- |
| 🛡️ **Zero-Trace Metadata Wiper** | Purges GPS coordinates, camera serials, device models, software tags, and PDF author/creator profiles using clean raw canvas reconstruction. |
| 🔐 **AES-256-GCM Steganography** | Encrypts files or text with PBKDF2-HMAC-SHA256 (100k rounds) + AES-GCM and invisibly injects into image LSB pixels. Tamper-evident & zero visual degradation. |
| 💥 **DoD 5220.22-M File Shredder** | Physically overwrites disk sectors (zeros, ones, random cryptographically secure bytes), scrambles metadata, and unlinks file to make recovery impossible. |
| 🖥️ **PyQt6 Desktop & Web SPA** | Cyber-themed modern desktop application + standalone web interface with dynamic bilingual support (Persian RTL / English LTR). |
| 🐳 **Docker Microservice** | Deploy self-hosted privacy studio with a single `docker-compose up -d`. |

---

## 🌐 Navigation / فهرست

- [English Guide](#-english-guide)
  - [Quick Start](#-quick-start)
  - [CLI Examples](#-cli-examples)
- [راهنمای فارسی](#-راهنمای-فارسی)
  - [شروع سریع](#-شروع-سریع)
  - [واسط خط فرمان (CLI)](#-واسط-خط-فرمان-cli)
- [Docker Deployment](#-docker-deployment)
- [License](#-license)

---

## 🇬🇧 English Guide

### 🚀 Quick Start

#### 1. Desktop Application (PyQt6)
Double-click `run_gui.bat` or run:
```bash
python main.py
```

#### 2. Web Studio (Single Page App)
Double-click `run_web.bat` or run:
```bash
python main.py --web
```
Open `http://localhost:8080` in your browser.

#### 3. Command-Line Interface (CLI)
```bash
# Scrub metadata from a photo or document:
python main.py wipe vacation.jpg -o safe_photo.jpg

# Encrypt and hide a secret message inside an image:
python main.py hide cover.png -p "MySecretPass#2026" -m "Confidential meeting at 22:00" -o stego.png

# Extract and decrypt secret from stego image:
python main.py extract stego.png -p "MySecretPass#2026"

# Permanently shred a sensitive file (3-pass DoD 5220.22-M):
python main.py shred private_data.docx --passes 3
```

---

## 🇮🇷 راهنمای فارسی

### 🚀 شروع سریع

#### ۱. اجرای نرم‌افزار دسکتاپ (PyQt6)
با دو بار کلیک روی `run_gui.bat` یا دستور:
```bash
python main.py
```

#### ۲. اجرای استودیوی تحت وب (Web Studio)
با دو بار کلیک روی `run_web.bat` یا دستور:
```bash
python main.py --web
```
سپس آدرس `http://localhost:8080` را در مرورگر باز کنید.

#### ۳. واسط خط فرمان (CLI)
```bash
# پاک‌سازی متادیتا و موقعیت GPS عکس:
python main.py wipe photo.jpg

# رمزنگاری و مخفی‌سازی پیام محرمانه در عکس:
python main.py hide cover.png -p "Password123" -m "پیام فوق محرمانه" -o secret.png

# امحای امن و غیرقابل ریکاوری فایل:
python main.py shred financial.xlsx --passes 3 -y
```

---

## 🐳 Docker Deployment

```bash
docker-compose up -d
```
Your local VaultShield privacy studio will be running at `http://localhost:8080`.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
