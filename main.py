import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.gui.main_window import MainWindow

def main():
    # Set Windows Process ID to show custom taskbar icon properly
    if os.name == 'nt':
        try:
            myappid = 'appforge.studio.packaging.engine.v1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Enable High DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("AppForge")
    app.setOrganizationName("AppForge Studio")

    # Load custom icon if available in assets
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_candidates = [
        os.path.join(base_dir, "app", "assets", "app_icon.ico"),
        os.path.join(base_dir, "app", "assets", "app_icon.png")
    ]
    for ic in icon_candidates:
        if os.path.exists(ic):
            app_icon = QIcon(ic)
            app.setWindowIcon(app_icon)
            break
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
