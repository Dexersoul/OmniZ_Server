# src/services/server_service.py
import os
import subprocess


class ServerServiceError(Exception):
    pass


class EmptyExecutablePathError(ServerServiceError):
    pass


class ExecutableNotFoundError(ServerServiceError):
    pass


class ExecutableIsDirectoryError(ServerServiceError):
    pass


class InvalidExecutableTypeError(ServerServiceError):
    pass


class UnexpectedExecutableNameError(ServerServiceError):
    pass


class ServerAlreadyRunningError(ServerServiceError):
    pass


class ServerNotRunningError(ServerServiceError):
    pass


class ServerStartError(ServerServiceError):
    pass


class ServerStopError(ServerServiceError):
    pass


class ServerService:
    # === CONSTANTS ===
    EXPECTED_EXE_NAME = "dayzserver_x64.exe"

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

    # === VALIDATION ===
    def validate_exe_path(self, exe_path):
        raw_path = str(exe_path or "").strip()

        if not raw_path:
            raise EmptyExecutablePathError("Empty executable path")

        normalized_path = os.path.abspath(
            os.path.expandvars(os.path.expanduser(raw_path))
        )

        if os.path.isdir(normalized_path):
            raise ExecutableIsDirectoryError(normalized_path)

        if not os.path.exists(normalized_path):
            raise ExecutableNotFoundError(normalized_path)

        if not os.path.isfile(normalized_path):
            raise ExecutableNotFoundError(normalized_path)

        if not normalized_path.lower().endswith(".exe"):
            raise InvalidExecutableTypeError(normalized_path)

        file_name = os.path.basename(normalized_path).lower()
        if file_name != self.EXPECTED_EXE_NAME:
            raise UnexpectedExecutableNameError(file_name)

        return normalized_path

    # === HELPERS ===
    def build_command(self, exe_path, launch_params):
        return [exe_path] + list(launch_params or [])

    # === ACTIONS ===
    def start_server(self, exe_path, launch_params):
        if self.is_running:
            raise ServerAlreadyRunningError("Server is already running")

        validated_exe_path = self.validate_exe_path(exe_path)
        working_dir = os.path.dirname(validated_exe_path) or None
        command = self.build_command(validated_exe_path, launch_params)

        try:
            process = subprocess.Popen(command, cwd=working_dir)
        except OSError as error:
            raise ServerStartError(str(error)) from error

        self._server_process = process
        return process

    def stop_server(self):
        process = self._server_process

        if process is None:
            self._server_process = None
            return False

        if process.poll() is not None:
            self._server_process = None
            return False

        try:
            process.terminate()

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

        except OSError as error:
            raise ServerStopError(str(error)) from error
        finally:
            self._server_process = None

        return True

    def restart_server(self, exe_path, launch_params):
        if not self.is_running:
            raise ServerNotRunningError("Server is not running")

        self.stop_server()
        return self.start_server(exe_path, launch_params)
