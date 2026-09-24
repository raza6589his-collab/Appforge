from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QProgressBar, QPushButton, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor

class TerminalView(QWidget):
    """Terminal view for streaming live build logs and progress"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.show_welcome_message()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Header bar
        header_layout = QHBoxLayout()
        title_lbl = QLabel("گزارش عملیات ساخت:")
        title_lbl.setObjectName("SectionTitle")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        self.btn_copy = QPushButton("کپی لاگ‌ها")
        self.btn_copy.setCursor(Qt.PointingHandCursor)
        self.btn_copy.clicked.connect(self.copy_logs)

        self.btn_clear = QPushButton("پاکسازی")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_logs)

        header_layout.addWidget(self.btn_copy)
        header_layout.addWidget(self.btn_clear)
        layout.addLayout(header_layout)

        # Slim Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Terminal text area
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("TerminalLogs")
        self.text_edit.setReadOnly(True)
        self.text_edit.setLayoutDirection(Qt.LeftToRight)
        layout.addWidget(self.text_edit)

    def show_welcome_message(self):
        welcome_html = """
        <div style='color: #8b949e; font-family: Consolas, monospace; padding: 4px; font-size: 11px;'>
            <div style='color: #58a6ff; font-weight: bold; margin-bottom: 4px;'>[Ready] سامانه AppForge آماده دریافت سورس کد پروژه است.</div>
            <div>• سورس‌کد پروژه را در کادر مربوطه مشخص کنید.</div>
            <div>• پلتفرم خروجی و تنظیمات بیلد را بررسی نمایید.</div>
            <div>• روی دکمه شروع ساخت فایل نصبی کلیک فرمایید.</div>
        </div>
        """
        self.text_edit.setHtml(welcome_html)

    def append_log(self, message: str, level: str = "info"):
        color = "#c9d1d9"
        badge = "[INFO]"

        if level == "error":
            color = "#f85149"
            badge = "[ERROR]"
        elif level == "warn":
            color = "#d29922"
            badge = "[WARN]"
        elif level == "success":
            color = "#3fb950"
            badge = "[SUCCESS]"
        elif level == "info":
            color = "#58a6ff"
            badge = "[INFO]"

        html_line = f"<div style='margin-bottom: 2px; color: {color}; font-family: Consolas, monospace; font-size: 11px;'><span style='color: #484f58;'>{badge}</span> {message}</div>"
        
        self.text_edit.append(html_line)
        self.text_edit.moveCursor(QTextCursor.End)

    def set_progress(self, val: int):
        self.progress_bar.setValue(val)

    def clear_logs(self):
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.show_welcome_message()

    def copy_logs(self):
        text = self.text_edit.toPlainText()
        QApplication.clipboard().setText(text)
