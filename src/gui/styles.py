"""
Cyber Glassmorphic Dark Theme stylesheet for VaultShield.
"""

DARK_THEME = """
QMainWindow {
    background-color: #080C14;
    color: #F8FAFC;
}

QWidget {
    background-color: transparent;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Vazirmatn', Tahoma, sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #1E293B;
    border-radius: 8px;
    background-color: #0F172A;
    padding: 14px;
}

QTabBar::tab {
    background-color: #1E293B;
    color: #94A3B8;
    padding: 10px 18px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #0284C7;
    color: #FFFFFF;
}

QTabBar::tab:hover:!selected {
    background-color: #334155;
    color: #F8FAFC;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284C7, stop:1 #2563EB);
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: bold;
    min-height: 22px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38BDF8, stop:1 #3B82F6);
}

QPushButton:pressed {
    background-color: #1D4ED8;
}

QPushButton:disabled {
    background-color: #334155;
    color: #64748B;
}

QPushButton#secondaryBtn {
    background-color: #1E293B;
    color: #F1F5F9;
    border: 1px solid #334155;
}

QPushButton#secondaryBtn:hover {
    background-color: #334155;
}

QPushButton#dangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
}

QPushButton#dangerBtn:hover {
    background-color: #EF4444;
}

QPushButton#langBtn {
    background-color: #1E293B;
    color: #38BDF8;
    border: 1px solid #38BDF8;
    padding: 6px 12px;
}

QLineEdit, QComboBox, QTextEdit {
    background-color: #080C14;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #F8FAFC;
    min-height: 22px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border-color: #38BDF8;
}

QProgressBar {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: bold;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #06B6D4);
    border-radius: 5px;
}
"""
