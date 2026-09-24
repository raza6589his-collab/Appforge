import os
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from ...utils.file_utils import get_image_info

class IconPreviewBox(QFrame):
    """Square rounded preview box for application icon"""
    clicked = Signal()

    def __init__(self, size: int = 72, parent=None):
        super().__init__(parent)
        self.box_size = size
        self.pixmap = None
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #58a6ff;
            }
        """)

    def set_image(self, image_path: str):
        if image_path and os.path.exists(image_path):
            self.pixmap = QPixmap(image_path)
        else:
            self.pixmap = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        if self.pixmap and not self.pixmap.isNull():
            # Draw clipped image with rounded corners
            path = QPainterPath()
            path.addRoundedRect(2, 2, self.box_size - 4, self.box_size - 4, 10, 10)
            painter.setClipPath(path)
            
            scaled = self.pixmap.scaled(
                self.box_size - 4, self.box_size - 4,
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            # Center the pixmap
            x = (self.box_size - scaled.width()) // 2
            y = (self.box_size - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # Draw subtle placeholder text
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(Qt.darkGray)
            font = painter.font()
            font.setPointSize(9)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "بدون\nآیکون")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class IconUploaderWidget(QWidget):
    """Component for uploading, dragging & dropping, and previewing application icons"""
    icon_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.icon_path = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # 1. Visual Preview Box
        self.preview_box = IconPreviewBox(size=72)
        self.preview_box.clicked.connect(self.browse_icon)
        layout.addWidget(self.preview_box)

        # 2. Controls and Metadata Column
        ctrl_layout = QVBoxLayout()
        ctrl_layout.setContentsMargins(0, 2, 0, 2)
        ctrl_layout.setSpacing(6)

        title_lbl = QLabel("آیکون و لوگوی برنامه:")
        title_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #f0f6fc;")
        ctrl_layout.addWidget(title_lbl)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_browse = QPushButton("انتخاب تصویر...")
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self.browse_icon)
        btn_row.addWidget(self.btn_browse)

        self.btn_remove = QPushButton("حذف لوگو")
        self.btn_remove.setObjectName("DangerButton")
        self.btn_remove.setCursor(Qt.PointingHandCursor)
        self.btn_remove.setEnabled(False)
        self.btn_remove.clicked.connect(self.clear_icon)
        btn_row.addWidget(self.btn_remove)

        btn_row.addStretch()
        ctrl_layout.addLayout(btn_row)

        # Metadata / Status string
        self.status_lbl = QLabel("اختیاری - تصویر PNG، JPG یا ICO را به این کادر بکشید")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #8b949e;")
        ctrl_layout.addWidget(self.status_lbl)

        layout.addLayout(ctrl_layout)

    def browse_icon(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب لوگو و آیکون اپلیکیشن",
            "",
            "تصاویر (*.png *.jpg *.jpeg *.webp *.ico);;تمام فایل‌ها (*.*)"
        )
        if file:
            self.set_icon(file)

    def set_icon(self, file_path: str):
        if not file_path or not os.path.exists(file_path):
            self.clear_icon()
            return

        self.icon_path = os.path.abspath(file_path)
        self.preview_box.set_image(self.icon_path)
        self.btn_remove.setEnabled(True)

        # Inspect metadata
        info = get_image_info(self.icon_path)
        if info:
            fmt = info['format']
            dims = f"{info['width']}×{info['height']}"
            size = info['size_str']
            self.status_lbl.setText(f"لوگو بارگذاری شد: {fmt} • {dims} پیکسل ({size})")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #3fb950; font-weight: 500;")
        else:
            self.status_lbl.setText(f"فایل آیکون: {os.path.basename(self.icon_path)}")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #58a6ff;")

        self.icon_changed.emit(self.icon_path)

    def clear_icon(self):
        self.icon_path = ""
        self.preview_box.set_image(None)
        self.btn_remove.setEnabled(False)
        self.status_lbl.setText("تصویر انتخاب نشده است (اختیاری)")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #8b949e;")
        self.icon_changed.emit("")

    def get_icon_path(self) -> str:
        return self.icon_path

    # Drag & Drop Events
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile().lower()
                if path.endswith(('.png', '.jpg', '.jpeg', '.webp', '.ico', '.bmp')):
                    event.acceptProposedAction()
                    self.preview_box.setStyleSheet("""
                        QFrame {
                            background-color: #1c2128;
                            border: 2px dashed #58a6ff;
                            border-radius: 12px;
                        }
                    """)

    def dragLeaveEvent(self, event):
        self.preview_box.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
        """)

    def dropEvent(self, event):
        self.preview_box.setStyleSheet("""
            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
            }
        """)
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.set_icon(path)
