import os
import sys
import tempfile
import unittest
from PIL import Image

# Ensure UTF-8 output encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from app.config import ProjectConfig, PlatformType
from app.utils.file_utils import (
    detect_entry_point, format_file_size,
    ensure_ico_format, get_image_info,
    detect_asset_folders, generate_version_file
)
from app.core.env_checker import check_system_environment
from app.core.desktop_builder import DesktopBuildWorker

class TestAppForge(unittest.TestCase):
    def test_environment_check(self):
        env = check_system_environment()
        self.assertIn("desktop", env)
        self.assertIn("android", env)
        self.assertTrue(env["desktop"]["pyinstaller"])
        print("Environment check passed successfully.")

    def test_config_validation(self):
        cfg = ProjectConfig()
        errors = cfg.validate()
        self.assertTrue(len(errors) > 0, "Empty config should fail validation")

        with tempfile.TemporaryDirectory() as tmp_dir:
            main_file = os.path.join(tmp_dir, "main.py")
            with open(main_file, "w", encoding="utf-8") as f:
                f.write("print('hello')\n")
            
            cfg.source_dir = tmp_dir
            cfg.entry_point = "main.py"
            cfg.app_name = "SampleTestApp"
            cfg.output_dir = tmp_dir
            
            val_errors = cfg.validate()
            self.assertEqual(len(val_errors), 0, f"Config should be valid: {val_errors}")

    def test_detect_entry_point(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            app_file = os.path.join(tmp_dir, "app.py")
            with open(app_file, "w", encoding="utf-8") as f:
                f.write("# sample app")
            
            entry = detect_entry_point(tmp_dir)
            self.assertEqual(entry, "app.py")

    def test_asset_detection_and_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create subfolders
            os.makedirs(os.path.join(tmp_dir, "assets"), exist_ok=True)
            os.makedirs(os.path.join(tmp_dir, "static"), exist_ok=True)
            os.makedirs(os.path.join(tmp_dir, "other_folder"), exist_ok=True)

            detected = detect_asset_folders(tmp_dir)
            self.assertIn("assets", detected)
            self.assertIn("static", detected)
            self.assertNotIn("other_folder", detected)

            # Test Windows version file generation
            ver_path = os.path.join(tmp_dir, "version_info.txt")
            generate_version_file(
                ver_path,
                app_name="TestApp",
                version="2.1.0",
                company_name="Acme Corp",
                file_description="My Great Software",
                copyright_str="© 2026 Acme Corp"
            )
            self.assertTrue(os.path.exists(ver_path))
            with open(ver_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Acme Corp", content)
                self.assertIn("2.1.0", content)
            print("Asset detection and version file tests passed.")

    def test_project_preset_save_load(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg = ProjectConfig()
            cfg.source_dir = tmp_dir
            cfg.app_name = "SavedPresetApp"
            cfg.company_name = "StarTech"
            cfg.app_version = "3.0.0"
            cfg.add_data = ["assets;assets"]

            saved = cfg.save_project_preset()
            self.assertTrue(saved)
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, "appforge.json")))

            # Load into fresh config
            cfg2 = ProjectConfig()
            loaded = cfg2.load_project_preset(tmp_dir)
            self.assertTrue(loaded)
            self.assertEqual(cfg2.app_name, "SavedPresetApp")
            self.assertEqual(cfg2.company_name, "StarTech")
            self.assertEqual(cfg2.add_data, ["assets;assets"])
            print("Preset save/load tests passed.")

    def test_icon_upload_and_conversion(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            png_path = os.path.join(tmp_dir, "test_logo.png")
            img = Image.new("RGBA", (128, 128), color=(30, 144, 255, 255))
            img.save(png_path, format="PNG")

            info = get_image_info(png_path)
            self.assertIsNotNone(info)
            self.assertEqual(info["width"], 128)
            self.assertEqual(info["height"], 128)
            self.assertEqual(info["format"], "PNG")

            ico_path = os.path.join(tmp_dir, "output_icon.ico")
            converted = ensure_ico_format(png_path, ico_path)
            self.assertIsNotNone(converted)
            self.assertTrue(os.path.exists(converted))
            print(f"Icon converted successfully to: {converted} (Size: {format_file_size(os.path.getsize(converted))})")

    def test_desktop_build_execution(self):
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as out_dir:
            # Create script and an asset folder
            script_path = os.path.join(src_dir, "demo.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write("import sys\nprint('AppForge Test Exe Run!')\nsys.exit(0)\n")

            asset_dir = os.path.join(src_dir, "assets")
            os.makedirs(asset_dir, exist_ok=True)
            with open(os.path.join(asset_dir, "info.txt"), "w") as f:
                f.write("sample asset")

            cfg = ProjectConfig()
            cfg.platform = PlatformType.DESKTOP
            cfg.source_dir = src_dir
            cfg.entry_point = "demo.py"
            cfg.app_name = "QuickTestApp"
            cfg.company_name = "MyBrand"
            cfg.file_description = "Built with AppForge"
            cfg.output_dir = out_dir
            cfg.add_data = ["assets;assets"]
            cfg.auto_install_deps = False
            cfg.onefile = True
            cfg.windowed = False
            cfg.clean_build = True
            cfg.auto_hidden_imports = True
            cfg.enable_smoke_test = True
            cfg.generate_installer = True

            worker = DesktopBuildWorker(cfg)
            results = []
            worker.build_finished.connect(lambda success, path: results.append((success, path)))
            
            # Run synchronously for testing
            worker.run()

            self.assertTrue(len(results) > 0)
            success, final_path = results[0]
            self.assertTrue(success, f"Build failed: {final_path}")
            self.assertTrue(os.path.exists(final_path), f"Output exe not found at: {final_path}")
            
            # Verify Inno Setup script was generated
            iss_file = os.path.join(out_dir, f"setup_{cfg.app_name}.iss")
            self.assertTrue(os.path.exists(iss_file), f"Inno setup script not found at {iss_file}")
            print(f"Generated test executable: {final_path} (Size: {format_file_size(os.path.getsize(final_path))})")
            print(f"Generated Inno Setup script: {iss_file}")

    def test_runtime_guarantees_tools(self):
        from app.utils.file_utils import detect_hidden_imports, generate_inno_setup_script
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. Test Hidden Imports Detection
            code_file = os.path.join(tmp_dir, "test_code.py")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write("import requests\nfrom PIL import Image\nimport customtkinter as ctk\n")

            flags = detect_hidden_imports(tmp_dir)
            self.assertTrue(any("customtkinter" in flg for flg in flags))
            self.assertTrue(any("urllib3" in flg for flg in flags))
            self.assertTrue(any("PIL" in flg for flg in flags))

            # 2. Test Inno Setup Script Generation
            fake_exe = os.path.join(tmp_dir, "TestApp.exe")
            with open(fake_exe, "w") as f:
                f.write("dummy binary")

            iss = generate_inno_setup_script(
                app_name="TestApp",
                version="1.0.0",
                company_name="Innovate Corp",
                exe_path=fake_exe,
                output_dir=tmp_dir
            )
            self.assertTrue(os.path.exists(iss))
            with open(iss, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("AppName=TestApp", content)
                self.assertIn("AppPublisher=Innovate Corp", content)
                self.assertIn("lzma2/ultra64", content)
            print("Runtime guarantee tools (Hidden imports & Inno Setup) passed.")

    def test_update_checker_logic(self):
        from app.core.update_checker import parse_version
        self.assertEqual(parse_version("v1.0.0"), (1, 0, 0))
        self.assertEqual(parse_version("1.2.3"), (1, 2, 3))
        self.assertEqual(parse_version("v2.1"), (2, 1, 0))
        self.assertTrue(parse_version("1.0.1") > parse_version("1.0.0"))
        self.assertTrue(parse_version("2.0.0") > parse_version("1.9.9"))
        self.assertFalse(parse_version("1.0.0") > parse_version("1.0.0"))
        print("Update checker version parsing tests passed.")

if __name__ == "__main__":
    unittest.main()


