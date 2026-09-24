import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox
)
from PySide6.QtCore import Signal, Qt
from .icon_uploader import IconUploaderWidget

class AndroidPanel(QWidget):
    """Configuration panel specifically for Android APK builds"""
    config_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def _emit_change(self, *args):
        self.config_changed.emit()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("تنظیمات بیلد اندروید:")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(0, 4, 0, 4)

        lbl_width = 85

        # Row 0: App Title & Version
        lbl_title = QLabel("عنوان برنامه:")
        lbl_title.setFixedWidth(lbl_width)
        grid.addWidget(lbl_title, 0, 0)

        self.txt_app_name = QLineEdit("MyApp")
        self.txt_app_name.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_app_name, 0, 1)

        lbl_version = QLabel("نسخه:")
        lbl_version.setFixedWidth(40)
        grid.addWidget(lbl_version, 0, 2)

        self.txt_version = QLineEdit("1.0.0")
        self.txt_version.setLayoutDirection(Qt.LeftToRight)
        self.txt_version.setFixedWidth(90)
        self.txt_version.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_version, 0, 3)

        # Row 1: Package Domain & Name
        lbl_domain = QLabel("دامنه پکیج:")
        lbl_domain.setFixedWidth(lbl_width)
        grid.addWidget(lbl_domain, 1, 0)

        self.txt_package_domain = QLineEdit("org.example")
        self.txt_package_domain.setLayoutDirection(Qt.LeftToRight)
        self.txt_package_domain.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_package_domain, 1, 1)

        lbl_pkg = QLabel("نام پکیج:")
        lbl_pkg.setFixedWidth(50)
        grid.addWidget(lbl_pkg, 1, 2)

        self.txt_package_name = QLineEdit("myapp")
        self.txt_package_name.setLayoutDirection(Qt.LeftToRight)
        self.txt_package_name.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_package_name, 1, 3)

        # Row 2: Orientation & Requirements
        lbl_ori = QLabel("جهت صفحه:")
        lbl_ori.setFixedWidth(lbl_width)
        grid.addWidget(lbl_ori, 2, 0)

        self.cmb_orientation = QComboBox()
        self.cmb_orientation.addItems(["portrait (عمودی)", "landscape (افقی)", "all (چرخش خودکار)"])
        self.cmb_orientation.currentIndexChanged.connect(self._emit_change)
        grid.addWidget(self.cmb_orientation, 2, 1)

        lbl_req = QLabel("پکیج‌ها:")
        lbl_req.setFixedWidth(50)
        grid.addWidget(lbl_req, 2, 2)

        self.txt_reqs = QLineEdit("python3,kivy")
        self.txt_reqs.setLayoutDirection(Qt.LeftToRight)
        self.txt_reqs.setPlaceholderText("مانند: python3,kivy,requests")
        self.txt_reqs.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_reqs, 2, 3)

        # Row 3: Options (Auto-deps + Permissions)
        lbl_opts = QLabel("گزینه‌ها:")
        lbl_opts.setFixedWidth(lbl_width)
        grid.addWidget(lbl_opts, 3, 0)

        opts_layout = QHBoxLayout()
        opts_layout.setSpacing(16)
        self.chk_auto_deps = QCheckBox("نصب خودکار پیش‌نیازها قبل از بیلد")
        self.chk_auto_deps.setChecked(True)
        self.chk_auto_deps.toggled.connect(self._emit_change)

        self.chk_perm_internet = QCheckBox("اینترنت")
        self.chk_perm_internet.setChecked(True)
        self.chk_perm_internet.toggled.connect(self._emit_change)
        self.chk_perm_storage = QCheckBox("حافظه فایل")
        self.chk_perm_storage.toggled.connect(self._emit_change)
        self.chk_perm_camera = QCheckBox("دوربین")
        self.chk_perm_camera.toggled.connect(self._emit_change)

        opts_layout.addWidget(self.chk_auto_deps)
        opts_layout.addWidget(self.chk_perm_internet)
        opts_layout.addWidget(self.chk_perm_storage)
        opts_layout.addWidget(self.chk_perm_camera)
        opts_layout.addStretch()
        grid.addLayout(opts_layout, 3, 1, 1, 3)

        layout.addLayout(grid)

        # 4. Modern Icon Uploader Component
        self.icon_uploader = IconUploaderWidget()
        self.icon_uploader.icon_changed.connect(self._emit_change)
        layout.addWidget(self.icon_uploader)

    def get_settings(self):
        perms = []
        if self.chk_perm_internet.isChecked():
            perms.append("INTERNET")
        if self.chk_perm_storage.isChecked():
            perms.extend(["READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE"])
        if self.chk_perm_camera.isChecked():
            perms.append("CAMERA")

        orientation_raw = self.cmb_orientation.currentText().split()[0]
        reqs = [r.strip() for r in self.txt_reqs.text().split(",") if r.strip()]

        return {
            "app_name": self.txt_app_name.text().strip() or "MyApp",
            "version": self.txt_version.text().strip() or "1.0.0",
            "package_domain": self.txt_package_domain.text().strip() or "org.example",
            "package_name": self.txt_package_name.text().strip() or "myapp",
            "orientation": orientation_raw,
            "requirements": reqs,
            "permissions": perms,
            "auto_install_deps": self.chk_auto_deps.isChecked(),
            "icon_path": self.icon_uploader.get_icon_path() or None
        }
