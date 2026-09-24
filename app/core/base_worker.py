import os
import sys
import subprocess
import ast
import importlib.util
from typing import List, Set
from PySide6.QtCore import QThread, Signal

class BaseBuildWorker(QThread):
    """Base QThread for running packaging commands with real-time log streaming"""
    log_received = Signal(str, str)     # (message, level: "info" | "warn" | "error" | "success")
    progress_updated = Signal(int)       # (0 to 100)
    build_finished = Signal(bool, str)   # (success, message_or_filepath)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._is_cancelled = False
        self.process = None

    def cancel(self):
        self._is_cancelled = True
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
        self.log_received.emit("عملیات ساخت توسط کاربر متوقف شد.", "warn")
        self.build_finished.emit(False, "عملیات متوقف شد.")

    def run_command(self, cmd, cwd=None, env=None) -> int:
        """Runs a subprocess and yields stdout line by line to UI"""
        cmd_str = ' '.join(cmd) if isinstance(cmd, list) else cmd
        self.log_received.emit(f"> {cmd_str}", "info")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                env=env
            )

            for line in iter(self.process.stdout.readline, ''):
                if self._is_cancelled:
                    break
                clean_line = line.rstrip()
                if clean_line:
                    level = "info"
                    lower = clean_line.lower()
                    if "error" in lower or "fatal" in lower or "failed" in lower:
                        level = "error"
                    elif "warn" in lower or "warning" in lower:
                        level = "warn"
                    elif "successfully" in lower or "completed" in lower or "installed" in lower:
                        level = "success"
                        
                    self.log_received.emit(clean_line, level)

            self.process.stdout.close()
            return_code = self.process.wait()
            return return_code
        except Exception as e:
            self.log_received.emit(f"خطا در اجرای فرآیند: {str(e)}", "error")
            return -1

    def install_desktop_dependencies(self, source_dir: str, entry_file: str) -> bool:
        """Phase 1: Automatically verifies and installs all project and build dependencies"""
        self.log_received.emit("=== فاز ۱: بررسی و نصب پیش‌نیازها و بسته‌های پایتون ===", "info")
        
        # 1. Ensure PyInstaller is installed
        if importlib.util.find_spec("PyInstaller") is None:
            self.log_received.emit("ابزار PyInstaller بر روی سیستم نصب نیست. در حال نصب خودکار...", "warn")
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"]
            code = self.run_command(cmd)
            if code != 0:
                self.log_received.emit("خطا در نصب PyInstaller.", "error")
                return False

        # 2. Check for requirements.txt in project directory
        req_file = os.path.join(source_dir, "requirements.txt")
        if os.path.exists(req_file):
            self.log_received.emit(f"فایل نیازمندی‌ها شناسایی شد: {req_file}", "info")
            self.log_received.emit("در حال نصب بسته‌های موجود در requirements.txt...", "info")
            cmd = [sys.executable, "-m", "pip", "install", "-r", req_file]
            code = self.run_command(cmd, cwd=source_dir)
            if code != 0:
                self.log_received.emit("هشدار: برخی بسته‌ها در requirements.txt با خطا مواجه شدند، ادامه فرآیند بررسی می‌شود...", "warn")
            else:
                self.log_received.emit("تمامی بسته‌های requirements.txt با موفقیت نصب شدند.", "success")
        else:
            # Auto-detect imports from entry script if no requirements.txt
            if os.path.exists(entry_file):
                self.log_received.emit("در حال اسکن سورس‌کد جهت شناسایی کتابخانه‌های ایمپورت شده...", "info")
                missing_pkgs = self.detect_missing_imports(entry_file)
                if missing_pkgs:
                    self.log_received.emit(f"کتابخانه‌های نصب‌نشده شناسایی شدند: {', '.join(missing_pkgs)}", "warn")
                    for pkg in missing_pkgs:
                        if self._is_cancelled:
                            return False
                        self.log_received.emit(f"در حال نصب خودکار بسته: {pkg}...", "info")
                        cmd = [sys.executable, "-m", "pip", "install", pkg]
                        self.run_command(cmd)
                else:
                    self.log_received.emit("تمام ماژول‌های ایمپورت‌شده در سیستم حاضر هستند.", "success")

        self.log_received.emit("پیش‌نیازها آماده شدند. ورود به فاز ساخت فایل نصبی...", "success")
        return True

    def detect_missing_imports(self, script_path: str) -> Set[str]:
        """Parses Python file AST to find third-party modules that are not installed"""
        missing = set()
        try:
            with open(script_path, "r", encoding="utf-8", errors="replace") as f:
                root = ast.parse(f.read(), filename=script_path)
            
            imported_modules = set()
            for node in ast.walk(root):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_modules.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_modules.add(node.module.split('.')[0])

            # Filter out standard library modules
            stdlib_names = getattr(sys, "stdlib_module_names", set())
            for mod in imported_modules:
                if mod in stdlib_names or mod.startswith("_"):
                    continue
                # Check if it is importable
                if importlib.util.find_spec(mod) is None:
                    missing.add(mod)
        except Exception as e:
            self.log_received.emit(f"خطای جزیی در اسکن کدهای پایتون: {e}", "warn")
        return missing

    def install_android_dependencies(self, source_dir: str) -> bool:
        """Phase 1 for Android: Ensures WSL tools and dependencies are prepared"""
        self.log_received.emit("=== فاز ۱: بررسی و نصب پیش‌نیازهای محیط اندروید در WSL ===", "info")

        # 1. Check Buildozer in WSL
        check_bd = ["wsl", "-d", "Ubuntu", "--", "bash", "-c", "command -v buildozer"]
        res = subprocess.run(check_bd, capture_output=True, text=True)
        if not res.stdout.strip():
            self.log_received.emit("ابزار Buildozer در توزیع Ubuntu نصب نیست. در حال نصب خودکار...", "warn")
            install_cmd = [
                "wsl", "-d", "Ubuntu", "--", "bash", "-c",
                "pip3 install --upgrade buildozer cython virtualenv"
            ]
            self.run_command(install_cmd)

        # 2. Sync requirements.txt with config requirements if present
        req_file = os.path.join(source_dir, "requirements.txt")
        if os.path.exists(req_file):
            try:
                with open(req_file, "r", encoding="utf-8", errors="replace") as f:
                    lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                for pkg in lines:
                    pkg_clean = pkg.split("==")[0].split(">=")[0].split("<=")[0].strip()
                    if pkg_clean and pkg_clean not in self.config.android_requirements:
                        self.config.android_requirements.append(pkg_clean)
                self.log_received.emit(f"بسته‌های سورس‌کد به تنظیمات اندروید اضافه شدند: {', '.join(self.config.android_requirements)}", "info")
            except Exception as e:
                self.log_received.emit(f"خطا در خواندن requirements.txt: {e}", "warn")

        self.log_received.emit("پیش‌نیازهای محیط اندروید آماده شدند.", "success")
        return True
