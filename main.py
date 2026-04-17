# main.py
import sys
from PyQt6.QtWidgets import QApplication

# Указываем полный путь начиная с папки src
from src.ui.main_window import OmniZServerWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OmniZServerWindow()
    window.show()
    sys.exit(app.exec())
