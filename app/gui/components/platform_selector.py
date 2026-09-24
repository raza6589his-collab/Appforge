from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QButtonGroup
from PySide6.QtCore import Signal, Qt
from ...config import PlatformType

class PlatformSelectorWidget(QWidget):
    """Modern Segmented Tab Control for toggling between Desktop and Android"""
    platform_changed = Signal(PlatformType)

    def __init__(self, initial_platform: PlatformType = PlatformType.DESKTOP, parent=None):
        super().__init__(parent)
        self.current_platform = initial_platform
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title = QLabel("پلتفرم خروجی:")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        # Segmented Control Container
        segment_box = QWidget()
        segment_box.setStyleSheet("""
            QWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 2px;
            }
        """)
        seg_layout = QHBoxLayout(segment_box)
        seg_layout.setContentsMargins(3, 3, 3, 3)
        seg_layout.setSpacing(4)

        self.btn_group = QButtonGroup(self)

        self.btn_desktop = QPushButton("ویندوز دسکتاپ (EXE)")
        self.btn_desktop.setCheckable(True)
        self.btn_desktop.setChecked(self.current_platform == PlatformType.DESKTOP)
        self.btn_desktop.setCursor(Qt.PointingHandCursor)
        self.btn_desktop.clicked.connect(lambda: self.select_platform(PlatformType.DESKTOP))

        self.btn_android = QPushButton("اندروید موبایل (APK)")
        self.btn_android.setCheckable(True)
        self.btn_android.setChecked(self.current_platform == PlatformType.ANDROID)
        self.btn_android.setCursor(Qt.PointingHandCursor)
        self.btn_android.clicked.connect(lambda: self.select_platform(PlatformType.ANDROID))

        self.btn_group.addButton(self.btn_desktop)
        self.btn_group.addButton(self.btn_android)

        seg_layout.addWidget(self.btn_desktop)
        seg_layout.addWidget(self.btn_android)

        self.update_segment_styles()
        layout.addWidget(segment_box)

    def select_platform(self, platform: PlatformType):
        if self.current_platform == platform:
            return
        self.current_platform = platform
        self.btn_desktop.setChecked(platform == PlatformType.DESKTOP)
        self.btn_android.setChecked(platform == PlatformType.ANDROID)
        self.update_segment_styles()
        self.platform_changed.emit(platform)

    def update_segment_styles(self):
        active_style = """
            QPushButton {
                background-color: #1f6feb;
                border: none;
                border-radius: 4px;
                color: #ffffff;
                font-weight: 600;
                padding: 8px 16px;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: #8b949e;
                font-weight: 500;
                padding: 8px 16px;
            }
            QPushButton:hover {
                color: #f0f6fc;
                background-color: #21262d;
            }
        """

        if self.current_platform == PlatformType.DESKTOP:
            self.btn_desktop.setStyleSheet(active_style)
            self.btn_android.setStyleSheet(inactive_style)
        else:
            self.btn_desktop.setStyleSheet(inactive_style)
            self.btn_android.setStyleSheet(active_style)
