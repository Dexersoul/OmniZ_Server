# src/ui/main_window.py
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
    QLayout,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QCursor, QCloseEvent

from src.services.server_service import (
    ServerService,
    ServerServiceError,
    EmptyExecutablePathError,
    ExecutableNotFoundError,
    ExecutableIsDirectoryError,
    InvalidExecutableTypeError,
    UnexpectedExecutableNameError,
    ServerAlreadyRunningError,
    ServerNotRunningError,
    ServerStartError,
    ServerStopError,
)
from src.services.settings_service import SettingsService
from src.ui.settings_panel import SettingsPanel
from src.utils.localization import LANG
from src.utils.updater import UpdateChecker


class OmniZServerWindow(QMainWindow):
    APP_VERSION = "0.1"
    UPDATE_INFO_URL = ""
    STATUS_POLL_MS = 1000

    def __init__(self):
        super().__init__()

        self.current_lang = "ru"
        self.time_left = 0
        self.settings_open = False
        self._last_running_state = False

        self.server_service = ServerService()
        self.settings_service = SettingsService()

        self.setFixedSize(480, 600)
        self.setWindowTitle("OmniZ Server")

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
        self.load_settings_into_ui()

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.tick_timer)

        self.state_timer = QTimer(self)
        self.state_timer.timeout.connect(self.sync_server_state)
        self.state_timer.start(self.STATUS_POLL_MS)

        self.sync_server_state(force=True)
        self.check_for_updates()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_screen = QWidget(self.central_widget)
        self.main_screen.setGeometry(0, 0, 480, 600)

        ms_layout = QVBoxLayout(self.main_screen)
        ms_layout.setContentsMargins(20, 20, 20, 20)

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

        self.status_lbl = QLabel()
        self.status_lbl.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ms_layout.addWidget(self.status_lbl)

        ms_layout.addSpacing(40)

        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton()
        self.start_btn.setFixedSize(160, 48)
        self.start_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.start_btn.clicked.connect(self.toggle_server)

        self.restart_btn = QPushButton()
        self.restart_btn.setFixedSize(160, 48)
        self.restart_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0AD4E;
                color: white;
                font-size: 16pt;
                font-weight: 600;
                border-radius: 24px;
            }
            QPushButton:disabled {
                background-color: #D9D9D9;
                color: #888888;
            }
        """)
        self.restart_btn.clicked.connect(self.restart_server)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addSpacing(10)
        btn_layout.addWidget(self.restart_btn)

        ms_layout.addLayout(btn_layout)
        ms_layout.addSpacing(10)

        self.timer_lbl = QLabel()
        self.timer_lbl.setFont(QFont("Inter", 10))
        self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_lbl.setStyleSheet("color: #555555;")
        ms_layout.addWidget(self.timer_lbl)

        ms_layout.addStretch()

        self.version_lbl = QLabel(f"v.{self.APP_VERSION}")
        self.version_lbl.setStyleSheet("color: gray;")
        ms_layout.addWidget(self.version_lbl, alignment=Qt.AlignmentFlag.AlignLeft)

        self.settings_panel = SettingsPanel(self.central_widget)
        self.settings_panel.setGeometry(480, 0, 400, 600)

    def load_settings_into_ui(self):
        settings_data = self.settings_service.load_settings()
        self.settings_panel.set_form_data(settings_data)

    def save_settings_from_ui(self):
        settings_data = self.settings_panel.get_form_data()
        self.settings_service.save_settings(settings_data)

    def get_current_form_data(self):
        return self.settings_panel.get_form_data()

    def get_launch_params_list(self, launch_params_text):
        return [
            line.strip() for line in launch_params_text.splitlines() if line.strip()
        ]

    def create_message_box(self, icon, title, text):
        box = QMessageBox(self)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setText(text)

        box.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel#qt_msgbox_label {
                color: #222222;
                font-size: 10pt;
                min-width: 0px;
                max-width: 360px;
            }
            QMessageBox QLabel#qt_msgboxex_icon_label {
                min-width: 32px;
                min-height: 32px;
            }
            QMessageBox QPushButton {
                min-width: 90px;
                padding: 6px 12px;
                background-color: #F0F0F0;
                border: 1px solid #CFCFCF;
                border-radius: 6px;
                color: #222222;
            }
            QMessageBox QPushButton:hover {
                background-color: #E7E7E7;
            }
            QMessageBox QPushButton:pressed {
                background-color: #DCDCDC;
            }
        """)

        text_label = box.findChild(QLabel, "qt_msgbox_label")
        if text_label is not None:
            text_label.setWordWrap(True)
            text_label.setMinimumWidth(0)
            text_label.setMaximumWidth(360)

        layout = box.layout()
        if layout is not None:
            layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        return box

    def show_warning_message(self, title, text):
        box = self.create_message_box(QMessageBox.Icon.Warning, title, text)
        box.exec()

    def show_error_message(self, title, text):
        box = self.create_message_box(QMessageBox.Icon.Critical, title, text)
        box.exec()

    def start_restart_timer(self, auto_restart_hours):
        if not self.server_service.is_running:
            self.stop_restart_timer()
            return

        restart_seconds = int(auto_restart_hours or 0) * 3600

        if restart_seconds > 0:
            self.time_left = restart_seconds
            self.countdown_timer.start(1000)
        else:
            self.time_left = 0
            self.countdown_timer.stop()

        self.update_timer_text()

    def stop_restart_timer(self):
        self.time_left = 0
        self.countdown_timer.stop()
        self.update_timer_text()

    def update_timer_text(self):
        lang = LANG[self.current_lang]

        if not self.server_service.is_running:
            self.timer_lbl.setText(lang["timer_prefix"] + "00:00:00")
            return

        if self.time_left > 0:
            hours = self.time_left // 3600
            minutes = (self.time_left % 3600) // 60
            seconds = self.time_left % 60
            self.timer_lbl.setText(
                f"{lang['timer_prefix']}{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
        else:
            self.timer_lbl.setText(lang["timer_prefix"] + lang["timer_disabled"])

    def sync_server_state(self, force=False):
        is_running = self.server_service.is_running

        if not is_running and self.time_left != 0:
            self.stop_restart_timer()

        if force or is_running != self._last_running_state:
            self._last_running_state = is_running
            self.update_texts()

    def tick_timer(self):
        if not self.server_service.is_running:
            self.stop_restart_timer()
            self.sync_server_state(force=True)
            return

        if self.time_left > 0:
            self.time_left -= 1

        if self.time_left > 0:
            self.update_timer_text()
        else:
            self.restart_server()

    def get_server_error_message(self, error):
        lang = LANG[self.current_lang]

        if isinstance(error, EmptyExecutablePathError):
            return lang["exe_path_empty"]

        if isinstance(error, ExecutableNotFoundError):
            return lang["exe_path_not_found"]

        if isinstance(error, ExecutableIsDirectoryError):
            return lang["exe_path_is_directory"]

        if isinstance(error, InvalidExecutableTypeError):
            return lang["exe_path_not_exe"]

        if isinstance(error, UnexpectedExecutableNameError):
            return lang["exe_path_invalid_name"]

        if isinstance(error, ServerAlreadyRunningError):
            return lang["server_already_running"]

        if isinstance(error, ServerNotRunningError):
            return lang["server_not_running"]

        if isinstance(error, ServerStartError):
            return lang["failed_to_start_process"].format(error=error)

        if isinstance(error, ServerStopError):
            return lang["failed_to_stop_process"].format(error=error)

        return lang["unexpected_server_error"].format(error=error)

    def show_server_error(self, error):
        lang = LANG[self.current_lang]
        message = self.get_server_error_message(error)

        if isinstance(error, (ServerStartError, ServerStopError)):
            self.show_error_message(lang["error_title"], message)
        else:
            self.show_warning_message(lang["error_title"], message)

    def toggle_server(self):
        lang = LANG[self.current_lang]

        if not self.server_service.is_running:
            form_data = self.get_current_form_data()
            exe_path = form_data["exe_path"]
            launch_params = self.get_launch_params_list(form_data["launch_params"])

            try:
                self.server_service.start_server(exe_path, launch_params)
            except ServerServiceError as error:
                self.show_server_error(error)
                self.sync_server_state(force=True)
                return
            except Exception as error:
                self.show_error_message(
                    lang["error_title"],
                    lang["unexpected_server_error"].format(error=error),
                )
                self.sync_server_state(force=True)
                return

            self.start_restart_timer(form_data["auto_restart_hours"])
        else:
            try:
                self.server_service.stop_server()
            except ServerServiceError as error:
                self.show_server_error(error)
                self.sync_server_state(force=True)
                return
            except Exception as error:
                self.show_error_message(
                    lang["error_title"],
                    lang["unexpected_server_error"].format(error=error),
                )
                self.sync_server_state(force=True)
                return

            self.stop_restart_timer()

        self.sync_server_state(force=True)

    def restart_server(self):
        lang = LANG[self.current_lang]

        if not self.server_service.is_running:
            self.sync_server_state(force=True)
            return

        form_data = self.get_current_form_data()
        exe_path = form_data["exe_path"]
        launch_params = self.get_launch_params_list(form_data["launch_params"])

        try:
            self.server_service.restart_server(exe_path, launch_params)
        except ServerNotRunningError:
            self.stop_restart_timer()
            self.sync_server_state(force=True)
            return
        except ServerServiceError as error:
            self.stop_restart_timer()
            self.show_server_error(error)
            self.sync_server_state(force=True)
            return
        except Exception as error:
            self.stop_restart_timer()
            self.sync_server_state(force=True)
            self.show_error_message(
                lang["error_title"],
                lang["failed_to_restart"].format(error=error),
            )
            return

        self.start_restart_timer(form_data["auto_restart_hours"])
        self.sync_server_state(force=True)

    def check_for_updates(self):
        if (
            not self.UPDATE_INFO_URL
            or "username" in self.UPDATE_INFO_URL
            or "gist_id" in self.UPDATE_INFO_URL
        ):
            return

        self.updater = UpdateChecker(self.APP_VERSION, self.UPDATE_INFO_URL)
        self.updater.update_available.connect(self.show_update_dialog)
        self.updater.start()

    def show_update_dialog(self, new_ver, url, changelog):
        lang = LANG[self.current_lang]

        message = lang["update_msg"].format(
            new_ver=new_ver,
            curr_ver=self.APP_VERSION,
            changelog=changelog,
        )

        box = self.create_message_box(
            QMessageBox.Icon.Information,
            lang["update_title"],
            message,
        )

        btn_yes = box.addButton(lang["btn_yes"], QMessageBox.ButtonRole.AcceptRole)
        box.addButton(lang["btn_no"], QMessageBox.ButtonRole.RejectRole)

        box.exec()

        if box.clickedButton() == btn_yes:
            webbrowser.open(url)

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
            self.save_settings_from_ui()

        self.anim.finished.connect(lambda: self.setFixedSize(self.width(), 600))
        self.anim.start()

    def update_texts(self):
        lang = LANG[self.current_lang]
        is_running = self.server_service.is_running

        self.setWindowTitle(lang["title"])
        self.restart_btn.setText(lang["restart"])
        self.restart_btn.setEnabled(is_running)

        if is_running:
            self.status_lbl.setText(lang["status_on"])
            self.status_lbl.setStyleSheet("color: #5CB85C;")
            self.start_btn.setText(lang["stop"])
            self.start_btn.setStyleSheet(
                "background-color: #D9534F; color: white; font-size: 16pt; font-weight: 600; border-radius: 24px;"
            )
        else:
            self.status_lbl.setText(lang["status_off"])
            self.status_lbl.setStyleSheet("color: #D9534F;")
            self.start_btn.setText(lang["start"])
            self.start_btn.setStyleSheet(
                "background-color: #5CB85C; color: white; font-size: 16pt; font-weight: 600; border-radius: 24px;"
            )

        self.update_timer_text()
        self.settings_panel.update_texts(self.current_lang)

    def change_language(self, index):
        self.current_lang = "ru" if index == 0 else "en"
        self.sync_server_state(force=True)

    def closeEvent(self, a0: QCloseEvent | None):
        self.save_settings_from_ui()

        try:
            self.server_service.stop_server()
        except ServerServiceError:
            pass

        if a0 is not None:
            a0.accept()
