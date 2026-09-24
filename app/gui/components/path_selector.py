import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog
)
from PySide6.QtCore import Signal, Qt
from ...config import PlatformType

class PathSelectorWidget(QWidget):
    """Allows user to select and specify where the output installer file is saved"""
    output_dir_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_dir):
            desktop_dir = os.path.expanduser("~")
        self.output_dir = desktop_dir
        self.app_name = "MyApp"
        self.platform = PlatformType.DESKTOP

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title = QLabel("مسیر ذخیره‌سازی فایل نصبی:")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        # Path input row with browse button
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.path_input = QLineEdit()
        self.path_input.setText(self.output_dir)
        self.path_input.setLayoutDirection(Qt.LeftToRight)
        self.path_input.textChanged.connect(self.on_text_changed)
        input_layout.addWidget(self.path_input)

        self.btn_browse = QPushButton("تغییر پوشه")
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self.browse_destination)
        input_layout.addWidget(self.btn_browse)

        layout.addLayout(input_layout)

        # Sub-row: Quick shortcuts and live preview in one line
        sub_layout = QHBoxLayout()
        sub_layout.setContentsMargins(0, 0, 0, 0)

        # Live file preview
        self.preview_lbl = QLabel()
        self.preview_lbl.setLayoutDirection(Qt.LeftToRight)
        self.preview_lbl.setStyleSheet("font-size: 11px; color: #3fb950; font-family: 'Consolas', monospace;")
        sub_layout.addWidget(self.preview_lbl)

        sub_layout.addStretch()

        # Minimalist shortcuts
        lbl_shortcuts = QLabel("میانبرها:")
        lbl_shortcuts.setStyleSheet("font-size: 11px; color: #8b949e;")
        sub_layout.addWidget(lbl_shortcuts)

        btn_desktop = QPushButton("دسکتاپ")
        btn_desktop.setStyleSheet("background: transparent; border: none; color: #58a6ff; font-size: 11px; text-decoration: underline;")
        btn_desktop.setCursor(Qt.PointingHandCursor)
        btn_desktop.clicked.connect(self.set_to_desktop)
        sub_layout.addWidget(btn_desktop)

        btn_downloads = QPushButton("دانلودها")
        btn_downloads.setStyleSheet("background: transparent; border: none; color: #58a6ff; font-size: 11px; text-decoration: underline;")
        btn_downloads.setCursor(Qt.PointingHandCursor)
        btn_downloads.clicked.connect(self.set_to_downloads)
        sub_layout.addWidget(btn_downloads)

        layout.addLayout(sub_layout)
        self.update_preview()

    def update_preview(self):
        ext = ".exe" if self.platform == PlatformType.DESKTOP else ".apk"
        final_file = os.path.join(self.output_dir, f"{self.app_name}{ext}")
        self.preview_lbl.setText(f"خروجی: {final_file}")

    def set_app_info(self, app_name: str, platform: PlatformType):
        self.app_name = app_name if app_name.strip() else "MyApp"
        self.platform = platform
        self.update_preview()

    def set_to_desktop(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(desktop):
            self.set_path(desktop)

    def set_to_downloads(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads):
            self.set_path(downloads)

    def browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه ذخیره فایل نصبی", self.output_dir)
        if folder:
            self.set_path(folder)

    def set_path(self, path: str):
        self.output_dir = path
        self.path_input.setText(path)
        self.update_preview()
        self.output_dir_changed.emit(path)

    def on_text_changed(self, text: str):
        self.output_dir = text.strip()
        self.update_preview()
        self.output_dir_changed.emit(self.output_dir)

    def get_output_dir(self) -> str:
        return self.output_dir
