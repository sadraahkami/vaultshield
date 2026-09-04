let activeTab = 'wipe';
let currentLanguage = 'fa';
let selectedWipeFile = null;
let selectedCarrierFile = null;
let selectedStegoFile = null;

const I18N_DICT = {
  fa: {
    app_subtitle: "استودیوی امنیت، پاک‌سازی عمیق متادیتا، پنهان‌نگاری با AES-256 و امحای فایل",
    lang_btn: "English",
    tab_wipe: "🛡️ پاک‌سازی متادیتا",
    tab_hide: "🔐 مخفی‌سازی در تصویر",
    tab_extract: "🔓 استخراج از تصویر",
    wipe_drop_title: "تصاویر یا اسناد PDF را اینجا رها کنید",
    wipe_drop_desc: "حذف EXIF، موقعیت مکانی GPS، سریال دوربین و مشخصات هویتی",
    btn_select_file: "انتخاب فایل...",
    btn_start_wipe: "پاک‌سازی کامل متادیتا و دانلود فایل امن",
    carrier_img_label: "تصویر حامل (Cover Image - PNG/BMP):",
    carrier_drop_hint: "انتخاب تصویر پوششی PNG...",
    btn_select_carrier: "انتخاب تصویر پوششی",
    secret_data_label: "پیام محرمانه برای مخفی‌سازی:",
    secret_text_placeholder: "متن یا اطلاعات محرمانه را اینجا وارد کنید...",
    passphrase_label: "رمز عبور رمزنگاری (AES-256-GCM):",
    passphrase_placeholder: "یک پسورد قوی وارد کنید...",
    btn_hide_payload: "رمزنگاری و تزریق نامرئی به تصویر",
    stego_img_label: "تصویر حاوی داده پنهان (Stego Image):",
    stego_drop_hint: "انتخاب تصویر Stego PNG...",
    btn_select_stego: "انتخاب تصویر حامل داده",
    extract_pass_label: "رمز عبور جهت رمزگشایی:",
    extract_pass_placeholder: "رمز عبور را وارد کنید...",
    btn_extract_payload: "استخراج و رمزگشایی داده محرمانه",
    result_header: "گزارش و خروجی عملیات امنیتی",
    btn_copy: "کپی متن",
    result_placeholder: "نتایج استخراج یا لاگ پاک‌سازی متادیتا در اینجا نمایش داده می‌شود...",
    status_wiping: "در حال بازتولید بایت‌ها و پاک‌سازی کامل متادیتا...",
    status_hiding: "در حال رمزنگاری با AES-256-GCM و تزریق پنهان به تصویر...",
    status_extracting: "در حال استخراج بیت‌های LSB و رمزگشایی داده...",
    msg_copied: "متن در کلیپ‌بورد کپی شد!",
    msg_enter_pass: "لطفاً رمز عبور را وارد کنید.",
    msg_enter_secret: "لطفاً متن محرمانه را وارد کنید."
  },
  en: {
    app_subtitle: "Deep Metadata Wiper, AES-256 Steganography Vault & DoD File Shredder",
    lang_btn: "فارسی",
    tab_wipe: "🛡️ Metadata Wiper",
    tab_hide: "🔐 Hide in Image (AES-256)",
    tab_extract: "🔓 Extract from Image",
    wipe_drop_title: "Drag & drop images or PDF files here",
    wipe_drop_desc: "Purges EXIF, GPS location, camera serials, and document author info",
    btn_select_file: "Select File...",
    btn_start_wipe: "Scrub All Metadata & Download Clean File",
    carrier_img_label: "Cover Image (PNG / BMP):",
    carrier_drop_hint: "Choose cover PNG image...",
    btn_select_carrier: "Select Cover Image",
    secret_data_label: "Secret Payload to Hide:",
    secret_text_placeholder: "Type confidential notes or secret data to embed...",
    passphrase_label: "Encryption Passphrase (AES-256-GCM):",
    passphrase_placeholder: "Enter a strong secret password...",
    btn_hide_payload: "Encrypt & Embed Invisibly into Image",
    stego_img_label: "Stego Image with Hidden Data:",
    stego_drop_hint: "Choose Stego PNG image...",
    btn_select_stego: "Select Stego Image",
    extract_pass_label: "Decryption Passphrase:",
    extract_pass_placeholder: "Enter passphrase...",
    btn_extract_payload: "Extract & Decrypt Payload",
    result_header: "Security Operations & Output Report",
    btn_copy: "Copy Content",
    result_placeholder: "Decrypted payload or scrub logs will appear here...",
    status_wiping: "Reconstructing canvas and stripping all metadata...",
    status_hiding: "Encrypting with AES-256-GCM and embedding into LSB...",
    status_extracting: "Extracting LSB bitstream and decrypting payload...",
    msg_copied: "Content copied to clipboard!",
    msg_enter_pass: "Please enter a passphrase.",
    msg_enter_secret: "Please enter secret text to hide."
  }
};

const fileInputWipe = document.getElementById('fileInputWipe');
const dropzoneWipe = document.getElementById('dropzoneWipe');
const wipeFileInfo = document.getElementById('wipeFileInfo');
const wipeFileName = document.getElementById('wipeFileName');
const removeWipeFileBtn = document.getElementById('removeWipeFileBtn');
const btnRunWipe = document.getElementById('btnRunWipe');

const fileInputCarrier = document.getElementById('fileInputCarrier');
const carrierFileName = document.getElementById('carrierFileName');
const secretTextInput = document.getElementById('secretTextInput');
const hidePassInput = document.getElementById('hidePassInput');
const btnRunHide = document.getElementById('btnRunHide');

