from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QDialog, QTextEdit, QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

class UpdateDialog(QDialog):
    """Clean popup dialog showing release notes and direct download button"""
    def __init__(self, update_info: dict, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setWindowTitle(f"بروزرسانی AppForge - نسخه {update_info.get('version', '')}")
        self.resize(520, 380)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(18, 18, 18, 18)

        # Header Title
        title_lbl = QLabel(f"🚀 {self.update_info.get('title', 'نسخه جدید در دسترس است!')}")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #58a6ff;")
        layout.addWidget(title_lbl)

        sub_lbl = QLabel(f"نسخه جدید ({self.update_info.get('version', '')}) در گیت‌هاب منتشر شد.")
        sub_lbl.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(sub_lbl)

        # Changelog / Release Notes
        notes_title = QLabel("تغییرات و امکانات نسخه جدید:")
        notes_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #c9d1d9; margin-top: 6px;")
        layout.addWidget(notes_title)

        notes_box = QTextEdit()
        notes_box.setReadOnly(True)
        notes_box.setStyleSheet(
            "background-color: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 8px; color: #c9d1d9; font-size: 12px;"
        )
        notes_text = self.update_info.get("notes", "").strip() or "تغییرات جزئی، بهبود پایداری و رفع باگ‌ها."
        notes_box.setPlainText(notes_text)
        layout.addWidget(notes_box)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        btn_download = QPushButton("📥 دانلود نسخه جدید از گیت‌هاب")
        btn_download.setCursor(Qt.PointingHandCursor)
        btn_download.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: #ffffff;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid #2ea043;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        btn_download.clicked.connect(self.on_download_clicked)

        btn_close = QPushButton("بعداً")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid #30363d;
            }
            QPushButton:hover {
                background-color: #30363d;
            }
        """)
        btn_close.clicked.connect(self.accept)

        btn_layout.addWidget(btn_download)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

    def on_download_clicked(self):
        url = self.update_info.get("download_url") or self.update_info.get("release_url")
        if url:
            QDesktopServices.openUrl(QUrl(url))
        self.accept()

class UpdateBannerWidget(QFrame):
    """
    Sleek GitHub-style top banner that appears when a new release is detected.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_info = {}
        self.setVisible(False)
        self.setup_ui()

    def setup_ui(self):
        self.setLayoutDirection(Qt.RightToLeft)
        self.setStyleSheet("""
            UpdateBannerWidget {
                background-color: #161b22;
                border: 1px solid #1f6feb;
                border-radius: 6px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)

        self.lbl_msg = QLabel("🚀 نسخه جدید AppForge در دسترس است!")
        self.lbl_msg.setStyleSheet("color: #58a6ff; font-weight: 500; font-size: 12px;")
        layout.addWidget(self.lbl_msg)

        layout.addStretch()

        self.btn_changelog = QPushButton("مشاهده تغییرات")
        self.btn_changelog.setCursor(Qt.PointingHandCursor)
        self.btn_changelog.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #30363d;
                color: #ffffff;
            }
        """)
        self.btn_changelog.clicked.connect(self.show_changelog)
        layout.addWidget(self.btn_changelog)

        self.btn_download = QPushButton("📥 دانلود نسخه جدید")
        self.btn_download.setCursor(Qt.PointingHandCursor)
        self.btn_download.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #2ea043;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        self.btn_download.clicked.connect(self.open_download)
        layout.addWidget(self.btn_download)

        self.btn_close = QPushButton("✕")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8b949e;
                border: none;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #f85149;
            }
        """)
        self.btn_close.clicked.connect(self.hide)
        layout.addWidget(self.btn_close)

    def display_update(self, info: dict):
        self.update_info = info
        version = info.get("version", "")
        self.lbl_msg.setText(f"🚀 نسخه جدید AppForge ({version}) در گیت‌هاب منتشر شد!")
        self.setVisible(True)

    def show_changelog(self):
        if self.update_info:
            dlg = UpdateDialog(self.update_info, self)
            dlg.exec()

    def open_download(self):
        url = self.update_info.get("download_url") or self.update_info.get("release_url")
        if url:
            QDesktopServices.openUrl(QUrl(url))
