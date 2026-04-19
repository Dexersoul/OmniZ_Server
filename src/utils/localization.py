# src/utils/localization.py
LANG = {
    "ru": {
        "title": "OmniZ Server",
        "status_off": "OFFLINE",
        "status_on": "ONLINE",
        "start": "СТАРТ",
        "stop": "СТОП",
        "restart": "РЕСТАРТ",
        "timer_prefix": "Таймер авторестарта\n",
        "settings_title": "Настройки сервера",
        "path_placeholder": "Путь к DayZServer_x64.exe",
        "browse": "Обзор",
        "auto_restart": "Авторестарт",
        "launch_cfg": "Параметры запуска",
        "cfg_tooltip": (
            "<b>-config=serverDZ.cfg</b> — Имя, пароль и базовые настройки<br>"
            "<b>-port=2302</b> — Порт сервера<br>"
            "<b>-profiles=</b> — Папка для логов, дампов, BattlEye и Rcon<br>"
            "<b>-cpuCount=</b> — Количество логических ядер процессора<br>"
            "<b>-mod=</b> — Клиентские моды (разделять через ;)<br>"
            "<b>-serverMod=</b> — Серверные моды<br>"
            "<b>-doLogs</b> — Запись системных сообщений (RPT)<br>"
            "<b>-adminLog</b> — Логирование действий администраторов<br>"
            "<b>-freezeCheck</b> — Остановка сервера при зависании (>5 мин)"
        ),
        "update_title": "Доступно обновление!",
        "update_msg": "Вышла новая версия OmniZ Server: v.{new_ver}\nВаша версия: v.{curr_ver}\n\nЧто нового:\n{changelog}\n\nХотите скачать обновление прямо сейчас?",
        "btn_yes": "Да, скачать",
        "btn_no": "Позже",
    },
    "en": {
        "title": "OmniZ Server",
        "status_off": "OFFLINE",
        "status_on": "ONLINE",
        "start": "START",
        "stop": "STOP",
        "restart": "RESTART",
        "timer_prefix": "Auto-Restart Timer\n",
        "settings_title": "Server Settings",
        "path_placeholder": "Path to DayZServer_x64.exe",
        "browse": "Browse",
        "auto_restart": "Auto-Restart",
        "launch_cfg": "Launch Parameters",
        "cfg_tooltip": (
            "<b>-config=serverDZ.cfg</b> — Basic settings, name, password<br>"
            "<b>-port=2302</b> — Server port<br>"
            "<b>-profiles=</b> — Folder for logs, dumps, BattlEye, Rcon<br>"
            "<b>-cpuCount=</b> — Number of logical CPU cores<br>"
            "<b>-mod=</b> — Client mods (separated by ;)<br>"
            "<b>-serverMod=</b> — Server mods<br>"
            "<b>-doLogs</b> — System messages logging (RPT)<br>"
            "<b>-adminLog</b> — Admin actions logging<br>"
            "<b>-freezeCheck</b> — Stop server on freeze (>5 min)"
        ),
        "update_title": "Update Available!",
        "update_msg": "A new version of OmniZ Server is available: v.{new_ver}\nYour version: v.{curr_ver}\n\nWhat's new:\n{changelog}\n\nDo you want to download the update now?",
        "btn_yes": "Yes, download",
        "btn_no": "Later",
    },
}