const fileInputStego = document.getElementById('fileInputStego');
const stegoFileName = document.getElementById('stegoFileName');
const extractPassInput = document.getElementById('extractPassInput');
const btnRunExtract = document.getElementById('btnRunExtract');

const resultViewer = document.getElementById('resultViewer');
const copyResultBtn = document.getElementById('copyResultBtn');
const statusAlert = document.getElementById('statusAlert');
const statusMsg = document.getElementById('statusMsg');
const langToggleBtn = document.getElementById('langToggleBtn');

function applyTranslations(lang) {
  const t = I18N_DICT[lang];
  if (!t) return;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (t[key]) el.textContent = t[key];
  });

  document.getElementById('tabBtnWipe').textContent = t.tab_wipe;
  document.getElementById('tabBtnHide').textContent = t.tab_hide;
  document.getElementById('tabBtnExtract').textContent = t.tab_extract;

  secretTextInput.placeholder = t.secret_text_placeholder;
  hidePassInput.placeholder = t.passphrase_placeholder;
  extractPassInput.placeholder = t.extract_pass_placeholder;
  resultViewer.placeholder = t.result_placeholder;
  langToggleBtn.textContent = t.lang_btn;
}

// Tab Switching
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    activeTab = btn.getAttribute('data-tab');
    document.getElementById(`tab-${activeTab}`).classList.add('active');
  });
});

// Wipe File Selection
fileInputWipe.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    selectedWipeFile = e.target.files[0];
    wipeFileName.textContent = selectedWipeFile.name;
    wipeFileInfo.classList.remove('hidden');
    btnRunWipe.disabled = false;
  }
});

removeWipeFileBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  selectedWipeFile = null;
  fileInputWipe.value = '';
  wipeFileInfo.classList.add('hidden');
  btnRunWipe.disabled = true;
});

// Carrier Selection
fileInputCarrier.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    selectedCarrierFile = e.target.files[0];
    carrierFileName.textContent = selectedCarrierFile.name;
    btnRunHide.disabled = false;
  }
});

// Stego Selection
fileInputStego.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    selectedStegoFile = e.target.files[0];
    stegoFileName.textContent = selectedStegoFile.name;
    btnRunExtract.disabled = false;
  }
});

// API Wipe
btnRunWipe.addEventListener('click', async () => {
  if (!selectedWipeFile) return;

  const t = I18N_DICT[currentLanguage];
  showLoading(t.status_wiping);

  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      const payload = { fileName: selectedWipeFile.name, fileData: b64 };
      const res = await fetch('/api/wipe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Scrubbing failed');
      }

      const blob = await res.blob();
      const disposition = res.headers.get('Content-Disposition');
      let filename = 'cleaned_file' + selectedWipeFile.name;
      if (disposition && disposition.indexOf('filename=') !== -1) {
        filename = disposition.split('filename=')[1].replace(/"/g, '').trim();
      }

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      resultViewer.value = `[+] Metadata scrubbed successfully!\nDownloaded: ${filename} (${blob.size} bytes)\nAll GPS coordinates, EXIF tags, and author profiles were permanently purged.`;
      hideLoading();
    };
    reader.readAsDataURL(selectedWipeFile);
  } catch (err) {
    showError(err.message);
  }
});

// API Hide
btnRunHide.addEventListener('click', async () => {
  const t = I18N_DICT[currentLanguage];
  if (!selectedCarrierFile) return;
  const secret = secretTextInput.value.trim();
  const pass = hidePassInput.value.trim();

  if (!secret) return alert(t.msg_enter_secret);
  if (!pass) return alert(t.msg_enter_pass);

  showLoading(t.status_hiding);

  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      const payload = {
        carrierData: b64,
        secretText: secret,
        passphrase: pass
      };
      const res = await fetch('/api/hide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'Steganography embedding failed');
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'stego_vault.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      resultViewer.value = `[+] Secret encrypted with AES-256-GCM and embedded into stego_vault.png!\nImage looks completely identical to original cover image to the human eye.`;
      hideLoading();
    };
    reader.readAsDataURL(selectedCarrierFile);
  } catch (err) {
    showError(err.message);
  }
});

// API Extract
btnRunExtract.addEventListener('click', async () => {
  const t = I18N_DICT[currentLanguage];
  if (!selectedStegoFile) return;
  const pass = extractPassInput.value.trim();
  if (!pass) return alert(t.msg_enter_pass);

  showLoading(t.status_extracting);

  try {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const b64 = e.target.result;
      const payload = { stegoData: b64, passphrase: pass };
      const res = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || 'Extraction failed');

      resultViewer.value = data.text;
      copyResultBtn.disabled = false;
      hideLoading();
    };
    reader.readAsDataURL(selectedStegoFile);
  } catch (err) {
    showError(err.message);
  }
});

copyResultBtn.addEventListener('click', () => {
  const t = I18N_DICT[currentLanguage];
  if (resultViewer.value) {
    navigator.clipboard.writeText(resultViewer.value);
    alert(t.msg_copied);
  }
});

function showLoading(msg) {
  statusMsg.textContent = msg;
  statusAlert.classList.remove('hidden');
}

function hideLoading() {
  statusAlert.classList.add('hidden');
}

function showError(msg) {
  statusMsg.textContent = 'Error: ' + msg;
  statusAlert.classList.remove('hidden');
}

langToggleBtn.addEventListener('click', () => {
  currentLanguage = currentLanguage === 'fa' ? 'en' : 'fa';
  document.documentElement.dir = currentLanguage === 'fa' ? 'rtl' : 'ltr';
  document.documentElement.lang = currentLanguage;
  applyTranslations(currentLanguage);
});

// Initialize translations
applyTranslations(currentLanguage);
