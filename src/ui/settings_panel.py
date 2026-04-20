# src/ui/settings_panel.py
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtGui import (
    QColor,
    QCursor,
    QFont,
    QIntValidator,
    QPainter,
    QPaintEvent,
    QPen,
)
from PyQt6.QtCore import QPointF, QRectF, QSize, Qt

from src.utils.localization import LANG


class FormCheckBox(QCheckBox):
    BOX_SIZE = 18
    BOX_RADIUS = 4
    BOX_TEXT_GAP = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(24)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def sizeHint(self):
        hint = super().sizeHint()
        return QSize(hint.width(), max(hint.height(), 24))

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        box_x = 0.0
        box_y = (rect.height() - self.BOX_SIZE) / 2
        box_rect = QRectF(box_x, box_y, self.BOX_SIZE, self.BOX_SIZE)

        if self.isEnabled():
            text_color = QColor("#1F2933")
            if self.isChecked():
                fill_color = QColor("#EAF3FF")
                border_color = QColor("#007BFF")
            else:
                fill_color = QColor("#FFFFFF")
                border_color = QColor("#AEBCCC")
        else:
            text_color = QColor("#94A3B8")
            fill_color = QColor("#F8FAFC")
            border_color = QColor("#CBD5E1")

        painter.setPen(QPen(border_color, 1.5))
        painter.setBrush(fill_color)
        painter.drawRoundedRect(box_rect, self.BOX_RADIUS, self.BOX_RADIUS)

        if self.isChecked():
            tick_pen = QPen(border_color, 2.2)
            tick_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            tick_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(tick_pen)

            p1 = QPointF(box_x + 4.5, box_y + 9.5)
            p2 = QPointF(box_x + 8.0, box_y + 13.0)
            p3 = QPointF(box_x + 13.5, box_y + 5.5)

            painter.drawLine(p1, p2)
            painter.drawLine(p2, p3)

        painter.setPen(text_color)
        painter.setFont(self.font())

        text_rect = rect.adjusted(
            int(self.BOX_SIZE + self.BOX_TEXT_GAP),
            0,
            0,
            0,
        )
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text(),
        )


