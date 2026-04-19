# src/services/settings_service.py
import json
import os


class SettingsService:
    # === SETTINGS PATHS ===
    CONFIG_DIR_NAME = "OmniZ_Server"
    CONFIG_FILE_NAME = "config.json"

    # === DEFAULTS ===
    DEFAULT_LAUNCH_PARAMS = (
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

    def __init__(self):
        appdata_path = os.getenv("APPDATA") or os.path.expanduser("~")
        self.config_dir = os.path.join(appdata_path, self.CONFIG_DIR_NAME)
        self.config_file = os.path.join(self.config_dir, self.CONFIG_FILE_NAME)

    # === INTERNAL ===
    def _ensure_config_dir(self):
        os.makedirs(self.config_dir, exist_ok=True)

    # === PUBLIC API ===
    def get_default_settings(self):
        return {
            "exe_path": "",
            "launch_params": self.DEFAULT_LAUNCH_PARAMS,
            "auto_restart_hours": 0,
        }

    def load_settings(self):
        self._ensure_config_dir()
        defaults = self.get_default_settings()

        if not os.path.exists(self.config_file):
            return defaults

        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception as error:
            print(f"Error loading config: {error}")
            return defaults

        return {
            "exe_path": data.get("exe_path", defaults["exe_path"]),
            "launch_params": data.get("launch_params", defaults["launch_params"]),
            "auto_restart_hours": data.get(
                "auto_restart_hours",
                defaults["auto_restart_hours"],
            ),
        }

    def save_settings(self, settings):
        self._ensure_config_dir()
        defaults = self.get_default_settings()

        data = {
            "exe_path": str(settings.get("exe_path", defaults["exe_path"])).strip(),
            "launch_params": str(
                settings.get("launch_params", defaults["launch_params"])
            ).strip(),
            "auto_restart_hours": int(
                settings.get("auto_restart_hours", defaults["auto_restart_hours"]) or 0
            ),
        }

        try:
            with open(self.config_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as error:
            print(f"Error saving config: {error}")
