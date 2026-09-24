import os
import subprocess
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt

from ..config import ProjectConfig, PlatformType
from ..core import DesktopBuildWorker, AndroidBuildWorker, check_system_environment
from ..core.update_checker import UpdateCheckerWorker, CURRENT_VERSION
from ..utils.file_utils import open_in_file_manager
from .styles import MAIN_STYLESHEET
from .components import (
    PlatformSelectorWidget, DropZoneWidget, PathSelectorWidget,
    DesktopPanel, AndroidPanel, TerminalView, UpdateBannerWidget, UpdateDialog
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AppForge Studio")
        self.resize(1160, 780)
        self.setMinimumSize(960, 660)
        
        self.config = ProjectConfig()
        self.active_worker = None
        self.last_built_file = None
        self.update_thread = None

        self.setup_ui()
        self.check_environment_status()
        self.check_updates(manual=False)

    def setup_ui(self):
        self.setStyleSheet(MAIN_STYLESHEET)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 14, 18, 0)
        root_layout.setSpacing(12)

        # 1. Minimal Header Bar
        header_widget = self.create_header()
        root_layout.addWidget(header_widget)

        # 1.5 Sleek Update Banner
        self.update_banner = UpdateBannerWidget()
        root_layout.addWidget(self.update_banner)

        # 2. Main Studio Work Area (2 Columns)
        main_columns = QHBoxLayout()
        main_columns.setSpacing(18)

        # === COLUMN 1 (Left): Terminal & Build Operations ===
        build_col = QVBoxLayout()
        build_col.setSpacing(10)

        self.terminal = TerminalView()
        build_col.addWidget(self.terminal, stretch=1)

        # Action Buttons Layout
        action_layout = QVBoxLayout()
        action_layout.setSpacing(8)

        self.btn_build = QPushButton("شروع ساخت فایل نصبی ویندوز")
        self.btn_build.setObjectName("PrimaryButton")
        self.btn_build.setCursor(Qt.PointingHandCursor)
        self.btn_build.clicked.connect(self.start_build)
        action_layout.addWidget(self.btn_build)

        # Secondary Actions: Run App, Open Folder, Cancel
        sub_actions = QHBoxLayout()
        sub_actions.setSpacing(8)

        self.btn_run_app = QPushButton("اجرای برنامه")
        self.btn_run_app.setObjectName("SuccessButton")
        self.btn_run_app.setCursor(Qt.PointingHandCursor)
        self.btn_run_app.setEnabled(False)
        self.btn_run_app.clicked.connect(self.run_built_app)
        sub_actions.addWidget(self.btn_run_app)

        self.btn_open_folder = QPushButton("باز کردن پوشه مقصد")
        self.btn_open_folder.setObjectName("SecondaryButton")
        self.btn_open_folder.setCursor(Qt.PointingHandCursor)
        self.btn_open_folder.setEnabled(False)
        self.btn_open_folder.clicked.connect(self.open_output_folder)
        sub_actions.addWidget(self.btn_open_folder)

        self.btn_cancel = QPushButton("توقف فرآیند")
        self.btn_cancel.setObjectName("DangerButton")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_build)
        sub_actions.addWidget(self.btn_cancel)

        action_layout.addLayout(sub_actions)
        build_col.addLayout(action_layout)

        main_columns.addLayout(build_col, stretch=45)

        # === COLUMN 2 (Right): Project Settings ===
        config_col = QVBoxLayout()
        config_col.setSpacing(12)

        self.platform_selector = PlatformSelectorWidget(initial_platform=self.config.platform)
        self.platform_selector.platform_changed.connect(self.on_platform_changed)
        config_col.addWidget(self.platform_selector)

        self.drop_zone = DropZoneWidget()
        self.drop_zone.source_selected.connect(self.on_source_selected)
        config_col.addWidget(self.drop_zone)

        self.desktop_panel = DesktopPanel()
        self.desktop_panel.config_changed.connect(self.on_config_changed)
        config_col.addWidget(self.desktop_panel)

        self.android_panel = AndroidPanel()
        self.android_panel.config_changed.connect(self.on_config_changed)
        self.android_panel.hide()
        config_col.addWidget(self.android_panel)

        self.path_selector = PathSelectorWidget()
        self.path_selector.output_dir_changed.connect(self.on_output_dir_changed)
        config_col.addWidget(self.path_selector)

        config_col.addStretch()
        main_columns.addLayout(config_col, stretch=55)

        root_layout.addLayout(main_columns, stretch=1)

        # 3. Footer Status Bar
        footer_bar = self.create_footer_status_bar()
        root_layout.addWidget(footer_bar)

    def create_header(self) -> QWidget:
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 4)

        ver_lbl = QLabel("v1.0.0")
        ver_lbl.setStyleSheet("color: #8b949e; font-size: 11px; background: #161b22; border: 1px solid #30363d; border-radius: 4px; padding: 2px 6px;")
        h_layout.addWidget(ver_lbl)

        h_layout.addStretch()

        title_box = QHBoxLayout()
        title_box.setSpacing(8)

        sub_title = QLabel("سامانه ساخت فایل‌های نصبی ویندوز و اندروید")
        sub_title.setStyleSheet("font-size: 11px; color: #8b949e;")

        title_lbl = QLabel("AppForge Studio")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #f0f6fc;")

        title_box.addWidget(sub_title)
        title_box.addWidget(title_lbl)
        h_layout.addLayout(title_box)

        return header

    def create_footer_status_bar(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("FooterStatusBar")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(12, 6, 12, 6)
        f_layout.setSpacing(18)

        self.status_pyinstaller = QLabel("موتور ویندوز: در حال بررسی...")
        self.status_pyinstaller.setStyleSheet("font-size: 11px; color: #8b949e;")

        self.status_wsl = QLabel("موتور اندروید: در حال بررسی...")
        self.status_wsl.setStyleSheet("font-size: 11px; color: #8b949e;")

        f_layout.addWidget(self.status_pyinstaller)
        f_layout.addWidget(self.status_wsl)
        f_layout.addStretch()

        self.btn_check_update = QPushButton(f"v{CURRENT_VERSION} (بررسی بروزرسانی)")
        self.btn_check_update.setCursor(Qt.PointingHandCursor)
        self.btn_check_update.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #58a6ff;
                font-size: 11px;
                text-decoration: underline;
                padding: 0 4px;
            }
            QPushButton:hover {
                color: #79c0ff;
            }
        """)
        self.btn_check_update.clicked.connect(lambda: self.check_updates(manual=True))
        f_layout.addWidget(self.btn_check_update)

        ready_hint = QLabel("AppForge Packaging Engine")
        ready_hint.setStyleSheet("font-size: 11px; color: #484f58;")
        f_layout.addWidget(ready_hint)

        return footer

    def check_updates(self, manual: bool = False):
        if self.update_thread and self.update_thread.isRunning():
            return
            
        if manual:
            self.terminal.append_log("در حال بررسی نسخه جدید در مخزن گیت‌هاب...", "info")
            
        self.update_thread = UpdateCheckerWorker()
        
        def on_update(info):
            self.update_banner.display_update(info)
            self.terminal.append_log(f"نسخه جدید {info.get('version')} در گیت‌هاب یافت شد!", "success")
            if manual:
                dlg = UpdateDialog(info, self)
                dlg.exec()
                
        def on_latest(version):
            if manual:
                QMessageBox.information(
                    self,
                    "بروزرسانی AppForge",
                    f"شما از آخرین نسخه پایدار نرم‌افزار (نسخه {version}) استفاده می‌کنید."
                )
                self.terminal.append_log(f"نسخه فعلی ({version}) آخرین نسخه موجود در گیت‌هاب است.", "info")
                
        def on_err(err_msg):
            if manual:
                self.terminal.append_log(f"خطا در اتصال به گیت‌هاب: {err_msg}", "warn")
                
        self.update_thread.update_found.connect(on_update)
        self.update_thread.up_to_date.connect(on_latest)
        self.update_thread.check_error.connect(on_err)
        self.update_thread.start()

    def check_environment_status(self):
        env = check_system_environment()
        
        if env["desktop"]["pyinstaller"]:
            self.status_pyinstaller.setText("● موتور ویندوز (PyInstaller): فعال")
            self.status_pyinstaller.setStyleSheet("font-size: 11px; color: #3fb950; font-weight: 500;")
        else:
            self.status_pyinstaller.setText("○ موتور ویندوز: غیرفعال")
            self.status_pyinstaller.setStyleSheet("font-size: 11px; color: #f85149;")

        if env["android"]["wsl_ubuntu"]:
            self.status_wsl.setText("● موتور اندروید (WSL Ubuntu): آماده")
            self.status_wsl.setStyleSheet("font-size: 11px; color: #3fb950; font-weight: 500;")
        else:
            self.status_wsl.setText("▲ موتور اندروید: نیازمند تنظیم")
            self.status_wsl.setStyleSheet("font-size: 11px; color: #d29922;")

    def on_platform_changed(self, platform: PlatformType):
        self.config.platform = platform
        if platform == PlatformType.DESKTOP:
            self.desktop_panel.show()
            self.android_panel.hide()
            self.btn_build.setText("شروع ساخت فایل نصبی ویندوز")
        else:
            self.desktop_panel.hide()
            self.android_panel.show()
            self.btn_build.setText("شروع ساخت فایل نصبی اندروید")

        self.update_path_preview()

    def on_source_selected(self, source_dir: str, entry_point: str):
        self.config.source_dir = source_dir
        self.config.entry_point = entry_point
        
        # 1. Try loading existing project preset
        loaded_preset = self.config.load_project_preset(source_dir)
        if loaded_preset:
            self.desktop_panel.load_from_config(self.config)
            self.terminal.append_log("پیکربندی ذخیره‌شده پروژه (appforge.json) با موفقیت بازیابی شد.", "success")
        else:
            suggested_name = os.path.basename(source_dir).capitalize()
            if suggested_name:
                self.desktop_panel.txt_app_name.setText(suggested_name)
                self.android_panel.txt_app_name.setText(suggested_name)
                self.android_panel.txt_package_name.setText(suggested_name.lower())

        # 2. Trigger auto-detection of asset directories
        self.desktop_panel.set_source_directory(source_dir)

        self.update_path_preview()
        self.terminal.append_log(f"پروژه تنظیم شد: \u200E{source_dir}\u200E (فایل: \u200E{entry_point}\u200E)", "info")

    def on_output_dir_changed(self, output_dir: str):
        self.config.output_dir = output_dir

    def on_config_changed(self):
        self.update_path_preview()

    def update_path_preview(self):
        if self.config.platform == PlatformType.DESKTOP:
            settings = self.desktop_panel.get_settings()
            app_name = settings["app_name"]
        else:
            settings = self.android_panel.get_settings()
            app_name = settings["app_name"]
            
        self.path_selector.set_app_info(app_name, self.config.platform)

    def sync_config(self):
        self.config.output_dir = self.path_selector.get_output_dir()
        
        if self.config.platform == PlatformType.DESKTOP:
            settings = self.desktop_panel.get_settings()
            self.config.app_name = settings["app_name"]
            self.config.app_version = settings["version"]
            self.config.company_name = settings.get("company_name", "")
            self.config.file_description = settings.get("file_description", "")
            self.config.add_data = settings.get("add_data", [])
            self.config.icon_path = settings["icon_path"]
            self.config.auto_install_deps = settings.get("auto_install_deps", True)
            self.config.onefile = settings["onefile"]
            self.config.windowed = settings["windowed"]
            self.config.clean_build = settings["clean"]
            self.config.auto_hidden_imports = settings.get("auto_hidden_imports", True)
            self.config.enable_smoke_test = settings.get("enable_smoke_test", True)
            self.config.generate_installer = settings.get("generate_installer", True)
            self.config.desktop_extra_args = settings["extra_args"]
        else:
            settings = self.android_panel.get_settings()
            self.config.app_name = settings["app_name"]
            self.config.app_version = settings["version"]
            self.config.package_domain = settings["package_domain"]
            self.config.package_name = settings["package_name"]
            self.config.orientation = settings["orientation"]
            self.config.permissions = settings["permissions"]
            self.config.android_requirements = settings["requirements"]
            self.config.auto_install_deps = settings.get("auto_install_deps", True)
            self.config.icon_path = settings["icon_path"]

    def start_build(self):
        self.sync_config()
        
        errors = self.config.validate()
        if errors:
            QMessageBox.warning(self, "خطا در ورودی‌ها", "\n".join(errors))
            return

        self.btn_build.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_run_app.setEnabled(False)
        self.btn_open_folder.setEnabled(False)
        self.terminal.clear_logs()

        if self.config.platform == PlatformType.DESKTOP:
            self.active_worker = DesktopBuildWorker(self.config)
        else:
            self.active_worker = AndroidBuildWorker(self.config)

        self.active_worker.log_received.connect(self.terminal.append_log)
        self.active_worker.progress_updated.connect(self.terminal.set_progress)
        self.active_worker.build_finished.connect(self.on_build_finished)
        self.active_worker.start()

    def cancel_build(self):
        if self.active_worker and self.active_worker.isRunning():
            self.active_worker.cancel()
            self.btn_cancel.setEnabled(False)

    def on_build_finished(self, success: bool, result_path_or_msg: str):
        self.btn_build.setEnabled(True)
        self.btn_cancel.setEnabled(False)

        if success:
            self.last_built_file = result_path_or_msg
            self.btn_open_folder.setEnabled(True)
            
            # Enable Quick Run App for Desktop Windows Executables
            if result_path_or_msg.lower().endswith(".exe"):
                self.btn_run_app.setEnabled(True)
                
            QMessageBox.information(
                self,
                "ساخت موفقیت‌آمیز",
                f"فایل نصبی با موفقیت آماده و ذخیره شد:\n\n{result_path_or_msg}"
            )
        else:
            QMessageBox.critical(
                self,
                "خطا در ساخت فایل نصبی",
                f"فرآیند ساخت با خطا مواجه شد:\n\n{result_path_or_msg}"
            )

    def run_built_app(self):
        """Launches the built application executable immediately"""
        if self.last_built_file and os.path.exists(self.last_built_file) and self.last_built_file.lower().endswith(".exe"):
            try:
                work_dir = os.path.dirname(self.last_built_file)
                subprocess.Popen([self.last_built_file], cwd=work_dir)
                self.terminal.append_log(f"برنامه با موفقیت اجرا شد: \u200E{self.last_built_file}\u200E", "success")
            except Exception as e:
                QMessageBox.critical(self, "خطا در اجرای برنامه", f"امکان اجرای فایل وجود ندارد: {e}")

    def open_output_folder(self):
        path = self.last_built_file or self.path_selector.get_output_dir()
        if path and os.path.exists(path):
            open_in_file_manager(path)

    def closeEvent(self, event):
        if self.update_thread and self.update_thread.isRunning():
            self.update_thread.wait(500)
        if self.active_worker and self.active_worker.isRunning():
            self.active_worker.cancel()
            self.active_worker.wait(1000)
        event.accept()
