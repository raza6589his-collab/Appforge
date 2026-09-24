import os
import shutil
import glob
import subprocess
from .base_worker import BaseBuildWorker

def win_to_wsl_path(win_path: str) -> str:
    """Converts Windows path like F:\\Mimo code to /mnt/f/Mimo code"""
    abs_path = os.path.abspath(win_path).replace("\\", "/")
    if len(abs_path) >= 2 and abs_path[1] == ":":
        drive = abs_path[0].lower()
        rest = abs_path[2:]
        return f"/mnt/{drive}{rest}"
    return abs_path

class AndroidBuildWorker(BaseBuildWorker):
    """Handles packaging source code into an Android APK using WSL & Buildozer"""

    def run(self):
        config = self.config

        source_dir = os.path.abspath(config.source_dir)
        output_dir = os.path.abspath(config.output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # 1. Check WSL availability
        self.log_received.emit("در حال بررسی زیرسیستم لینوکس (WSL 2 Ubuntu)...", "info")
        try:
            wsl_check = subprocess.run(["wsl", "--status"], capture_output=True, text=True, timeout=5)
            if wsl_check.returncode != 0:
                self.log_received.emit("زیرسیستم WSL در ویندوز فعال نیست یا به درستی پیکربندی نشده است.", "error")
                self.build_finished.emit(False, "سرویس WSL در دسترس نیست.")
                return
        except Exception as e:
            self.log_received.emit(f"خطا در ارتباط با WSL: {str(e)}", "error")
            self.build_finished.emit(False, "امکان ارتباط با WSL وجود ندارد.")
            return

        # 2. Phase 1: Auto-Install Android Tools & Project Dependencies (if enabled)
        if config.auto_install_deps:
            self.progress_updated.emit(15)
            ok = self.install_android_dependencies(source_dir)
            if not ok or self._is_cancelled:
                return

        # 3. Phase 2: Configure & Build Android APK
        self.log_received.emit("=== فاز ۲: ساخت فایل نصبی اندروید (Buildozer) ===", "info")
        self.progress_updated.emit(30)

        spec_path = os.path.join(source_dir, "buildozer.spec")
        self.log_received.emit("پیکربندی فایل تنظیمات buildozer.spec...", "info")
        self.create_or_update_spec(spec_path, config)

        self.progress_updated.emit(40)

        # Translate paths to WSL
        wsl_source = win_to_wsl_path(source_dir)
        self.log_received.emit(f"مسیر سورس در محیط لینوکس: {wsl_source}", "info")

        # Run buildozer android debug
        self.log_received.emit("در حال کامپایل پروژه و ساخت فایل APK در محیط WSL...", "info")
        build_cmd = [
            "wsl", "-d", "Ubuntu", "--", "bash", "-c",
            f"cd '{wsl_source}' && buildozer android debug"
        ]

        ret_code = self.run_command(build_cmd)

        if self._is_cancelled:
            return

        self.progress_updated.emit(85)

        # Locate output APK in bin/ folder
        bin_dir = os.path.join(source_dir, "bin")
        apk_files = glob.glob(os.path.join(bin_dir, "*.apk"))

        if apk_files:
            latest_apk = max(apk_files, key=os.path.getmtime)
            apk_filename = os.path.basename(latest_apk)
            dest_apk = os.path.join(output_dir, apk_filename)
            
            # Copy to user-defined output directory
            try:
                shutil.copy2(latest_apk, dest_apk)
                self.progress_updated.emit(100)
                self.log_received.emit("فایل نصبی APK با موفقیت ساخته و ذخیره شد.", "success")
                self.log_received.emit(f"مسیر نهایی APK: {dest_apk}", "success")
                self.build_finished.emit(True, dest_apk)
            except Exception as e:
                self.log_received.emit(f"فایل در {latest_apk} ساخته شد اما انتقال به مقصد با خطا مواجه شد: {e}", "warn")
                self.build_finished.emit(True, latest_apk)
        else:
            if ret_code == 0:
                self.log_received.emit("فرآیند به پایان رسید اما فایل APK در پوشه bin یافت نشد.", "warn")
                self.build_finished.emit(False, "فایل APK یافت نشد.")
            else:
                self.progress_updated.emit(0)
                self.log_received.emit(f"ساخت APK با کد خطای {ret_code} متوقف شد. لاگ‌ها را بررسی کنید.", "error")
                self.build_finished.emit(False, f"خطای بیلد با کد {ret_code}")

    def create_or_update_spec(self, spec_path: str, config):
        """Generates a complete buildozer.spec file customized to user settings"""
        reqs = ",".join(config.android_requirements) if config.android_requirements else "python3,kivy"
        perms = ",".join(config.permissions) if config.permissions else "INTERNET"

        icon_directive = ""
        if config.icon_path and os.path.exists(config.icon_path):
            icon_name = os.path.basename(config.icon_path)
            dest_icon = os.path.join(config.source_dir, icon_name)
            if os.path.abspath(config.icon_path) != os.path.abspath(dest_icon):
                try:
                    shutil.copy2(config.icon_path, dest_icon)
                except Exception:
                    pass
            icon_directive = f"icon.filename = %(source.dir)s/{icon_name}"

        spec_content = f"""[app]
title = {config.app_name}
package.name = {config.package_name}
package.domain = {config.package_domain}
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,html,css,js
version = {config.app_version}
requirements = {reqs}
orientation = {config.orientation}
android.permissions = {perms}
{icon_directive}
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
"""
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(spec_content)
        self.log_received.emit("فایل buildozer.spec با موفقیت ساخته شد.", "info")
