# src/utils/updater.py
import json
import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal


class UpdateChecker(QThread):
    # Сигналы для передачи данных в интерфейс
    update_available = pyqtSignal(str, str, str)  # версия, ссылка, список изменений

    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url

    def run(self):
        try:
            # Делаем запрос к JSON файлу (таймаут 3 секунды, чтобы не висеть вечно)
            req = urllib.request.Request(
                self.update_url, headers={"User-Agent": "OmniZ-Updater"}
            )
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode("utf-8"))

            latest_version = data.get("version")
            download_url = data.get("url")
            changelog = data.get("changelog", "Нет описания / No description")

            # Если версия на сервере отличается от текущей - подаем сигнал!
            # (Для простоты сравниваем строки, в реальном проекте можно использовать float)
            if latest_version and latest_version != self.current_version:
                self.update_available.emit(latest_version, download_url, changelog)

        except Exception as e:
            # Если нет интернета или сервер лежит - просто молчим, чтобы не бесить пользователя
            print(f"[Updater] Ошибка проверки обновлений: {e}")
