import os
import subprocess
import sys
from typing import Optional, Dict, Any, List
from PIL import Image

def detect_entry_point(directory: str) -> Optional[str]:
    """Finds common entry files like main.py, app.py, run.py, or any primary .py file"""
    if not os.path.exists(directory):
        return None
        
    if os.path.isfile(directory):
        return os.path.basename(directory)
        
    candidates = ["main.py", "app.py", "run.py", "index.py", "gui.py", "window.py"]
    for c in candidates:
        full = os.path.join(directory, c)
        if os.path.exists(full):
            return c
            
    # Fallback: first python file in root
    try:
        files = os.listdir(directory)
        py_files = [f for f in files if f.endswith(".py") and not f.startswith("__")]
        if py_files:
            return py_files[0]
    except Exception:
        pass
        
    return None

def detect_asset_folders(directory: str) -> List[str]:
    """Scans project directory for common asset folders (assets, static, templates, images, data, etc.)"""
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return []
        
    common_names = {
        "assets", "static", "templates", "images", "img", "icons",
        "data", "resources", "res", "fonts", "locales", "db", "ui"
    }
    
    found = []
    try:
        for entry in os.scandir(directory):
            if entry.is_dir() and entry.name.lower() in common_names:
                found.append(entry.name)
    except Exception:
        pass
        
    return sorted(found)

def open_in_file_manager(path: str):
    """Opens the directory in Windows Explorer and selects the file if a file is given."""
    if not os.path.exists(path):
        return
        
    if os.name == 'nt':
        if os.path.isfile(path):
            subprocess.run(f'explorer /select,"{os.path.abspath(path)}"', shell=True)
        else:
            subprocess.run(f'explorer "{os.path.abspath(path)}"', shell=True)
    elif sys.platform == 'darwin':
        subprocess.run(['open', '-R', path])
    else:
        subprocess.run(['xdg-open', os.path.dirname(path) if os.path.isfile(path) else path])

