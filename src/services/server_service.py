# src/services/server_service.py
import os
import subprocess


class ServerService:
    # === INIT ===
    def __init__(self):
        self._server_process = None

    # === STATE ===
    @property
    def is_running(self):
        if self._server_process is None:
            return False

        if self._server_process.poll() is None:
            return True

        self._server_process = None
        return False

    # === ACTIONS ===
    def start_server(self, exe_path, launch_params):
        if not exe_path:
            raise FileNotFoundError("Empty executable path")

        if not os.path.isfile(exe_path):
            raise FileNotFoundError(f"Executable not found: {exe_path}")

        if self.is_running:
            raise RuntimeError("Server is already running")

        working_dir = os.path.dirname(exe_path) or None
        command = [exe_path] + list(launch_params)

        self._server_process = subprocess.Popen(command, cwd=working_dir)
        return self._server_process

    def stop_server(self):
        process = self._server_process

        if process is None:
            self._server_process = None
            return

        if process.poll() is not None:
            self._server_process = None
            return

        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        finally:
            self._server_process = None

    def restart_server(self, exe_path, launch_params):
        self.stop_server()
        return self.start_server(exe_path, launch_params)
