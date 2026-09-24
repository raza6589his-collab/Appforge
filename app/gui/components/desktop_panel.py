import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton
)
from PySide6.QtCore import Signal, Qt
from .icon_uploader import IconUploaderWidget
from ...utils.file_utils import detect_asset_folders

class DesktopPanel(QWidget):
    """Configuration panel specifically for Desktop (.exe) builds"""
    config_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_source_dir = ""
        self.setup_ui()

    def _emit_change(self, *args):
        self.config_changed.emit()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("تنظیمات بیلد ویندوز:")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(0, 2, 0, 2)

        lbl_width = 85

        # Row 0: App Name & Version
        lbl_name = QLabel("نام برنامه:")
        lbl_name.setFixedWidth(lbl_width)
        grid.addWidget(lbl_name, 0, 0)

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

        # Row 1: Company / Author & Description (Metadata)
        lbl_comp = QLabel("شرکت/سازنده:")
        lbl_comp.setFixedWidth(lbl_width)
        grid.addWidget(lbl_comp, 1, 0)

        self.txt_company = QLineEdit()
        self.txt_company.setPlaceholderText("اختیاری - نام توسعه‌دهنده یا شرکت")
        self.txt_company.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_company, 1, 1)

        lbl_desc = QLabel("توضیحات:")
        lbl_desc.setFixedWidth(40)
        grid.addWidget(lbl_desc, 1, 2)

        self.txt_desc = QLineEdit()
        self.txt_desc.setPlaceholderText("توضیحات نرم‌افزار")
        self.txt_desc.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_desc, 1, 3)

        # Row 2: Asset & Data Bundling
        lbl_assets = QLabel("فایل‌های جانبی:")
        lbl_assets.setFixedWidth(lbl_width)
        grid.addWidget(lbl_assets, 2, 0)

        asset_layout = QHBoxLayout()
        asset_layout.setSpacing(6)
        self.txt_assets = QLineEdit()
        self.txt_assets.setLayoutDirection(Qt.LeftToRight)
        self.txt_assets.setPlaceholderText("مانند: assets;assets, data;data")
        self.txt_assets.textChanged.connect(self._emit_change)
        
        self.btn_auto_assets = QPushButton("شناسایی خودکار")
        self.btn_auto_assets.setCursor(Qt.PointingHandCursor)
        self.btn_auto_assets.clicked.connect(self.auto_detect_assets)
        
        asset_layout.addWidget(self.txt_assets)
        asset_layout.addWidget(self.btn_auto_assets)
        grid.addLayout(asset_layout, 2, 1, 1, 3)

        # Row 3: Checkboxes
        lbl_opts = QLabel("گزینه‌ها:")
        lbl_opts.setFixedWidth(lbl_width)
        grid.addWidget(lbl_opts, 3, 0)

        check_layout = QHBoxLayout()
        check_layout.setSpacing(16)

        self.chk_auto_deps = QCheckBox("نصب خودکار پیش‌نیازها")
        self.chk_auto_deps.setChecked(True)
        self.chk_auto_deps.toggled.connect(self._emit_change)

        self.chk_onefile = QCheckBox("تک فایلی مستقل")
        self.chk_onefile.setChecked(True)
        self.chk_onefile.toggled.connect(self._emit_change)

        self.chk_windowed = QCheckBox("مخفی‌سازی کنسول")
        self.chk_windowed.setChecked(True)
        self.chk_windowed.toggled.connect(self._emit_change)

        self.chk_clean = QCheckBox("پاکسازی کش")
        self.chk_clean.setChecked(True)
        self.chk_clean.toggled.connect(self._emit_change)

        check_layout.addWidget(self.chk_auto_deps)
        check_layout.addWidget(self.chk_onefile)
        check_layout.addWidget(self.chk_windowed)
        check_layout.addWidget(self.chk_clean)
        check_layout.addStretch()

        grid.addLayout(check_layout, 3, 1, 1, 3)

        # Row 4: Runtime Guarantees
        lbl_guarantee = QLabel("تضمین اجرا:")
        lbl_guarantee.setFixedWidth(lbl_width)
        grid.addWidget(lbl_guarantee, 4, 0)

        guar_layout = QHBoxLayout()
        guar_layout.setSpacing(16)

        self.chk_auto_hidden = QCheckBox("اسکن وابستگی‌های پنهان")
        self.chk_auto_hidden.setChecked(True)
        self.chk_auto_hidden.toggled.connect(self._emit_change)

        self.chk_smoke_test = QCheckBox("تست سلامت اولیه (Smoke Test)")
        self.chk_smoke_test.setChecked(True)
        self.chk_smoke_test.toggled.connect(self._emit_change)

        self.chk_inno = QCheckBox("ساخت اسکریپت نصاب (Inno Setup)")
        self.chk_inno.setChecked(True)
        self.chk_inno.toggled.connect(self._emit_change)

        self.btn_path_guide = QPushButton("راهنمای مسیر فایل‌ها")
        self.btn_path_guide.setCursor(Qt.PointingHandCursor)
        self.btn_path_guide.clicked.connect(self.show_path_guide_dialog)

        guar_layout.addWidget(self.chk_auto_hidden)
        guar_layout.addWidget(self.chk_smoke_test)
        guar_layout.addWidget(self.chk_inno)
        guar_layout.addWidget(self.btn_path_guide)
        guar_layout.addStretch()

        grid.addLayout(guar_layout, 4, 1, 1, 3)

        # Row 5: Extra Arguments
        lbl_extra = QLabel("دستورات جانبی:")
        lbl_extra.setFixedWidth(lbl_width)
        grid.addWidget(lbl_extra, 5, 0)

        self.txt_extra = QLineEdit()
        self.txt_extra.setLayoutDirection(Qt.LeftToRight)
        self.txt_extra.setPlaceholderText("اختیاری، مثلا: --hidden-import=requests")
        self.txt_extra.textChanged.connect(self._emit_change)
        grid.addWidget(self.txt_extra, 5, 1, 1, 3)

        layout.addLayout(grid)

        # Icon Uploader Component
        self.icon_uploader = IconUploaderWidget()
        self.icon_uploader.icon_changed.connect(self._emit_change)
        layout.addWidget(self.icon_uploader)

    def show_path_guide_dialog(self):
        from PySide6.QtWidgets import QDialog, QTextEdit, QMessageBox
        from ...utils.file_utils import RESOURCE_PATH_HELPER_CODE
        from PySide6.QtGui import QGuiApplication
        
        dlg = QDialog(self)
        dlg.setWindowTitle("راهنمای دسترسی امن به فایل‌ها در پایتون")
        dlg.resize(550, 320)
        d_layout = QVBoxLayout(dlg)
        
        info = QLabel(
            "در فایل‌های تک‌فایلی (.exe)، فایل‌های جانبی در پوشه موقت سیستم باز می‌شوند.\n"
            "برای جلوگیری از ارور FileNotFoundError، از تابع استاندارد زیر در سورس‌کد خود استفاده کنید:"
        )
        info.setWordWrap(True)
        d_layout.addWidget(info)
        
        code_view = QTextEdit()
        code_view.setPlainText(RESOURCE_PATH_HELPER_CODE)
        code_view.setReadOnly(True)
        code_view.setLayoutDirection(Qt.LeftToRight)
        d_layout.addWidget(code_view)
        
        btn_copy = QPushButton("کپی کد کمکی در کلیپ‌بورد")
        def copy_code():
            QGuiApplication.clipboard().setText(RESOURCE_PATH_HELPER_CODE)
            QMessageBox.information(dlg, "کپی شد", "کد تابع کمکی با موفقیت در حافظه کپی شد.")
        btn_copy.clicked.connect(copy_code)
        d_layout.addWidget(btn_copy)
        
        dlg.exec()

    def set_source_directory(self, source_dir: str):
        self.current_source_dir = source_dir
        self.auto_detect_assets()

    def auto_detect_assets(self):
        if not self.current_source_dir or not os.path.isdir(self.current_source_dir):
            return
        found_dirs = detect_asset_folders(self.current_source_dir)
        if found_dirs:
            pairs = [f"{d};{d}" for d in found_dirs]
            current = [p.strip() for p in self.txt_assets.text().split(",") if p.strip()]
            for p in pairs:
                if p not in current:
                    current.append(p)
            self.txt_assets.setText(", ".join(current))

    def load_from_config(self, config):
        self.txt_app_name.setText(config.app_name)
        self.txt_version.setText(config.app_version)
        self.txt_company.setText(config.company_name)
        self.txt_desc.setText(config.file_description)
        if config.add_data:
            self.txt_assets.setText(", ".join(config.add_data))
        if config.icon_path:
            self.icon_uploader.set_icon(config.icon_path)
        self.chk_auto_deps.setChecked(config.auto_install_deps)
        self.chk_onefile.setChecked(config.onefile)
        self.chk_windowed.setChecked(config.windowed)
        self.chk_clean.setChecked(config.clean_build)
        self.chk_auto_hidden.setChecked(config.auto_hidden_imports)
        self.chk_smoke_test.setChecked(config.enable_smoke_test)
        self.chk_inno.setChecked(config.generate_installer)
        self.txt_extra.setText(config.desktop_extra_args)

    def get_settings(self):
        assets_raw = [a.strip() for a in self.txt_assets.text().split(",") if a.strip()]
        return {
            "app_name": self.txt_app_name.text().strip() or "MyApp",
            "version": self.txt_version.text().strip() or "1.0.0",
            "company_name": self.txt_company.text().strip(),
            "file_description": self.txt_desc.text().strip(),
            "add_data": assets_raw,
            "icon_path": self.icon_uploader.get_icon_path() or None,
            "auto_install_deps": self.chk_auto_deps.isChecked(),
            "onefile": self.chk_onefile.isChecked(),
            "windowed": self.chk_windowed.isChecked(),
            "clean": self.chk_clean.isChecked(),
            "auto_hidden_imports": self.chk_auto_hidden.isChecked(),
            "enable_smoke_test": self.chk_smoke_test.isChecked(),
            "generate_installer": self.chk_inno.isChecked(),
            "extra_args": self.txt_extra.text().strip()
        }