def ensure_ico_format(image_path: str, output_ico_path: str) -> Optional[str]:
    """Converts any standard image (PNG/JPG/WEBP) to a high-quality multi-resolution .ico for Windows"""
    if not image_path or not os.path.exists(image_path):
        return None
        
    if image_path.lower().endswith('.ico'):
        return image_path
        
    try:
        img = Image.open(image_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(output_ico_path, format='ICO', sizes=icon_sizes)
        return output_ico_path
    except Exception as e:
        print(f"Icon conversion error: {e}")
        return None

def get_image_info(image_path: str) -> Optional[Dict[str, Any]]:
    """Inspects an image file and returns format, dimensions and file size"""
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with Image.open(image_path) as img:
            file_bytes = os.path.getsize(image_path)
            return {
                "format": img.format or "IMG",
                "width": img.width,
                "height": img.height,
                "size_str": format_file_size(file_bytes)
            }
    except Exception:
        return None

def generate_version_file(
    output_path: str,
    app_name: str,
    version: str,
    company_name: str = "",
    file_description: str = "",
    copyright_str: str = ""
) -> str:
    """Generates a standard Windows VS_VERSION_INFO file for PyInstaller to stamp onto .exe binaries"""
    # Parse version tuple e.g. "1.2.3" -> (1, 2, 3, 0)
    parts = []
    for p in version.split('.'):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 4:
        parts.append(0)
    v_tuple = tuple(parts[:4])
    
    comp = company_name or "Independent Developer"
    desc = file_description or f"{app_name} Application"
    cprt = copyright_str or f"Copyright © 2026 {comp}"

    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={v_tuple},
    prodvers={v_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', '{comp}'),
        StringStruct('FileDescription', '{desc}'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', '{app_name}'),
        StringStruct('LegalCopyright', '{cprt}'),
        StringStruct('OriginalFilename', '{app_name}.exe'),
        StringStruct('ProductName', '{app_name}'),
        StringStruct('ProductVersion', '{version}')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path

def format_file_size(size_bytes: int) -> str:
    """Formats file size to human readable string"""
    if size_bytes == 0:
        return "0 B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    p = float(size_bytes)
    while p >= 1024 and i < len(size_names) - 1:
        p /= 1024.0
        i += 1
    return f"{p:.1f} {size_names[i]}"

RESOURCE_PATH_HELPER_CODE = """# تابع استاندارد دسترسی امن به فایل‌ها و مدیا (در سورس‌کد و فایل نصبی EXE)
import os
import sys

def get_resource_path(relative_path: str) -> str:
    \"\"\"مسیر امن فایل را بازمی‌گرداند؛ با پشتیبانی کامل از پوشه موقت PyInstaller\"\"\"
    try:
        # در حالت تک‌فایلی EXE، پای‌اینستالر فایل‌ها را در _MEIPASS باز می‌کند
        base_path = sys._MEIPASS
    except AttributeError:
        # در حالت اجرای مستقیم سورس‌کد
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# نمونه استفاده:
# icon_path = get_resource_path("assets/icon.png")
# db_path = get_resource_path("data/database.sqlite")
"""

def detect_hidden_imports(directory: str) -> List[str]:
    """Scans all python files in directory and returns needed PyInstaller flags for complex libraries"""
    if not os.path.exists(directory):
        return []
        
    known_rules = {
        "customtkinter": ["--collect-all=customtkinter"],
        "requests": ["--hidden-import=urllib3", "--hidden-import=certifi", "--hidden-import=charset_normalizer", "--hidden-import=idna"],
        "pil": ["--hidden-import=PIL._tkinter_finder"],
        "pillow": ["--hidden-import=PIL._tkinter_finder"],
        "uvicorn": ["--collect-all=uvicorn"],
        "fastapi": ["--collect-all=fastapi", "--collect-all=uvicorn"],
        "sqlalchemy": ["--collect-all=sqlalchemy"],
        "matplotlib": ["--collect-all=matplotlib"],
        "pandas": ["--collect-all=pandas"],
        "pygame": ["--collect-all=pygame"],
        "pydantic": ["--collect-all=pydantic"],
        "rich": ["--collect-all=rich"],
        "cryptography": ["--collect-all=cryptography"],
        "cv2": ["--collect-all=cv2"],
        "scipy": ["--collect-all=scipy"],
        "docx": ["--collect-all=docx"],
        "openpyxl": ["--collect-all=openpyxl"],
        "httpx": ["--collect-all=httpx"],
        "playwright": ["--collect-all=playwright"],
        "selenium": ["--collect-all=selenium"],
        "flask": ["--collect-all=flask"],
        "engineio": ["--collect-all=engineio"],
        "socketio": ["--collect-all=socketio"],
        "dotenv": ["--hidden-import=dotenv"],
    }
    
    found_flags = set()
    
    # Scan directory
    if os.path.isfile(directory):
        files_to_scan = [directory]
    else:
        files_to_scan = []
        for root, _, files in os.walk(directory):
            for f in files:
                if f.endswith(".py"):
                    files_to_scan.append(os.path.join(root, f))
                    
    for file_path in files_to_scan:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
                for lib, flags in known_rules.items():
                    if f"import {lib}" in content or f"from {lib}" in content:
                        for flg in flags:
                            found_flags.add(flg)
        except Exception:
            continue
            
    return sorted(list(found_flags))

def generate_inno_setup_script(
    app_name: str,
    version: str,
    company_name: str,
    exe_path: str,
    output_dir: str,
    icon_path: Optional[str] = None
) -> str:
    """Generates an Inno Setup 6 (.iss) script for creating a real Windows Setup Wizard"""
    exe_filename = os.path.basename(exe_path)
    comp = company_name or "Independent Developer"
    iss_filename = f"setup_{app_name}.iss"
    iss_path = os.path.join(output_dir, iss_filename)
    
    icon_line = ""
    if icon_path and os.path.exists(icon_path):
        icon_line = f'SetupIconFile={os.path.abspath(icon_path)}'
        
    content = f"""; Inno Setup Script generated by AppForge Studio
[Setup]
AppId={{{{{app_name}-{comp}}}}}
AppName={app_name}
AppVersion={version}
AppPublisher={comp}
DefaultDirName={{autopf}}\\{app_name}
DefaultGroupName={app_name}
DisableProgramGroupPage=yes
OutputDir={os.path.abspath(output_dir)}
OutputBaseFilename=Setup_{app_name}_{version}
{icon_line}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "{os.path.abspath(exe_path)}"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{autoprograms}}\\{app_name}"; Filename: "{{app}}\\{exe_filename}"
Name: "{{autodesktop}}\\{app_name}"; Filename: "{{app}}\\{exe_filename}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{exe_filename}"; Description: "{{cm:LaunchProgram,{app_name}}}"; Flags: nowait postinstall skipifsilent
"""
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return iss_path

def compile_inno_setup_script(iss_path: str) -> Optional[str]:
    """Tries to find ISCC.exe and compile the Inno Setup script into Setup.exe"""
    candidates = [
        "iscc",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    iscc_bin = None
    for cand in candidates:
        try:
            res = subprocess.run([cand, "/?"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            if res.returncode == 0 or "Inno Setup" in res.stdout or "Inno Setup" in res.stderr:
                iscc_bin = cand
                break
        except Exception:
            continue
            
    if not iscc_bin:
        return None
        
    try:
        res = subprocess.run([iscc_bin, iss_path], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        if res.returncode == 0:
            return iss_path
    except Exception:
        pass
        
    return None

