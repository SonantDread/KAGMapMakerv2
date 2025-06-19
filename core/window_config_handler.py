import json
import os
from typing import Optional

from PyQt6.QtWidgets import QMainWindow

from utils.file_handler import FileHandler
from utils.vec2f import Vec2f


class WindowConfigHandler:
    def __init__(self, window: QMainWindow) -> None:
        self.window = window

        self.fh = FileHandler()
        self._ensure_valid_configs()

    def save_window_config(self) -> None:
        config_path = self.fh.paths.get("config_path")
        if config_path is None:
            raise SyntaxError("ERROR: File Handler does not have the right path.")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            full_config = {}

        if 'window' not in full_config or not isinstance(full_config.get('window'), dict):
            full_config['window'] = {}

        size = self._get_window_size()
        offset = self._get_window_offset()

        full_config['window']['offset'] = {
            'x': offset.x,
            'y': offset.y
        }

        full_config['window']['size'] = {
            'width': size.x,
            'height': size.y
        }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=4)

        except (FileNotFoundError, PermissionError) as e:
            print(f"ERROR: Failed to save window config to '{config_path}': {e}")

    def load_window_config(self) -> None:
        window: QMainWindow = self.window
        config = self._get_window_config()

        window.setWindowTitle("KAG Map Maker")

        # don't crash the script, just dont load any configs
        if config is None:
            return

        offset = config['offset']
        offset = Vec2f(offset.get('x', 0), offset.get('y', 0))

        size = config['size']
        size = Vec2f(size.get('width', 1920*.75), size.get('height', 1080*.75))

        self._set_window_offset_size(offset, size)

    def _set_window_offset_size(self, offset: Vec2f, size: Vec2f) -> None:
        offset_x, offset_y = offset
        width, height = size
        self.window.setGeometry(int(offset_x), int(offset_y), int(width), int(height))

    def _get_window_config(self, is_retry: bool = False) -> Optional[dict]:
        paths = [
            self.fh.paths.get("config_path"),
            self.fh.paths.get("default_config_path")
        ]

        for path in paths:
            # should never happen
            if not path:
                raise SyntaxError("Error in getting FileHandler's paths.")

            # attempt to load the config
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    window_config = config.get('window')

                    if window_config:
                        return window_config

            # not found? try again
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as exc:
                # corrupt or wrong structure
                print(f"Invalid config file at '{path}': {exc}")

                if is_retry:
                    print("ERROR: Configuration fix failed. Aborting.")
                    return None

                print("Attempting to repair configuration...")
                self._ensure_valid_configs()

                return self._get_window_config(True)

        print("Warning: Could not find a valid 'window' configuration.")
        return None

    def _ensure_valid_configs(self) -> None:
        config_path = self.fh.paths.get("config_path")
        default_config_path = self.fh.paths.get("default_config_path")

        if not config_path or not default_config_path:
            print("ERROR: Critical configuration paths are not defined. Cannot repair.")
            return

        # default config
        try:
            with open(default_config_path, 'r', encoding='utf-8') as f:
                default_cfg = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"CRITICAL: Cannot load default config template from '{default_config_path}'. Aborting repair. Error: {e}")
            return

        # attempt to load user's config, if its bad use a blank dictionary
        user_cfg = {}
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_cfg = json.load(f)

            # valid JSON but not a dictionary
            if not isinstance(user_cfg, dict):
                user_cfg = {}

        # missing or corrupt
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"User config at '{config_path}' is missing or corrupt. Will create a new one.")

        # recursively validate and merge the user config against the default template
        validated_config = self._validate_and_merge(default_cfg, user_cfg)

        # write the corrected configuration back to the user's file
        try:
            # ensure the destination directory exists
            config_dir = os.path.dirname(config_path)
            os.makedirs(config_dir, exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(validated_config, f, indent=4)

            print(f"Successfully validated and repaired user config at: {config_path}")

        except (json.JSONDecodeError, PermissionError) as e:
            print(f"CRITICAL: Failed to write repaired config to '{config_path}'. Error: {e}")

    def _validate_and_merge(self, template: dict, user_data: dict) -> dict:
        validated_output = {}

        for key, template_value in template.items():
            user_value = user_data.get(key)

            # the template value is a nested dictionary
            if isinstance(template_value, dict):
                # if user's value is also a dict, recurse into it, otherwise treat as invalid
                user_nested_dict = user_value if isinstance(user_value, dict) else {}
                validated_output[key] = self._validate_and_merge(template_value, user_nested_dict)

            # the template value is a primitive (string, int, bool, list, etc).
            else:
                # check if the user's value has the same type as the template's value
                if isinstance(user_value, type(template_value)):
                    # types match, keep user's
                    validated_output[key] = user_value

                else:
                    # keep default, type mismatch
                    validated_output[key] = template_value

        # add keys that are in the user's config but not in the template
        for key, user_value in user_data.items():
            if key not in template:
                validated_output[key] = user_value

        return validated_output

    def _get_window_size(self) -> Vec2f:
        size = self.window.size()
        return Vec2f(size.width(), size.height())

    def _get_window_offset(self) -> Vec2f:
        offset = self.window.geometry()
        return Vec2f(offset.x(), offset.y())
