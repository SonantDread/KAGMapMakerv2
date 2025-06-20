import json
import os
from typing import Optional

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QRect

from core.communicator import Communicator
from utils.file_handler import FileHandler
from utils.vec2f import Vec2f


class WindowConfigHandler:
    def __init__(self, window: QMainWindow) -> None:
        self.window = window

        self.fh = FileHandler()
        self.communicator = Communicator()

        self._ensure_valid_configs()

    def save_window_config(self) -> None:
        config_path = self.fh.paths.get("config_path")
        if config_path is None:
            raise SyntaxError("ERROR: File Handler does not have the right path.")

        full_config: dict = self._get_config_data() or {}

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

        last_map = self.communicator.last_saved_map_path
        # ignore saving a null map path
        if last_map is not None and last_map != "":
            full_config['last worked on map'] = last_map

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=4)

        except (FileNotFoundError, PermissionError) as e:
            print(f"ERROR: Failed to save window config to '{config_path}': {e}")

    def load_window_config(self) -> None:
        window: QMainWindow = self.window
        full_config = self._get_config_data()

        window.setWindowTitle("KAG Map Maker")

        # don't crash the script, just dont load any configs
        if full_config is None:
            return

        self.communicator.last_saved_map_path = full_config.get("last worked on map")

        # safely get the window config using .get() to avoid errors if the key is missing
        window_config = full_config.get('window')
        if not window_config:
            print("Warning: 'window' configuration not found. Using default geometry.")
            return

        offset = window_config.get('offset', {})
        offset = Vec2f(offset.get('x', 0), offset.get('y', 0))

        size = window_config.get('size', {})
        size = Vec2f(size.get('width', 1920*.75), size.get('height', 1080*.75))

        self._set_window_offset_size(offset, size)

    def _set_window_offset_size(self, offset: Vec2f, size: Vec2f) -> None:
        offset_x, offset_y = offset
        width, height = size

        offset_x, offset_y, width, height = self._ensure_window_onscreen(offset, size)

        self.window.setGeometry(int(offset_x), int(offset_y), int(width), int(height))

    def _ensure_window_onscreen(self, offset: Vec2f, size: Vec2f) -> list[int, int, int, int]:
        """
        Ensures that the window is sufficiently visible on at least one screen.

        If less than 20% of the window's area is visible across all available
        screens, its position and size are reset to be centered on the
        primary screen. Otherwise, the original coordinates are returned.

        Returns:
            A list containing the validated [x, y, width, height].
        """
        # define the minimum visibility required to keep the current position
        min_visibility_threshold = 0.20

        # create a QRect for the proposed window geometry.
        window_rect = QRect(int(offset.x), int(offset.y), int(size.x), int(size.y))
        window_area = window_rect.width() * window_rect.height()

        # handle invalid size (e.g., width/height is zero or negative)
        if window_area <= 0:
            print("Window has invalid size. Resetting to default.")
            # trigger the reset logic by treating it as 0% visible
            visibility_ratio = 0

        else:
            # calculate the total visible area by checking against all screens
            total_visible_area = 0
            screens = QGuiApplication.screens()
            for screen in screens:
                # use availableGeometry() to account for taskbars, docks, etc
                screen_geometry = screen.availableGeometry()

                # find the area of intersection between the window and the screen
                intersection = window_rect.intersected(screen_geometry)

                # the intersection rect will have a non-positive width/height if no overlap
                if not intersection.isEmpty():
                    total_visible_area += intersection.width() * intersection.height()

            visibility_ratio = total_visible_area / window_area

        # check if the visibility ratio is below the threshold
        if visibility_ratio < min_visibility_threshold:
            # if the window is mostly off-screen, reset its position and size
            print("Window is too far offscreen. Resetting position.")

            # get the primary screen to center the window on
            primary_screen = QGuiApplication.primaryScreen()
            if not primary_screen:
                # extremely rare case but good to have a fallback
                return [100, 100, 1024, 768]

            screen_rect = primary_screen.availableGeometry()

            # set a new, sensible default size (e.g: 75% of the screen)
            new_width = int(screen_rect.width() * 0.75)
            new_height = int(screen_rect.height() * 0.75)

            # calculate coordinates to center the new window
            new_x = screen_rect.x() + (screen_rect.width() - new_width) // 2
            new_y = screen_rect.y() + (screen_rect.height() - new_height) // 2

            return [new_x, new_y, new_width, new_height]

        else:
            # the window is sufficiently visible, so return the original coordinates
            return [int(offset.x), int(offset.y), int(size.x), int(size.y)]

    def _get_config_data(self, is_retry: bool = False) -> Optional[dict]:
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

                    if config:
                        return config

            # not found? try again
            except (json.JSONDecodeError, KeyError, FileNotFoundError) as exc:
                # corrupt or wrong structure
                print(f"Invalid config file at '{path}': {exc}")

                if is_retry:
                    print("ERROR: Configuration fix failed. Aborting.")
                    return None

                print("Attempting to repair configuration...")
                self._ensure_valid_configs()

                return self._get_config_data(True)

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
