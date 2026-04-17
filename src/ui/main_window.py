# src/ui/main_window.py
import os
import subprocess
import webbrowser
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QCursor

# Импортируем наши модули (убедись, что пути в main.py настроены верно)
from src.ui.settings_panel import SettingsPanel
from src.utils.localization import LANG
from src.utils.updater import UpdateChecker


class OmniZServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # --- Системные параметры ---
        self.current_lang = "ru"
        self.APP_VERSION = "0.1"
        self.is_running = False
        self.server_process = None
        self.time_left = 0
        self.settings_open = False

        # --- Настройки окна ---
        self.setFixedSize(480, 600)
        self.setWindowTitle("OmniZ Server")

        # Глобальный стиль: жесткие цвета для защиты от темной темы Windows
        self.setStyleSheet("""
            QMainWindow { background-color: #F8F9FA; }
            QLabel { color: #333333; font-family: 'Inter'; }
            QToolTip { 
                background-color: #2C2F33; 
                color: #FFFFFF; 
                border: 1px solid #555; 
                border-radius: 4px; 
                padding: 6px; 
                font-family: 'Inter';
            }
        """)

        self.init_ui()
        self.update_texts()

        # Таймер для обратного отсчета
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.tick_timer)

        # Запуск фоновой проверки обновлений
        self.check_for_updates()

    def init_ui(self):
        # Главный контейнер без Layout (для ручного позиционирования)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # --- ГЛАВНЫЙ ЭКРАН (Левая часть, 480x600) ---
        self.main_screen = QWidget(self.central_widget)
        self.main_screen.setGeometry(0, 0, 480, 600)
        ms_layout = QVBoxLayout(self.main_screen)
        ms_layout.setContentsMargins(20, 20, 20, 20)

        # Верхняя панель (Заголовок, Язык, Шестеренка)
        top_bar = QHBoxLayout()
        self.title_lbl = QLabel("OmniZ Server")
        self.title_lbl.setFont(QFont("Inter", 18, QFont.Weight.Bold))

        self.lang_cb = QComboBox()
        self.lang_cb.addItems(["🇷🇺 Русский", "🇺🇸 English"])
        self.lang_cb.setFixedSize(115, 32)
        self.lang_cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.lang_cb.setStyleSheet("""
            QComboBox { border: 1px solid #ccc; border-radius: 4px; padding-left: 8px; background: white; color: #333333; font-size: 10pt; }
            QComboBox QAbstractItemView { background-color: white; color: #333333; selection-background-color: #E0E0E0; }
        """)
        self.lang_cb.currentIndexChanged.connect(self.change_language)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_btn.setStyleSheet(
            "border: none; font-size: 18pt; color: #333333; background: transparent;"
        )
        self.settings_btn.clicked.connect(self.toggle_settings)

        top_bar.addWidget(self.title_lbl)
        top_bar.addStretch()
        top_bar.addWidget(self.lang_cb)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.settings_btn)
        ms_layout.addLayout(top_bar)

        ms_layout.addStretch()

        # Статус сервера
        self.status_lbl = QLabel()
        self.status_lbl.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ms_layout.addWidget(self.status_lbl)

        ms_layout.addSpacing(40)

        # Блок кнопок
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton()
        self.start_btn.setFixedSize(160, 48)
        self.start_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.start_btn.clicked.connect(self.toggle_server)

        self.restart_btn = QPushButton()
        self.restart_btn.setFixedSize(160, 48)
        self.restart_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.restart_btn.setStyleSheet(
            "background-color: #F0AD4E; color: white; font-size: 16pt; font-weight: 600; border-radius: 24px;"
        )
        self.restart_btn.clicked.connect(self.restart_server)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.restart_btn)
        ms_layout.addLayout(btn_layout)

        ms_layout.addSpacing(10)

        # Таймер
        self.timer_lbl = QLabel()
        self.timer_lbl.setFont(QFont("Inter", 10))
        self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_lbl.setStyleSheet("color: #555555;")
        ms_layout.addWidget(self.timer_lbl)

        ms_layout.addStretch()

        # Версия
        self.version_lbl = QLabel(f"v.{self.APP_VERSION}")
        self.version_lbl.setStyleSheet("color: gray;")
        ms_layout.addWidget(self.version_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        # --- ОКНО НАСТРОЕК (Правая часть, 400x600) ---
        # Изначально находится на X=480 (спрятано за правой границей)
        self.settings_panel = SettingsPanel(self.central_widget)
        self.settings_panel.setGeometry(480, 0, 400, 600)

    # ================= ЛОГИКА СЕРВЕРА =================

    def toggle_server(self):
        if not self.is_running:
            exe_path = self.settings_panel.path_input.text().strip()

            if not exe_path or not os.path.exists(exe_path):
                msg = (
                    "Укажите путь к DayZServer_x64.exe!"
                    if self.current_lang == "ru"
                    else "Specify path to DayZServer_x64.exe!"
                )
                QMessageBox.warning(self, "Ошибка", msg)
                return

            params_text = self.settings_panel.cfg_input.toPlainText()
            params_list = [p.strip() for p in params_text.split("\n") if p.strip()]

            try:
                self.server_process = subprocess.Popen([exe_path] + params_list)
                self.is_running = True

                restart_seconds = self.settings_panel.get_restart_seconds()
                if restart_seconds > 0:
                    self.time_left = restart_seconds
                    self.countdown_timer.start(1000)
                else:
                    self.time_left = 0
                    self.countdown_timer.stop()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start: {e}")
                return
        else:
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            self.is_running = False
            self.countdown_timer.stop()
            self.time_left = 0

        self.update_texts()

    def restart_server(self):
        if self.is_running:
            self.toggle_server()
            QTimer.singleShot(1500, self.toggle_server)

    def tick_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            h, m, s = (
                self.time_left // 3600,
                (self.time_left % 3600) // 60,
                self.time_left % 60,
            )
            prefix = LANG[self.current_lang]["timer_prefix"]
            self.timer_lbl.setText(f"{prefix}{h:02d}:{m:02d}:{s:02d}")
        else:
            self.restart_server()

    # ================= СИСТЕМА ОБНОВЛЕНИЙ =================

    def check_for_updates(self):
        # Замените на реальный URL вашего version.json на GitHub
        url = "https://gist.githubusercontent.com/username/gist_id/raw/version.json"
        self.updater = UpdateChecker(self.APP_VERSION, url)
        self.updater.update_available.connect(self.show_update_dialog)
        self.updater.start()

    def show_update_dialog(self, new_ver, url, changelog):
        lang = LANG[self.current_lang]
        msg = lang["update_msg"].format(
            new_ver=new_ver, curr_ver=self.APP_VERSION, changelog=changelog
        )

        box = QMessageBox(self)
        box.setWindowTitle(lang["update_title"])
        box.setText(msg)
        box.setStyleSheet("QLabel { color: #333; }")
        btn_yes = box.addButton(lang["btn_yes"], QMessageBox.ButtonRole.AcceptRole)
        box.addButton(lang["btn_no"], QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() == btn_yes:
            webbrowser.open(url)

    # ================= ИНТЕРФЕЙС =================

    def toggle_settings(self):
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        geo = self.geometry()
        if not self.settings_open:
            self.anim.setEndValue(QRect(geo.x(), geo.y(), 880, 600))
            self.settings_btn.setStyleSheet(
                "border: none; font-size: 18pt; color: #007BFF; background: transparent;"
            )
            self.settings_open = True
        else:
            self.anim.setEndValue(QRect(geo.x(), geo.y(), 480, 600))
            self.settings_btn.setStyleSheet(
                "border: none; font-size: 18pt; color: #333333; background: transparent;"
            )
            self.settings_open = False
            # --- НОВОЕ: Мгновенно сохраняем данные при скрытии панели! ---
            self.settings_panel.save_settings()

        self.anim.finished.connect(lambda: self.setFixedSize(self.width(), 600))
        self.anim.start()

    def update_texts(self):
        lang = LANG[self.current_lang]
        self.restart_btn.setText(lang["restart"])

        if self.is_running:
            self.status_lbl.setText(lang["status_on"])
            self.status_lbl.setStyleSheet("color: #5CB85C;")
            self.start_btn.setText(lang["stop"])
            self.start_btn.setStyleSheet(
                "background-color: #D9534F; color: white; font-size: 16pt; font-weight: 600; border-radius: 24px;"
            )
            if self.time_left == 0:
                self.timer_lbl.setText(lang["timer_prefix"] + "OFF")
        else:
            self.status_lbl.setText(lang["status_off"])
            self.status_lbl.setStyleSheet("color: #D9534F;")
            self.start_btn.setText(lang["start"])
            self.start_btn.setStyleSheet(
                "background-color: #5CB85C; color: white; font-size: 16pt; font-weight: 600; border-radius: 24px;"
            )
            self.timer_lbl.setText(lang["timer_prefix"] + "00:00:00")

        self.settings_panel.update_texts(self.current_lang)

    def change_language(self, index):
        self.current_lang = "ru" if index == 0 else "en"
        self.update_texts()

    def closeEvent(self, a0):
        """Срабатывает при закрытии окна"""
        # Страховочное сохранение
        self.settings_panel.save_settings()

        # Убиваем сервер при выходе, чтобы он не остался висеть в памяти
        if self.is_running and self.server_process:
            self.server_process.terminate()

        if a0:
            a0.accept()  # Разрешаем окну закрыться
