# src/ui/settings_panel.py
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
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        self.title_lbl = QLabel()
        self.title_lbl.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        layout.addWidget(self.title_lbl)

        layout.addSpacing(20)

        # Поле пути к файлу + кнопка "Обзор"
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

        # Кнопки авторестарта
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

        # --- НОВОЕ: Заголовок "Параметры запуска" + Иконка подсказки ---
        cfg_header_layout = QHBoxLayout()
        self.cfg_lbl = QLabel()
        self.cfg_lbl.setFont(QFont("Inter", 11, QFont.Weight.Medium))

        self.cfg_hint = QLabel("❔")
        self.cfg_hint.setCursor(
            QCursor(Qt.CursorShape.WhatsThisCursor)
        )  # Курсор с вопросиком
        self.cfg_hint.setStyleSheet(
            "color: #007BFF; font-size: 11pt; border: none; background: transparent;"
        )

        cfg_header_layout.addWidget(self.cfg_lbl)
        cfg_header_layout.addWidget(self.cfg_hint)
        cfg_header_layout.addStretch()
        layout.addLayout(cfg_header_layout)

        # --- Поле ввода с дефолтными параметрами ---
        self.cfg_input = QTextEdit()
        self.cfg_input.setStyleSheet(
            "border: 1px solid #CCC; border-radius: 4px; padding: 10px; font-family: Consolas, monospace; background: white; color: black; font-size: 9pt;"
        )

        # Предзаполняем стандартными параметрами
        default_cfg = (
            "-config=serverDZ.cfg\n"
            "-port=2302\n"
            "-profiles=profiles\n"
            "-cpuCount=4\n"
            "-doLogs\n"
            "-adminLog\n"
            "-freezeCheck\n"
            "-mod=\n"
            "-serverMod="
        )
        self.cfg_input.setPlainText(default_cfg)

        layout.addWidget(self.cfg_input)

    def update_texts(self, current_lang):
        lang = LANG[current_lang]
        self.title_lbl.setText(lang["settings_title"])
        self.path_input.setPlaceholderText(lang["path_placeholder"])
        self.browse_btn.setText(lang["browse"])
        self.ar_lbl.setText(lang["auto_restart"])
        self.cfg_lbl.setText(lang["launch_cfg"])
        # Применяем текст подсказки из словаря
        self.cfg_hint.setToolTip(lang["cfg_tooltip"])

        suffix = "ч" if current_lang == "ru" else "h"
        time_values = [3, 6, 12]
        for i, btn in enumerate(self.ar_btns):
            btn.setText(f"{time_values[i]}{suffix}")

    def on_ar_btn_clicked(self, clicked_btn):
        for btn in self.ar_btns:
            if btn != clicked_btn:
                btn.setChecked(False)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите исполняемый файл сервера",
            "",
            "Executable Files (*.exe);;All Files (*)",
        )
        if file_name:
            self.path_input.setText(file_name)

    def get_restart_seconds(self):
        """Возвращает выбранное время авторестарта в секундах"""
        time_values = [3, 6, 12]
        for i, btn in enumerate(self.ar_btns):
            if btn.isChecked():
                return time_values[i] * 3600  # Переводим часы в секунды
        return 0  # Если ничего не выбрано (таймер выключен)
