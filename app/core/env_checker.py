import subprocess
import shutil
import sys
import os
from typing import Dict, Any

def check_system_environment() -> Dict[str, Any]:
    """Checks tools required for Desktop (.exe) and Android (.apk) packaging"""
    status = {
        "desktop": {
            "pyinstaller": False,
            "python_version": sys.version.split()[0],
            "details": ""
        },
        "android": {
            "wsl_installed": False,
            "wsl_ubuntu": False,
            "buildozer_in_wsl": False,
            "details": ""
        }
    }

    # 1. Desktop Check (PyInstaller)
    try:
        import PyInstaller
        status["desktop"]["pyinstaller"] = True
        status["desktop"]["details"] = f"PyInstaller نسخه {PyInstaller.__version__} آماده به کار است."
    except ImportError:
        status["desktop"]["pyinstaller"] = False
        status["desktop"]["details"] = "PyInstaller نصب نیست. با اجرای pip install pyinstaller نصب کنید."

    # 2. Android Check (WSL)
    try:
        wsl_res = subprocess.run(["wsl", "--status"], capture_output=True, text=True, timeout=5)
        if wsl_res.returncode == 0:
            status["android"]["wsl_installed"] = True
            
            # Check Ubuntu distro
            list_res = subprocess.run(["wsl", "-l", "-v"], capture_output=True, text=True, timeout=5)
            if "Ubuntu" in list_res.stdout or "ubuntu" in list_res.stdout:
                status["android"]["wsl_ubuntu"] = True
                
                # Check Buildozer inside WSL
                bd_res = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", "command -v buildozer"], capture_output=True, text=True, timeout=5)
                if bd_res.stdout.strip():
                    status["android"]["buildozer_in_wsl"] = True
                    status["android"]["details"] = "محیط لینوکس WSL و ابزار Buildozer برای ساخت APK کاملاً آماده است."
                else:
                    status["android"]["details"] = "محیط لینوکس WSL Ubuntu آماده است (ابزار Buildozer در صورت نیاز به طور خودکار نصب می‌شود)."
            else:
                status["android"]["details"] = "توزیع لینوکس Ubuntu در WSL یافت نشد."
        else:
            status["android"]["details"] = "زیرسیستم WSL 2 در ویندوز فعال نیست."
    except Exception as e:
        status["android"]["details"] = f"خطا در بررسی WSL: {str(e)}"

    return status