class SettingsPanel(QFrame):
    # === INIT ===
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_lang = "ru"
        self.ar_btns = []

        self.setObjectName("settingsPanel")
        self.setFixedSize(400, 600)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            QFrame#settingsPanel {
                background-color: #FFFFFF;
                border-left: 1px solid #E0E0E0;
            }

            QWidget#settingsPanelContent {
                background-color: #FFFFFF;
            }

            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }

            QLabel {
                color: #1F2933;
                background: transparent;
            }

            QLabel[role="section"] {
                color: #007BFF;
                font-weight: 700;
                background: transparent;
            }

            QLabel[role="field"] {
                color: #334155;
                background: transparent;
            }

            QLineEdit {
                border: 1px solid #CCC;
                border-radius: 4px;
                padding: 0 8px;
                font-size: 10pt;
                background: #FFFFFF;
                color: #111111;
                selection-background-color: #007BFF;
                selection-color: #FFFFFF;
                min-height: 36px;
            }

            QTextEdit {
                border: 1px solid #CCC;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 9pt;
                background: #FFFFFF;
                color: #111111;
                selection-background-color: #007BFF;
                selection-color: #FFFFFF;
                min-height: 110px;
            }

            QPushButton[role="browse"] {
                background-color: #F0F0F0;
                border: 1px solid #CCC;
                border-radius: 4px;
                font-weight: bold;
                color: #333333;
            }

            QPushButton[role="browse"]:hover {
                background-color: #E7E7E7;
            }

            QCheckBox {
                color: #1F2933;
                font-size: 10pt;
                spacing: 10px;
                background: transparent;
            }

            QScrollBar:vertical {
                width: 10px;
                background: #FFFFFF;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #D0D4D9;
                border-radius: 5px;
                min-height: 24px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                height: 0px;
            }
        """)

        self.init_ui()

    # === UI HELPERS ===
    def create_section_label(self):
        label = QLabel()
        label.setProperty("role", "section")
        label.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        return label

    def create_field_label(self):
        label = QLabel()
        label.setProperty("role", "field")
        label.setFont(QFont("Inter", 10, QFont.Weight.Medium))
        return label

    def create_line_edit(self):
        return QLineEdit()

    def create_text_edit(self):
        return QTextEdit()

    def create_checkbox(self):
        return FormCheckBox()

    def add_field_block(self, parent_layout, label_widget, input_widget):
        block_layout = QVBoxLayout()
        block_layout.setSpacing(6)
        block_layout.addWidget(label_widget)
        block_layout.addWidget(input_widget)
        parent_layout.addLayout(block_layout)

    # === UI ===
    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(30, 30, 20, 30)
        root_layout.setSpacing(0)

        self.title_lbl = QLabel()
        self.title_lbl.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet("color: #1F2933; background: transparent;")
        root_layout.addWidget(self.title_lbl)
        root_layout.addSpacing(16)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        viewport = self.scroll_area.viewport()
        if viewport is not None:
            viewport.setStyleSheet("background-color: #FFFFFF;")

        root_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("settingsPanelContent")
        self.scroll_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.scroll_area.setWidget(self.scroll_content)

        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setContentsMargins(0, 0, 10, 0)
        content_layout.setSpacing(16)

        # === EXE ===
        self.exe_lbl = self.create_field_label()
        content_layout.addWidget(self.exe_lbl)

        path_layout = QHBoxLayout()
        path_layout.setSpacing(10)

        self.path_input = self.create_line_edit()

        self.browse_btn = QPushButton()
        self.browse_btn.setProperty("role", "browse")
        self.browse_btn.setFixedSize(80, 36)
        self.browse_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.browse_btn.clicked.connect(self.browse_file)

        path_layout.addWidget(self.path_input, 1)
        path_layout.addWidget(self.browse_btn)
        content_layout.addLayout(path_layout)

        # === AUTO RESTART ===
        self.ar_lbl = self.create_section_label()
        content_layout.addWidget(self.ar_lbl)

        ar_layout = QHBoxLayout()
        ar_layout.setSpacing(10)

        for hours in [3, 6, 12]:
            btn = QPushButton()
            btn.setFixedSize(50, 36)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F0F0F0;
                    color: #333333;
                    border: 1px solid #C8D0D8;
                    border-radius: 18px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: #E7EEF7;
                    border: 1px solid #AEBCCC;
                }
                QPushButton:pressed {
                    background-color: #DCE8F5;
                    border: 1px solid #93A7BC;
                }
                QPushButton:checked {
                    background-color: #007BFF;
                    color: #FFFFFF;
                    border: 1px solid #007BFF;
                }
                QPushButton:checked:hover {
                    background-color: #006FE6;
                    border: 1px solid #006FE6;
                }
                QPushButton:checked:pressed {
                    background-color: #005FCC;
                    border: 1px solid #005FCC;
                }
            """)
            btn.clicked.connect(lambda checked, b=btn: self.on_ar_btn_clicked(b))
            self.ar_btns.append(btn)
            ar_layout.addWidget(btn)

        ar_layout.addStretch()
        content_layout.addLayout(ar_layout)

        # === MAIN SECTION ===
        self.main_group_lbl = self.create_section_label()
        content_layout.addWidget(self.main_group_lbl)

        self.config_lbl = self.create_field_label()
        self.config_input = self.create_line_edit()
        self.add_field_block(content_layout, self.config_lbl, self.config_input)

        self.port_lbl = self.create_field_label()
        self.port_input = self.create_line_edit()
        self.port_input.setValidator(QIntValidator(1, 65535, self))
        self.add_field_block(content_layout, self.port_lbl, self.port_input)

        self.profiles_lbl = self.create_field_label()
        self.profiles_input = self.create_line_edit()
        self.add_field_block(content_layout, self.profiles_lbl, self.profiles_input)

        # === RUNTIME SECTION ===
        self.runtime_group_lbl = self.create_section_label()
        content_layout.addWidget(self.runtime_group_lbl)

        self.cpu_lbl = self.create_field_label()
        self.cpu_input = self.create_line_edit()
        self.cpu_input.setValidator(QIntValidator(1, 6, self))
        self.cpu_input.setMaxLength(1)
        self.add_field_block(content_layout, self.cpu_lbl, self.cpu_input)

        # === LOGS SECTION ===
        self.logs_group_lbl = self.create_section_label()
        content_layout.addWidget(self.logs_group_lbl)

        self.do_logs_cb = self.create_checkbox()
        self.admin_log_cb = self.create_checkbox()
        self.freeze_check_cb = self.create_checkbox()

        content_layout.addWidget(self.do_logs_cb)
        content_layout.addWidget(self.admin_log_cb)
        content_layout.addWidget(self.freeze_check_cb)

        # === MODS SECTION ===
        self.mods_group_lbl = self.create_section_label()
        content_layout.addWidget(self.mods_group_lbl)

        self.mod_lbl = self.create_field_label()
        self.mod_input = self.create_line_edit()
        self.add_field_block(content_layout, self.mod_lbl, self.mod_input)

        self.server_mod_lbl = self.create_field_label()
        self.server_mod_input = self.create_line_edit()
        self.add_field_block(content_layout, self.server_mod_lbl, self.server_mod_input)

        # === ADDITIONAL SECTION ===
        self.additional_group_lbl = self.create_section_label()
        content_layout.addWidget(self.additional_group_lbl)

        self.additional_params_lbl = self.create_field_label()
        self.additional_params_input = self.create_text_edit()
        self.add_field_block(
            content_layout,
            self.additional_params_lbl,
            self.additional_params_input,
        )

        content_layout.addStretch()

    # === FORM DATA ===
    def set_form_data(self, data):
        self.path_input.setText(str(data.get("exe_path", "") or ""))
        self.config_input.setText(str(data.get("config_file", "") or ""))
        self.port_input.setText(str(data.get("port", "") or ""))
        self.profiles_input.setText(str(data.get("profiles_dir", "") or ""))
        self.cpu_input.setText(str(data.get("cpu_count", "") or ""))
        self.mod_input.setText(str(data.get("mod_list", "") or ""))
        self.server_mod_input.setText(str(data.get("server_mod_list", "") or ""))
        self.additional_params_input.setPlainText(
            str(data.get("additional_params_text", "") or "")
        )

        self.do_logs_cb.setChecked(bool(data.get("do_logs", False)))
        self.admin_log_cb.setChecked(bool(data.get("admin_log", False)))
        self.freeze_check_cb.setChecked(bool(data.get("freeze_check", False)))

        saved_hours = data.get("auto_restart_hours", 0)

        for btn in self.ar_btns:
            btn.setChecked(False)

        for index, hours in enumerate([3, 6, 12]):
            if hours == saved_hours:
                self.ar_btns[index].setChecked(True)
                break

    def get_form_data(self):
        return {
            "exe_path": self.path_input.text().strip(),
            "config_file": self.config_input.text(),
            "port": self.port_input.text(),
            "profiles_dir": self.profiles_input.text(),
            "cpu_count": self.cpu_input.text(),
            "do_logs": self.do_logs_cb.isChecked(),
            "admin_log": self.admin_log_cb.isChecked(),
            "freeze_check": self.freeze_check_cb.isChecked(),
            "mod_list": self.mod_input.text(),
            "server_mod_list": self.server_mod_input.text(),
            "additional_params_text": self.additional_params_input.toPlainText(),
            "auto_restart_hours": self.get_selected_restart_hours(),
        }

    # === HELPERS ===
    def update_texts(self, current_lang):
        self.current_lang = current_lang
        lang = LANG[current_lang]

        self.title_lbl.setText(lang["settings_title"])
        self.exe_lbl.setText(lang["exe_path_label"])
        self.path_input.setPlaceholderText(lang["path_placeholder"])
        self.browse_btn.setText(lang["browse"])

        self.ar_lbl.setText(lang["auto_restart"])

        self.main_group_lbl.setText(lang["launch_group_main"])
        self.config_lbl.setText(lang["config_file_label"])
        self.port_lbl.setText(lang["port_label"])
        self.profiles_lbl.setText(lang["profiles_dir_label"])

        self.runtime_group_lbl.setText(lang["launch_group_runtime"])
        self.cpu_lbl.setText(lang["cpu_count_label"])

        self.logs_group_lbl.setText(lang["launch_group_logs"])
        self.do_logs_cb.setText(lang["do_logs_label"])
        self.admin_log_cb.setText(lang["admin_log_label"])
        self.freeze_check_cb.setText(lang["freeze_check_label"])

        self.mods_group_lbl.setText(lang["launch_group_mods"])
        self.mod_lbl.setText(lang["mod_label"])
        self.server_mod_lbl.setText(lang["server_mod_label"])

        self.additional_group_lbl.setText(lang["launch_group_additional"])
        self.additional_params_lbl.setText(lang["additional_params_label"])

        self.config_input.setPlaceholderText(lang["config_placeholder"])
        self.port_input.setPlaceholderText(lang["port_placeholder"])
        self.profiles_input.setPlaceholderText(lang["profiles_placeholder"])
        self.cpu_input.setPlaceholderText(lang["cpu_placeholder"])
        self.mod_input.setPlaceholderText(lang["mod_placeholder"])
        self.server_mod_input.setPlaceholderText(lang["server_mod_placeholder"])
        self.additional_params_input.setPlaceholderText(
            lang["additional_params_placeholder"]
        )
        self.additional_params_input.setToolTip(lang["additional_params_tooltip"])

        suffix = "ч" if current_lang == "ru" else "h"
        for index, btn in enumerate(self.ar_btns):
            btn.setText(f"{[3, 6, 12][index]}{suffix}")

    def on_ar_btn_clicked(self, clicked_btn):
        for btn in self.ar_btns:
            if btn != clicked_btn:
                btn.setChecked(False)

    def browse_file(self):
        lang = LANG[self.current_lang]

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            lang["select_exe_title"],
            "",
            "EXE (*.exe)",
        )
        if file_name:
            self.path_input.setText(file_name)

    def get_selected_restart_hours(self):
        for index, btn in enumerate(self.ar_btns):
            if btn.isChecked():
                return [3, 6, 12][index]
        return 0
