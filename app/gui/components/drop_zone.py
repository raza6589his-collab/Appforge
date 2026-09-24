import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from ...utils.file_utils import detect_entry_point

class DropZoneWidget(QFrame):
    """Clean Minimalist Drop Zone for the source project"""
    source_selected = Signal(str, str) # (source_dir, entry_point)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZoneWidget")
        self.setAcceptDrops(True)
        self.source_dir = ""
        self.entry_point = ""
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(125)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.update_style(is_hover=False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(6)

        # Main text
        self.main_lbl = QLabel("پوشه یا فایل پروژه را به این کادر بکشید و رها کنید")
        self.main_lbl.setAlignment(Qt.AlignCenter)
        self.main_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #f0f6fc; background: transparent; border: none;")
        layout.addWidget(self.main_lbl)

        # Subtitle
        self.details_lbl = QLabel("یا از کلیدهای زیر برای انتخاب دستی سورس‌کد استفاده نمایید")
        self.details_lbl.setAlignment(Qt.AlignCenter)
        self.details_lbl.setStyleSheet("font-size: 11px; color: #8b949e; background: transparent; border: none;")
        layout.addWidget(self.details_lbl)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(10)

        self.btn_browse_folder = QPushButton("انتخاب پوشه سورس")
        self.btn_browse_folder.setCursor(Qt.PointingHandCursor)
        self.btn_browse_folder.clicked.connect(self.browse_folder)

        self.btn_browse_file = QPushButton("انتخاب فایل اصلی اسکریپت")
        self.btn_browse_file.setCursor(Qt.PointingHandCursor)
        self.btn_browse_file.clicked.connect(self.browse_file)

        btn_layout.addWidget(self.btn_browse_folder)
        btn_layout.addWidget(self.btn_browse_file)
        layout.addLayout(btn_layout)

    def update_style(self, is_hover: bool):
        if is_hover:
            self.setStyleSheet("""
                #DropZoneWidget {
                    background-color: #1c2128;
                    border: 1px dashed #58a6ff;
                    border-radius: 6px;
                }
            """)
        else:
            self.setStyleSheet("""
                #DropZoneWidget {
                    background-color: #161b22;
                    border: 1px dashed #30363d;
                    border-radius: 6px;
                }
            """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.update_style(is_hover=True)

    def dragLeaveEvent(self, event):
        self.update_style(is_hover=False)

    def dropEvent(self, event):
        self.update_style(is_hover=False)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.handle_path_input(path)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "انتخاب پوشه پروژه سورس کد")
        if folder:
            self.handle_path_input(folder)

    def browse_file(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل اصلی پروژه", "", "فایل‌های پایتون (*.py);;تمام فایل‌ها (*.*)"
        )
        if file:
            self.handle_path_input(file)

    def handle_path_input(self, path: str):
        if not os.path.exists(path):
            return

        if os.path.isfile(path):
            self.source_dir = os.path.dirname(path)
            self.entry_point = os.path.basename(path)
        else:
            self.source_dir = path
            detected = detect_entry_point(path)
            self.entry_point = detected if detected else "main.py"

        folder_name = os.path.basename(self.source_dir)
        self.main_lbl.setText(f"پروژه: {folder_name}")
        self.details_lbl.setText(f"فایل اصلی: \u200E{self.entry_point}\u200E | مسیر: \u200E{self.source_dir}\u200E")
        self.details_lbl.setStyleSheet("font-size: 11px; color: #58a6ff; background: transparent; font-weight: 500; border: none;")

        self.source_selected.emit(self.source_dir, self.entry_point)
