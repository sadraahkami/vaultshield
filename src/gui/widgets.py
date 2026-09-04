"""
Custom Qt Widgets for VaultShield Desktop Interface.
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from .icons import IconProvider


class FileDropZone(QFrame):
    file_dropped = pyqtSignal(str)

    def __init__(self, hint_text: str = "Drag & drop files here", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropzoneFrame")
        self.setStyleSheet("""
            QFrame#dropzoneFrame {
                border: 2px dashed #334155;
                border-radius: 10px;
                background-color: #080C14;
                padding: 20px;
            }
            QFrame#dropzoneFrame:hover {
                border-color: #38BDF8;
                background-color: #0F172A;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        self.icon_lbl = QLabel()
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setPixmap(IconProvider.get_icon("shield", "#38BDF8", 36).pixmap(36, 36))
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(hint_text)
        self.text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_lbl.setStyleSheet("color: #94A3B8; font-size: 13px; font-weight: bold;")
        layout.addWidget(self.text_lbl)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame#dropzoneFrame {
                    border: 2px dashed #38BDF8;
                    background-color: #1E293B;
                }
            """)
        else:
            super().dragEnterEvent(event)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame#dropzoneFrame {
                border: 2px dashed #334155;
                border-radius: 10px;
                background-color: #080C14;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                lp = urls[0].toLocalFile()
                if lp:
                    self.file_dropped.emit(lp)
            event.acceptProposedAction()
        self.dragLeaveEvent(None)


class FileSelectedCard(QFrame):
    delete_requested = pyqtSignal()

    def __init__(self, filepath: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.filepath = filepath
        p = Path(filepath)
        size = p.stat().st_size if p.exists() else 0

        self.setStyleSheet("""
            FileSelectedCard {
                background-color: #080C14;
                border: 1px solid #1E293B;
                border-radius: 8px;
                padding: 8px 12px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(IconProvider.get_icon("file", "#38BDF8", 22).pixmap(22, 22))
        layout.addWidget(icon_lbl)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        name_lbl = QLabel(p.name)
        name_lbl.setStyleSheet("font-weight: bold; color: #F8FAFC; font-size: 13px;")
        info_col.addWidget(name_lbl)

        size_kb = size / 1024.0
        size_str = f"{size_kb / 1024.0:.2f} MB" if size_kb > 1024 else f"{size_kb:.1f} KB"
        meta_lbl = QLabel(f"{size_str} | {str(p)}")
        meta_lbl.setStyleSheet("color: #64748B; font-size: 11px;")
        info_col.addWidget(meta_lbl)

        layout.addLayout(info_col, stretch=1)

        del_btn = QPushButton()
        del_btn.setIcon(IconProvider.get_icon("trash", "#EF4444", 16))
        del_btn.setFixedSize(28, 28)
        del_btn.setStyleSheet("background: transparent; border: none;")
        del_btn.clicked.connect(self.delete_requested.emit)
        layout.addWidget(del_btn)
