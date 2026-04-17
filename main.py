# main.py
import sys
import os

# Жестко указываем Питону, где искать наши модули (папку src)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "src"))

from PyQt6.QtWidgets import QApplication
from ui.main_window import OmniZServerWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OmniZServerWindow()
    window.show()
    sys.exit(app.exec())
