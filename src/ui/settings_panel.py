# src/ui/settings_panel.py
import os
import json
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt
from src.utils.localization import LANG


class SettingsPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 600)
        self.setStyleSheet("""
            SettingsPanel { background-color: #FFFFFF; border-left: 1px solid #E0E0E0; }
            QLabel { color: #333333; }
        """)

        # --- Настройка путей AppData ---
        appdata_path = os.getenv("APPDATA") or os.path.expanduser("~")  # Путь к Roaming
        self.config_dir = os.path.join(appdata_path, "OmniZ_Server")
        self.config_file = os.path.join(self.config_dir, "config.json")

        # Создаем папку, если её нет
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        self.title_lbl = QLabel()
        self.title_lbl.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        layout.addWidget(self.title_lbl)

        layout.addSpacing(20)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setFixedSize(240, 36)
        self.path_input.setStyleSheet(
            "border: 1px solid #CCC; border-radius: 4px; padding: 0 8px; font-size: 10pt; background: white; color: black;"
        )

        self.browse_btn = QPushButton()
        self.browse_btn.setFixedSize(80, 36)
        self.browse_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.browse_btn.setStyleSheet(
            "background-color: #F0F0F0; border: 1px solid #CCC; border-radius: 4px; font-weight: bold; color: #333333;"
        )
        self.browse_btn.clicked.connect(self.browse_file)

        path_layout.addWidget(self.path_input)
        path_layout.addSpacing(10)
        path_layout.addWidget(self.browse_btn)
        path_layout.addStretch()
        layout.addLayout(path_layout)

        layout.addSpacing(20)

        self.ar_lbl = QLabel()
        self.ar_lbl.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        layout.addWidget(self.ar_lbl)

        ar_layout = QHBoxLayout()
        self.ar_btns = []
        for hours in [3, 6, 12]:
            btn = QPushButton()
            btn.setFixedSize(50, 36)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton { background-color: #F0F0F0; border-radius: 18px; border: none; font-weight: bold; color: #333333; }
                QPushButton:checked { background-color: #007BFF; color: white; }
            """)
            btn.clicked.connect(lambda checked, b=btn: self.on_ar_btn_clicked(b))
            self.ar_btns.append(btn)
            ar_layout.addWidget(btn)
        ar_layout.addStretch()
        layout.addLayout(ar_layout)

        layout.addSpacing(20)

        cfg_header_layout = QHBoxLayout()
        self.cfg_lbl = QLabel()
        self.cfg_lbl.setFont(QFont("Inter", 11, QFont.Weight.Medium))

        self.cfg_hint = QLabel("❔")
        self.cfg_hint.setCursor(QCursor(Qt.CursorShape.WhatsThisCursor))
        self.cfg_hint.setStyleSheet(
            "color: #007BFF; font-size: 11pt; border: none; background: transparent;"
        )

        cfg_header_layout.addWidget(self.cfg_lbl)
        cfg_header_layout.addWidget(self.cfg_hint)
        cfg_header_layout.addStretch()
        layout.addLayout(cfg_header_layout)

        self.cfg_input = QTextEdit()
        self.cfg_input.setStyleSheet(
            "border: 1px solid #CCC; border-radius: 4px; padding: 10px; font-family: Consolas, monospace; background: white; color: black; font-size: 9pt;"
        )
        layout.addWidget(self.cfg_input)

    # ================= ЛОГИКА СОХРАНЕНИЯ В APPDATA =================

    def load_settings(self):
        """Загрузка данных из JSON в папке AppData"""
        default_cfg = (
            "-config=serverDZ.cfg\n-port=2302\n-profiles=profiles\n"
            "-cpuCount=4\n-doLogs\n-adminLog\n-freezeCheck\n-mod=\n-serverMod="
        )

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.path_input.setText(data.get("exe_path", ""))
                    self.cfg_input.setPlainText(data.get("launch_params", default_cfg))

                    saved_hours = data.get("auto_restart_hours", 0)
                    time_values = [3, 6, 12]
                    for i, btn in enumerate(self.ar_btns):
                        btn.setChecked(time_values[i] == saved_hours)
                return
            except Exception as e:
                print(f"Error loading config: {e}")

        # Если файла нет, ставим дефолт
        self.cfg_input.setPlainText(default_cfg)

    def save_settings(self):
        """Сохранение данных в JSON в папку AppData"""
        saved_hours = 0
        for i, btn in enumerate(self.ar_btns):
            if btn.isChecked():
                saved_hours = [3, 6, 12][i]
                break

        data = {
            "exe_path": self.path_input.text().strip(),
            "launch_params": self.cfg_input.toPlainText().strip(),
            "auto_restart_hours": saved_hours,
        }

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    # ================= ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =================

    def update_texts(self, current_lang):
        lang = LANG[current_lang]
        self.title_lbl.setText(lang["settings_title"])
        self.path_input.setPlaceholderText(lang["path_placeholder"])
        self.browse_btn.setText(lang["browse"])
        self.ar_lbl.setText(lang["auto_restart"])
        self.cfg_lbl.setText(lang["launch_cfg"])
        self.cfg_hint.setToolTip(lang["cfg_tooltip"])
        suffix = "ч" if current_lang == "ru" else "h"
        for i, btn in enumerate(self.ar_btns):
            btn.setText(f"{[3, 6, 12][i]}{suffix}")

    def on_ar_btn_clicked(self, clicked_btn):
        for btn in self.ar_btns:
            if btn != clicked_btn:
                btn.setChecked(False)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Выберите EXE", "", "EXE (*.exe)"
        )
        if file_name:
            self.path_input.setText(file_name)

    def get_restart_seconds(self):
        for i, btn in enumerate(self.ar_btns):
            if btn.isChecked():
                return [3, 6, 12][i] * 3600
        return 0
