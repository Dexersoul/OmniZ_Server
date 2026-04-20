# src/services/launch_params_service.py
import re


class LaunchParamsValidationError(Exception):
    def __init__(self, message_key):
        super().__init__(message_key)
        self.message_key = message_key


class LaunchParamsService:
    # === LIMITS ===
    MAX_CPU_COUNT = 6

    # === BUILD ORDER ===
    BUILD_ORDER = [
        ("value", "config_file", "-config"),
        ("value", "port", "-port"),
        ("value", "profiles_dir", "-profiles"),
        ("value", "cpu_count", "-cpuCount"),
        ("bool", "do_logs", "-doLogs"),
        ("bool", "admin_log", "-adminLog"),
        ("bool", "freeze_check", "-freezeCheck"),
        ("value", "mod_list", "-mod"),
        ("value", "server_mod_list", "-serverMod"),
    ]

    # === DEFAULT STRUCTURED VALUES ===
    DEFAULT_STRUCTURED_PARAMS = {
        "config_file": "serverDZ.cfg",
        "port": "2302",
        "profiles_dir": "profiles",
        "cpu_count": "4",
        "do_logs": True,
        "admin_log": True,
        "freeze_check": True,
        "mod_list": "",
        "server_mod_list": "",
        "additional_params_text": "",
    }

    # === FORM SHAPES ===
    def get_empty_form_data(self):
        data = {}

        for item_type, key, _ in self.BUILD_ORDER:
            data[key] = False if item_type == "bool" else ""

        data["additional_params_text"] = ""
        return data

    def get_default_structured_params(self):
        return dict(self.DEFAULT_STRUCTURED_PARAMS)

    def build_default_launch_params_text(self):
        return self.build_launch_params_text(self.get_default_structured_params())

    # === PARSE ===
    def parse_launch_params_text(self, launch_params_text):
        structured = self.get_empty_form_data()
        additional_lines = []
        seen_keys = set()

        for line in self._split_lines(launch_params_text):
            item_type, key, value = self._match_supported_line(line)

            if key is None:
                additional_lines.append(line)
                continue

            if key in seen_keys:
                additional_lines.append(line)
                continue

            seen_keys.add(key)

            if item_type == "bool":
                structured[key] = True
            else:
                if key == "cpu_count":
                    structured[key] = self._normalize_loaded_cpu_count(value)
                else:
                    structured[key] = value

        structured["additional_params_text"] = "\n".join(additional_lines)
        return structured

    # === NORMALIZE ===
    def normalize_form_data(self, form_data):
        normalized = self.get_empty_form_data()

        normalized["config_file"] = self._normalize_text(
            form_data.get("config_file", "")
        )
        normalized["port"] = self._normalize_port(form_data.get("port", ""))
        normalized["profiles_dir"] = self._normalize_text(
            form_data.get("profiles_dir", "")
        )
        normalized["cpu_count"] = self._normalize_cpu_count(
            form_data.get("cpu_count", "")
        )

        normalized["do_logs"] = bool(form_data.get("do_logs", False))
        normalized["admin_log"] = bool(form_data.get("admin_log", False))
        normalized["freeze_check"] = bool(form_data.get("freeze_check", False))

        normalized["mod_list"] = self._normalize_mod_list(form_data.get("mod_list", ""))
        normalized["server_mod_list"] = self._normalize_mod_list(
            form_data.get("server_mod_list", "")
        )

        normalized["additional_params_text"] = self._normalize_additional_params(
            form_data.get("additional_params_text", "")
        )

        return normalized

    # === BUILD ===
    def build_launch_params_list(self, form_data):
        normalized = self.normalize_form_data(form_data)
        lines = []

        for item_type, key, flag in self.BUILD_ORDER:
            if item_type == "bool":
                if normalized[key]:
                    lines.append(flag)
                continue

            value = normalized[key]
            if value:
                lines.append(f"{flag}={value}")

        lines.extend(self._split_lines(normalized["additional_params_text"]))
        return lines

    def build_launch_params_text(self, form_data):
        return "\n".join(self.build_launch_params_list(form_data))

    # === INTERNAL MATCH ===
    def _match_supported_line(self, line):
        for item_type, key, flag in self.BUILD_ORDER:
            if item_type == "bool":
                if line.lower() == flag.lower():
                    return item_type, key, True
                continue

            pattern = rf"^{re.escape(flag)}\s*=\s*(.*)$"
            match = re.match(pattern, line, flags=re.IGNORECASE)

            if match is not None:
                return item_type, key, match.group(1).strip()

        return None, None, None

    # === INTERNAL NORMALIZE ===
    def _normalize_text(self, value):
        return str(value or "").strip()

    def _normalize_port(self, value):
        raw_value = self._normalize_text(value)

        if not raw_value:
            return ""

        if not raw_value.isdigit():
            raise LaunchParamsValidationError("invalid_port")

        port = int(raw_value)
        if port < 1 or port > 65535:
            raise LaunchParamsValidationError("invalid_port")

        return str(port)

    def _normalize_cpu_count(self, value):
        raw_value = self._normalize_text(value)

        if not raw_value:
            return ""

        if not raw_value.isdigit():
            raise LaunchParamsValidationError("invalid_cpu_count")

        cpu_count = int(raw_value)
        if cpu_count < 1 or cpu_count > self.MAX_CPU_COUNT:
            raise LaunchParamsValidationError("invalid_cpu_count")

        return str(cpu_count)

    def _normalize_loaded_cpu_count(self, value):
        raw_value = self._normalize_text(value)

        if not raw_value.isdigit():
            return raw_value

        cpu_count = int(raw_value)

        if cpu_count < 1:
            return "1"

        if cpu_count > self.MAX_CPU_COUNT:
            return str(self.MAX_CPU_COUNT)

        return str(cpu_count)

    def _normalize_mod_list(self, value):
        raw_value = self._normalize_text(value)

        if not raw_value:
            return ""

        parts = [part.strip() for part in raw_value.split(";")]
        parts = [part for part in parts if part]
        return ";".join(parts)

    def _normalize_additional_params(self, value):
        return "\n".join(self._split_lines(value))

    def _split_lines(self, value):
        text = str(value or "")
        lines = [line.strip() for line in text.splitlines()]
        return [line for line in lines if line]
