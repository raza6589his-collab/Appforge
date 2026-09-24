import os
import sys
import shutil
import tempfile
import subprocess
from .base_worker import BaseBuildWorker
from ..utils.file_utils import (
    ensure_ico_format, generate_version_file,
    detect_hidden_imports, generate_inno_setup_script, compile_inno_setup_script
)

class DesktopBuildWorker(BaseBuildWorker):
    """Handles packaging Python source code into a Windows Desktop Executable (.exe)"""
    
    def run(self):
        config = self.config
        
        # 1. Validation
        source_dir = os.path.abspath(config.source_dir)
        entry_file = os.path.join(source_dir, config.entry_point) if not os.path.isabs(config.entry_point) else config.entry_point
        
        if not os.path.exists(entry_file):
            self.log_received.emit(f"فایل نقطه ورود یافت نشد: {entry_file}", "error")
            self.build_finished.emit(False, f"فایل اصلی یافت نشد: {entry_file}")
            return
            
        output_dir = os.path.abspath(config.output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # 2. Phase 1: Auto-Install Dependencies (if enabled)
        if config.auto_install_deps:
            self.progress_updated.emit(15)
            ok = self.install_desktop_dependencies(source_dir, entry_file)
            if not ok or self._is_cancelled:
                return

        # 3. Phase 2: Build Desktop Installer (.exe)
        self.log_received.emit("=== فاز ۲: ساخت فایل نصبی مستقل ویندوز (PyInstaller) ===", "info")
        self.progress_updated.emit(35)
        
        # Temp build directories
        temp_work = os.path.join(tempfile.gettempdir(), f"appforge_build_{config.app_name}")
        temp_spec = os.path.join(tempfile.gettempdir(), f"appforge_spec_{config.app_name}")
        os.makedirs(temp_work, exist_ok=True)
        os.makedirs(temp_spec, exist_ok=True)
        
        # Icon Handling
        icon_arg = []
        converted_ico = None
        if config.icon_path and os.path.exists(config.icon_path):
            temp_ico = os.path.join(tempfile.gettempdir(), f"{config.app_name}_icon.ico")
            converted_ico = ensure_ico_format(config.icon_path, temp_ico)
            if converted_ico and os.path.exists(converted_ico):
                icon_arg = [f"--icon={converted_ico}"]
                self.log_received.emit(f"آیکون با وضوح چندگانه آماده شد: {converted_ico}", "info")

        # Windows File Metadata & Version Stamp
        version_arg = []
        try:
            ver_file_path = os.path.join(temp_spec, "version_info.txt")
            generate_version_file(
                ver_file_path,
                app_name=config.app_name,
                version=config.app_version,
                company_name=config.company_name,
                file_description=config.file_description,
                copyright_str=config.copyright_str
            )
            version_arg = [f"--version-file={ver_file_path}"]
            self.log_received.emit("شناسنامه و مشخصات نسخه ویندوز با موفقیت تولید شد.", "info")
        except Exception as e:
            self.log_received.emit(f"هشدار در ایجاد فایل مشخصات نسخه: {e}", "warn")
        
        self.progress_updated.emit(45)
        
        # Assemble PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            f"--name={config.app_name}",
            f"--distpath={output_dir}",
            f"--workpath={temp_work}",
            f"--specpath={temp_spec}",
            "--noconfirm",
        ]
        
        if config.clean_build:
            cmd.append("--clean")
            
        if config.onefile:
            cmd.append("--onefile")
        else:
            cmd.append("--onedir")
            
        if config.windowed:
            cmd.append("--windowed")
            
        cmd.extend(icon_arg)
        cmd.extend(version_arg)
        cmd.append(f"--paths={source_dir}")
        
        # Add bundled assets and data files (--add-data)
        if config.add_data:
            for item in config.add_data:
                if not item.strip():
                    continue
                parts = item.split(";") if ";" in item else [item, os.path.basename(item)]
                src = parts[0].strip()
                dst = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                full_src = os.path.join(source_dir, src) if not os.path.isabs(src) else src
                if os.path.exists(full_src):
                    cmd.append(f"--add-data={full_src};{dst}")
                    self.log_received.emit(f"بسته‌بندی فایل/پوشه جانبی: {src} -> {dst}", "info")
        
        # Smart Hidden Imports Detection
        if config.auto_hidden_imports:
            hidden_flags = detect_hidden_imports(source_dir)
            if hidden_flags:
                cmd.extend(hidden_flags)
                self.log_received.emit(f"شناسایی هوشمند وابستگی‌های پنهان ({len(hidden_flags)} دستور): {' '.join(hidden_flags)}", "info")

        if config.desktop_extra_args.strip():
            cmd.extend(config.desktop_extra_args.strip().split())
            
        cmd.append(entry_file)
        
        self.progress_updated.emit(55)
        self.log_received.emit(f"دستور بیلد: {' '.join(cmd)}", "info")
        
        # Execute build command
        ret_code = self.run_command(cmd, cwd=source_dir)
        
        if self._is_cancelled:
            return
            
        self.progress_updated.emit(85)
        
        # Verify result
        if ret_code == 0:
            if config.onefile:
                target_exe = os.path.join(output_dir, f"{config.app_name}.exe")
            else:
                target_exe = os.path.join(output_dir, config.app_name, f"{config.app_name}.exe")
                
            if os.path.exists(target_exe):
                # Also save preset in source dir
                config.save_project_preset()
                self.log_received.emit("ساخت فایل نصبی با موفقیت به پایان رسید.", "success")
                self.log_received.emit(f"مسیر نهایی: {target_exe}", "success")

                # Generate Inno Setup Script
                if config.generate_installer:
                    try:
                        self.log_received.emit("در حال تولید اسکریپت نصاب ویندوز (Inno Setup)...", "info")
                        iss_file = generate_inno_setup_script(
                            app_name=config.app_name,
                            version=config.app_version,
                            company_name=config.company_name,
                            exe_path=target_exe,
                            output_dir=output_dir,
                            icon_path=converted_ico or config.icon_path
                        )
                        self.log_received.emit(f"اسکریپت نصاب رسمی آماده شد: {os.path.basename(iss_file)}", "success")
                        compiled_setup = compile_inno_setup_script(iss_file)
                        if compiled_setup:
                            self.log_received.emit("کامپایل خودکار نصاب Setup.exe با موفقیت انجام شد!", "success")
                    except Exception as e:
                        self.log_received.emit(f"هشدار در تولید اسکریپت نصاب: {e}", "warn")

                # Pre-flight Smoke Test
                if config.enable_smoke_test:
                    self.perform_smoke_test(target_exe)

                self.progress_updated.emit(100)
                self.build_finished.emit(True, target_exe)
            else:
                self.log_received.emit(f"فایل اجرایی در مسیر مورد نظر یافت نشد. خروجی را بررسی کنید: {output_dir}", "warn")
                self.build_finished.emit(True, output_dir)
        else:
            self.progress_updated.emit(0)
            self.log_received.emit(f"فرآیند ساخت با کد خطای {ret_code} متوقف شد.", "error")
            self.build_finished.emit(False, f"کد خروج غیرعادی: {ret_code}")
            
        # Clean temporary dirs
        try:
            shutil.rmtree(temp_work, ignore_errors=True)
            shutil.rmtree(temp_spec, ignore_errors=True)
        except Exception:
            pass

    def perform_smoke_test(self, exe_path: str):
        """Runs the compiled executable briefly to verify it does not crash on launch"""
        self.log_received.emit("=== فاز ۳: تست سلامت زنده اولیه (Pre-flight Smoke Test) ===", "info")
        self.log_received.emit("در حال تست باز شدن اولیه برنامه جهت تایید سلامت اجرای ماژول‌ها...", "info")
        try:
            proc = subprocess.Popen(
                [exe_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            try:
                stdout, stderr = proc.communicate(timeout=2.5)
                if proc.returncode != 0:
                    self.log_received.emit(f"⚠️ اخطار: برنامه پس از باز شدن متوقف شد (کد خروج: {proc.returncode})", "warn")
                    err_msg = stderr.strip() or stdout.strip()
                    if err_msg:
                        self.log_received.emit(f"خطای دریافتی:\n{err_msg}", "error")
                        if "ModuleNotFoundError" in err_msg or "ImportError" in err_msg:
                            self.log_received.emit("راهنما: یکی از ماژول‌ها در بسته موجود نیست. فیلد دستورات جانبی را بررسی کنید.", "warn")
                else:
                    self.log_received.emit("✅ تست اولیه موفق: برنامه بدون خطا اجرا شد (کد خروج: ۰).", "success")
            except subprocess.TimeoutExpired:
                # App was still running after 2.5s (healthy GUI event loop)
                proc.terminate()
                try:
                    proc.wait(timeout=1.0)
                except Exception:
                    proc.kill()
                self.log_received.emit("✅ تست سلامت زنده موفق: برنامه گرافیکی بدون کرش لود شد و آماده استفاده است.", "success")
        except Exception as e:
            self.log_received.emit(f"عدم امکان اجرای تست خودکار: {e}", "warn")
