import os
import json
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Optional

class PlatformType(str, Enum):
    DESKTOP = "desktop"
    ANDROID = "android"

@dataclass
class ProjectConfig:
    platform: PlatformType = PlatformType.DESKTOP
    source_dir: str = ""
    entry_point: str = ""
    app_name: str = "MyApp"
    app_version: str = "1.0.0"
    output_dir: str = ""
    icon_path: Optional[str] = None
    
    # Auto-Dependency Resolution
    auto_install_deps: bool = True
    
    # Commercial Metadata
    company_name: str = ""
    file_description: str = ""
    copyright_str: str = ""
    
    # Assets & Data Bundling
    add_data: List[str] = field(default_factory=list)
    
    # Desktop Settings (PyInstaller)
    onefile: bool = True
    windowed: bool = True
    clean_build: bool = True
    desktop_extra_args: str = ""
    
    # Runtime Guarantees
    auto_hidden_imports: bool = True
    enable_smoke_test: bool = True
    generate_installer: bool = True
    
    # Android Settings (Buildozer / Python-for-Android)
    package_domain: str = "org.example"
    package_name: str = "myapp"
    orientation: str = "portrait"
    permissions: List[str] = field(default_factory=lambda: ["INTERNET"])
    android_requirements: List[str] = field(default_factory=lambda: ["python3", "kivy"])
    android_extra_args: str = ""

    def validate(self) -> List[str]:
        errors = []
        if not self.source_dir or not os.path.exists(self.source_dir):
            errors.append("پوشه یا فایل سورس کد مشخص نشده یا وجود ندارد.")
        if not self.entry_point:
            errors.append("فایل اجرایی اصلی (مانند main.py) انتخاب نشده است.")
        if not self.app_name.strip():
            errors.append("نام برنامه نباید خالی باشد.")
        if not self.output_dir:
            errors.append("مسیر ذخیره‌سازی فایل نصبی خروجی مشخص نشده است.")
        elif not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"امکان ساخت پوشه خروجی وجود ندارد: {str(e)}")
        
        if self.icon_path and not os.path.exists(self.icon_path):
            errors.append("فایل آیکون انتخاب‌شده یافت نشد.")
            
        return errors

    def save_project_preset(self, directory: str = "") -> bool:
        """Saves current settings into appforge.json inside project source folder"""
        target_dir = directory or self.source_dir
        if not target_dir or not os.path.isdir(target_dir):
            return False
            
        cfg_file = os.path.join(target_dir, "appforge.json")
        try:
            data = asdict(self)
            data["platform"] = self.platform.value
            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load_project_preset(self, directory: str) -> bool:
        """Loads settings from appforge.json if present in the selected folder"""
        cfg_file = os.path.join(directory, "appforge.json")
        if not os.path.exists(cfg_file):
            return False
            
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for key, val in data.items():
                if key == "platform":
                    self.platform = PlatformType(val)
                elif hasattr(self, key):
                    setattr(self, key, val)
            return True
        except Exception:
            return False
