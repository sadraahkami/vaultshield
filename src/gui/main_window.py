"""
Main Desktop Application Window for VaultShield using PyQt6.
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QLineEdit, QTabWidget, QTextEdit, QComboBox,
    QProgressBar, QStackedWidget
)

from ..core.i18n import tr, set_current_language, get_current_language
from ..core.metadata_wiper import MetadataWiper, WipeReport
from ..core.steganography import SteganographyVault, StegoPayload
from ..core.shredder import FileShredder, ShredReport
from .icons import IconProvider
from .styles import DARK_THEME
from .widgets import FileDropZone, FileSelectedCard


class SecurityWorker(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str, object)

    def __init__(self, mode: str, kwargs: dict):
        super().__init__()
        self.mode = mode
        self.kwargs = kwargs

    def run(self):
        try:
            if self.mode == "wipe":
                src = self.kwargs["input_path"]
                dst = self.kwargs.get("output_path")
                self.progress.emit(20, "Reconstructing canvas & purging metadata...")
                report = MetadataWiper.wipe_metadata(src, dst)
                self.finished.emit(True, f"Scrubbed {len(report.removed_items)} metadata headers successfully.", report)

            elif self.mode == "hide":
                carrier = self.kwargs["carrier_path"]
                out = self.kwargs["output_path"]
                passphrase = self.kwargs["passphrase"]
                data = self.kwargs["data"]
                is_file = self.kwargs.get("is_file", False)
                filename = self.kwargs.get("filename", "")

                self.progress.emit(30, "Encrypting with AES-256-GCM & embedding LSB...")
                success = SteganographyVault.hide_payload(
                    carrier_image_path=carrier,
                    output_image_path=out,
                    passphrase=passphrase,
                    secret_data=data,
                    is_file=is_file,
                    filename=filename
                )
                self.finished.emit(success, f"Payload hidden in {Path(out).name}", out)

            elif self.mode == "extract":
                stego = self.kwargs["stego_path"]
                passphrase = self.kwargs["passphrase"]
                self.progress.emit(40, "Extracting LSB & decrypting AES-256...")
                payload = SteganographyVault.extract_payload(stego, passphrase)
                self.finished.emit(True, "Payload decrypted successfully.", payload)

            elif self.mode == "shred":
                file_to_shred = self.kwargs["filepath"]
                passes = self.kwargs.get("passes", 3)

                def on_shred_prog(pct, msg):
                    self.progress.emit(pct, msg)

                report = FileShredder.shred_file(file_to_shred, passes=passes, progress_callback=on_shred_prog)
                self.finished.emit(report.success, f"Permanently shredded in {report.duration_seconds}s.", report)

        except Exception as e:
            self.finished.emit(False, str(e), None)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.thread: Optional[QThread] = None
        self.worker: Optional[SecurityWorker] = None

        # State paths
        self.wipe_file: Optional[str] = None
        self.hide_carrier: Optional[str] = None
        self.extract_file: Optional[str] = None
        self.shred_file: Optional[str] = None
        self.extracted_payload: Optional[StegoPayload] = None

        self._init_window()
        self._build_ui()
        self._retranslate_ui()

    def _init_window(self):
        self.resize(1020, 720)
        self.setMinimumSize(840, 580)
        self.setStyleSheet(DARK_THEME)

    def _build_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        # Top Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.lbl_brand = QLabel("🛡️ VaultShield")
        self.lbl_brand.setStyleSheet("font-size: 16px; font-weight: 800; color: #38BDF8;")

        self.btn_lang = QPushButton()
        self.btn_lang.setObjectName("langBtn")
        self.btn_lang.clicked.connect(self._toggle_language)

        top_bar.addWidget(self.lbl_brand)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_lang)
        main_layout.addLayout(top_bar)

        # Tab Widget
        self.tabs = QTabWidget()

        # TAB 1: Metadata Wiper
        tab_wipe = QWidget()
        lay_wipe = QVBoxLayout(tab_wipe)
        lay_wipe.setSpacing(12)

        self.wipe_drop = FileDropZone("Drag & drop images (JPG, PNG, WebP) or PDF files here")
        self.wipe_drop.file_dropped.connect(self._on_wipe_dropped)
        lay_wipe.addWidget(self.wipe_drop)

        self.wipe_card_container = QStackedWidget()
        self.wipe_card_empty = QWidget()
        self.wipe_card_container.addWidget(self.wipe_card_empty)
        lay_wipe.addWidget(self.wipe_card_container)

        self.btn_run_wipe = QPushButton()
        self.btn_run_wipe.setEnabled(False)
        self.btn_run_wipe.clicked.connect(self._on_run_wipe)
        lay_wipe.addWidget(self.btn_run_wipe)

        self.txt_wipe_log = QTextEdit()
        self.txt_wipe_log.setReadOnly(True)
        self.txt_wipe_log.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.txt_wipe_log.setPlaceholderText("Scrubbing reports will appear here...")
        lay_wipe.addWidget(self.txt_wipe_log)

        self.tabs.addTab(tab_wipe, IconProvider.get_icon("shield", "#38BDF8", 18), "Wipe")

        # TAB 2: Stego Hide
        tab_hide = QWidget()
        lay_hide = QVBoxLayout(tab_hide)
        lay_hide.setSpacing(12)

        self.lbl_carrier = QLabel()
        self.lbl_carrier.setStyleSheet("font-weight: bold;")
        lay_hide.addWidget(self.lbl_carrier)

        self.hide_carrier_drop = FileDropZone("Drag & drop Cover Image (PNG or BMP)")
        self.hide_carrier_drop.file_dropped.connect(self._on_carrier_dropped)
        lay_hide.addWidget(self.hide_carrier_drop)

        self.carrier_card_container = QStackedWidget()
        self.carrier_card_empty = QWidget()
        self.carrier_card_container.addWidget(self.carrier_card_empty)
        lay_hide.addWidget(self.carrier_card_container)

        self.lbl_secret = QLabel()
        self.lbl_secret.setStyleSheet("font-weight: bold;")
        lay_hide.addWidget(self.lbl_secret)

        self.txt_secret = QTextEdit()
        self.txt_secret.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.txt_secret.setPlaceholderText("Type secret message here or drop confidential payload...")
        lay_hide.addWidget(self.txt_secret)

        row_pass = QHBoxLayout()
        self.lbl_pass = QLabel()
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        row_pass.addWidget(self.lbl_pass)
        row_pass.addWidget(self.txt_pass, stretch=1)
        lay_hide.addLayout(row_pass)

        self.btn_run_hide = QPushButton()
        self.btn_run_hide.clicked.connect(self._on_run_hide)
        lay_hide.addWidget(self.btn_run_hide)

        self.tabs.addTab(tab_hide, IconProvider.get_icon("lock", "#F59E0B", 18), "Hide")

        # TAB 3: Stego Extract
        tab_extract = QWidget()
        lay_extract = QVBoxLayout(tab_extract)
        lay_extract.setSpacing(12)

        self.extract_drop = FileDropZone("Drag & drop Stego Image (PNG with hidden data)")
        self.extract_drop.file_dropped.connect(self._on_extract_dropped)
        lay_extract.addWidget(self.extract_drop)

        self.extract_card_container = QStackedWidget()
        self.extract_card_empty = QWidget()
        self.extract_card_container.addWidget(self.extract_card_empty)
        lay_extract.addWidget(self.extract_card_container)

        row_ext_pass = QHBoxLayout()
        self.lbl_ext_pass = QLabel()
        self.txt_ext_pass = QLineEdit()
        self.txt_ext_pass.setEchoMode(QLineEdit.EchoMode.Password)
        row_ext_pass.addWidget(self.lbl_ext_pass)
        row_ext_pass.addWidget(self.txt_ext_pass, stretch=1)
        lay_extract.addLayout(row_ext_pass)

        self.btn_run_extract = QPushButton()
        self.btn_run_extract.clicked.connect(self._on_run_extract)
        lay_extract.addWidget(self.btn_run_extract)

        self.txt_extract_result = QTextEdit()
        self.txt_extract_result.setReadOnly(True)
        self.txt_extract_result.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        lay_extract.addWidget(self.txt_extract_result)

        self.btn_save_extracted = QPushButton("Save Extracted File...")
        self.btn_save_extracted.setObjectName("secondaryBtn")
        self.btn_save_extracted.setVisible(False)
        self.btn_save_extracted.clicked.connect(self._on_save_extracted_file)
        lay_extract.addWidget(self.btn_save_extracted)

        self.tabs.addTab(tab_extract, IconProvider.get_icon("unlock", "#10B981", 18), "Extract")

        # TAB 4: Shredder
        tab_shred = QWidget()
        lay_shred = QVBoxLayout(tab_shred)
        lay_shred.setSpacing(12)

        self.lbl_shred_warn = QLabel()
        self.lbl_shred_warn.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 13px;")
        self.lbl_shred_warn.setWordWrap(True)
        lay_shred.addWidget(self.lbl_shred_warn)

        self.shred_drop = FileDropZone("Drag & drop file to PERMANENTLY shred and destroy")
        self.shred_drop.file_dropped.connect(self._on_shred_dropped)
        lay_shred.addWidget(self.shred_drop)

        self.shred_card_container = QStackedWidget()
        self.shred_card_empty = QWidget()
        self.shred_card_container.addWidget(self.shred_card_empty)
        lay_shred.addWidget(self.shred_card_container)

        row_passes = QHBoxLayout()
        self.lbl_shred_passes = QLabel()
        self.combo_shred_passes = QComboBox()
        self.combo_shred_passes.addItem("3 Passes (DoD 5220.22-M - Recommended)", 3)
        self.combo_shred_passes.addItem("1 Pass (Fast - Random Bytes)", 1)
        self.combo_shred_passes.addItem("7 Passes (DoD 5220.22-M ECE - Ultra)", 7)
        row_passes.addWidget(self.lbl_shred_passes)
        row_passes.addWidget(self.combo_shred_passes, stretch=1)
        lay_shred.addLayout(row_passes)

        self.btn_run_shred = QPushButton()
        self.btn_run_shred.setObjectName("dangerBtn")
        self.btn_run_shred.setEnabled(False)
        self.btn_run_shred.clicked.connect(self._on_run_shred)
        lay_shred.addWidget(self.btn_run_shred)

        lay_shred.addStretch()
        self.tabs.addTab(tab_shred, IconProvider.get_icon("shred", "#DC2626", 18), "Shred")

        main_layout.addWidget(self.tabs, stretch=1)

        # Bottom Progress & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #38BDF8; font-weight: bold;")
        main_layout.addWidget(self.lbl_status)

    def _retranslate_ui(self):
        is_rtl = get_current_language() == "fa"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if is_rtl else Qt.LayoutDirection.LeftToRight)

        self.setWindowTitle(tr("app_title"))
        self.lbl_brand.setText("🛡️ " + tr("app_title"))
        self.btn_lang.setText(tr("lang_toggle_btn"))

        self.tabs.setTabText(0, tr("tab_wipe"))
        self.tabs.setTabText(1, tr("tab_hide"))
        self.tabs.setTabText(2, tr("tab_extract"))
        self.tabs.setTabText(3, tr("tab_shred"))

        self.btn_run_wipe.setText(tr("btn_start_wipe"))
        self.lbl_carrier.setText(tr("carrier_img_label"))
        self.lbl_secret.setText(tr("secret_data_label"))
        self.lbl_pass.setText(tr("passphrase_label"))
        self.txt_pass.setPlaceholderText(tr("passphrase_placeholder"))
        self.btn_run_hide.setText(tr("btn_hide_payload"))

        self.lbl_ext_pass.setText(tr("extract_pass_label"))
        self.txt_ext_pass.setPlaceholderText(tr("passphrase_placeholder"))
        self.btn_run_extract.setText(tr("btn_extract_payload"))

        self.lbl_shred_warn.setText(tr("shred_warning"))
        self.lbl_shred_passes.setText(tr("shred_passes_label"))
        self.btn_run_shred.setText(tr("btn_shred"))

    def _toggle_language(self):
        new_lang = "en" if get_current_language() == "fa" else "fa"
        set_current_language(new_lang)
        self._retranslate_ui()

    def _on_wipe_dropped(self, filepath: str):
        self.wipe_file = filepath
        card = FileSelectedCard(filepath)
        card.delete_requested.connect(self._clear_wipe)
        self.wipe_card_container.addWidget(card)
        self.wipe_card_container.setCurrentWidget(card)
        self.btn_run_wipe.setEnabled(True)

    def _clear_wipe(self):
        self.wipe_file = None
        self.wipe_card_container.setCurrentWidget(self.wipe_card_empty)
        self.btn_run_wipe.setEnabled(False)

    def _on_carrier_dropped(self, filepath: str):
        self.hide_carrier = filepath
        card = FileSelectedCard(filepath)
        card.delete_requested.connect(self._clear_carrier)
        self.carrier_card_container.addWidget(card)
        self.carrier_card_container.setCurrentWidget(card)

    def _clear_carrier(self):
        self.hide_carrier = None
        self.carrier_card_container.setCurrentWidget(self.carrier_card_empty)

    def _on_extract_dropped(self, filepath: str):
        self.extract_file = filepath
        card = FileSelectedCard(filepath)
        card.delete_requested.connect(self._clear_extract)
        self.extract_card_container.addWidget(card)
        self.extract_card_container.setCurrentWidget(card)

    def _clear_extract(self):
        self.extract_file = None
        self.extract_card_container.setCurrentWidget(self.extract_card_empty)

    def _on_shred_dropped(self, filepath: str):
        self.shred_file = filepath
        card = FileSelectedCard(filepath)
        card.delete_requested.connect(self._clear_shred)
        self.shred_card_container.addWidget(card)
        self.shred_card_container.setCurrentWidget(card)
        self.btn_run_shred.setEnabled(True)

    def _clear_shred(self):
        self.shred_file = None
        self.shred_card_container.setCurrentWidget(self.shred_card_empty)
        self.btn_run_shred.setEnabled(False)

    def _start_worker(self, mode: str, kwargs: dict):
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.lbl_status.setText(tr("status_processing"))

        self.thread = QThread()
        self.worker = SecurityWorker(mode, kwargs)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(self._on_worker_finished)

        self.thread.start()

    def _on_worker_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(msg)

    def _on_worker_finished(self, success: bool, msg: str, result_obj: object):
        if self.thread:
            self.thread.quit()
            self.thread.wait()

        self.progress_bar.setVisible(False)

        if success:
            self.lbl_status.setText(tr("status_success"))
            if isinstance(result_obj, WipeReport):
                self.txt_wipe_log.setPlainText(
                    f"Scrubbed Output: {result_obj.cleaned_file}\n"
                    f"Original Size: {result_obj.original_size} bytes -> Cleaned: {result_obj.cleaned_size} bytes\n"
                    f"Removed Elements:\n - " + "\n - ".join(result_obj.removed_items)
                )
            elif isinstance(result_obj, StegoPayload):
                self.extracted_payload = result_obj
                self.txt_extract_result.setPlainText(result_obj.text)
                self.btn_save_extracted.setVisible(result_obj.is_file)
            elif isinstance(result_obj, ShredReport):
                self._clear_shred()

            QMessageBox.information(self, tr("status_success"), msg)
        else:
            self.lbl_status.setText(tr("error_title"))
            QMessageBox.critical(self, tr("error_title"), f"Error:\n{msg}")

    def _on_run_wipe(self):
        if not self.wipe_file:
            return
        self._start_worker("wipe", {"input_path": self.wipe_file})

    def _on_run_hide(self):
        if not self.hide_carrier:
            QMessageBox.warning(self, tr("error_title"), "Please drop a cover image first.")
            return

        passphrase = self.txt_pass.text().strip()
        if not passphrase:
            QMessageBox.warning(self, tr("error_title"), "Please provide an encryption passphrase.")
            return

        secret_text = self.txt_secret.toPlainText().strip()
        if not secret_text:
            QMessageBox.warning(self, tr("error_title"), "Please provide a secret payload.")
            return

        out_path, _ = QFileDialog.getSaveFileName(self, "Save Stego Image", "stego_vault.png", "PNG Images (*.png)")
        if not out_path:
            return

        self._start_worker("hide", {
            "carrier_path": self.hide_carrier,
            "output_path": out_path,
            "passphrase": passphrase,
            "data": secret_text.encode("utf-8"),
            "is_file": False
        })

    def _on_run_extract(self):
        if not self.extract_file:
            QMessageBox.warning(self, tr("error_title"), "Please drop a Stego Image first.")
            return

        passphrase = self.txt_ext_pass.text().strip()
        if not passphrase:
            QMessageBox.warning(self, tr("error_title"), "Please provide the decryption passphrase.")
            return

        self._start_worker("extract", {
            "stego_path": self.extract_file,
            "passphrase": passphrase
        })

    def _on_save_extracted_file(self):
        if not self.extracted_payload or not self.extracted_payload.is_file:
            return
        default_fn = self.extracted_payload.filename or "extracted_secret.bin"
        save_p, _ = QFileDialog.getSaveFileName(self, "Save Decrypted File", default_fn, "All Files (*.*)")
        if save_p:
            with open(save_p, "wb") as f:
                f.write(self.extracted_payload.data)
            QMessageBox.information(self, tr("status_success"), f"Saved to {save_p}")

    def _on_run_shred(self):
        if not self.shred_file:
            return

        confirm = QMessageBox.warning(
            self,
            "Confirm Irreversible Destruction",
            f"Are you sure you want to PERMANENTLY destroy:\n{self.shred_file}\n\n"
            "This file will be cryptographically overwritten and cannot be recovered by any means!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        passes = self.combo_shred_passes.currentData() or 3
        self._start_worker("shred", {
            "filepath": self.shred_file,
            "passes": passes
        })
