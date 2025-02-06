"""
Handles configuration loading and custom item management for the application.
"""
import json
from PyQt6.QtWidgets import QMainWindow

from utils.file_handler import FileHandler
from utils.vec2f import Vec2f
from base.citem import CItem

class ConfigHandler:
    """Handles configuration loading and management for the application."""

    def __init__(self):
        self.fh = FileHandler()
        self.readonly_config_path = self.fh.paths.get("default_config_path")
        self.config_path = self.fh.paths.get("config_path")
        self.loaded_citem_configs: dict[str, list[CItem]] = {}
        self.loaded_configs: dict[str, dict] = {}

    def load_config(self, path: str) -> None:
        pass # todo: implement this so we can implement a way to find the path to kag

    def load_modded_items(self, file_path: str) -> list[CItem]:
        """
        Loads modded items from a single JSON file.

        Args:
            file_path (str): Path to the JSON file containing modded item definitions

        Returns:
            List[CItem]: List of parsed modded items

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the JSON is invalid
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            items = [CItem.from_dict(item_data, file_path) for item_data in data]
            config_name = self.fh.get_file_truename(file_path)
            self.loaded_citem_configs[config_name] = items
            return items

        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Could not find modded item file: {file_path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in modded item file: {file_path}") from exc

    def get_items_from_mod(self, mod_folder_name: str) -> list[CItem]:
        """
        Retrieves all items from a specific mod folder.

        Args:
            mod_folder_name (str): Name of the mod folder to get items from

        Returns:
            List[CItem]: List of items from the specified mod folder
        """
        items = []
        for config_items in self.loaded_citem_configs.values():
            items.extend([
                item for item in config_items
                if item.mod_info.folder_name == mod_folder_name
            ])
        return items

    def get_loaded_file_items(self, file_path: str) -> list[CItem]:
        """
        Retrieves all items from a specific loaded file.

        Args:
            file_path (str): Path to the file to get items from

        Returns:
            List[CItem]: List of items from the specified file
        """
        config_name = self.fh.get_file_truename(file_path)
        return self.loaded_citem_configs.get(config_name, [])

    def get_loaded_mod_folders(self) -> list[str]:
        """
        Returns a list of all unique mod folder names that have been loaded.

        Returns:
            List[str]: List of unique mod folder names
        """
        mod_folders = set()
        for items in self.loaded_citem_configs.values():
            for item in items:
                mod_folders.add(item.mod_info.folder_name)
        return sorted(list(mod_folders))

    # updated old window loading code
    # todo: this should probably be updated
    def _get_config_file(self, config_type: str, config_path: str = None):
        """
        Retrieve configuration file, with fallback to default config.

        Args:
            config_type (str): Type of configuration to retrieve (e.g., 'window')
            config_path (str, optional): Path to user configuration file

        Returns:
            dict: Configuration dictionary
            None: If no valid configuration is found
        """
        try:
            # try to load user configuration
            if config_path:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_cfg = json.load(f)
                    if config_type in user_cfg and user_cfg.get(config_type):
                        return type('ConfigFile', (), {'cfg': user_cfg})()

            # fallback to readonly (default) configuration
            with open(self.readonly_config_path, 'r', encoding='utf-8') as f:
                default_cfg = json.load(f)
                if config_type in default_cfg and default_cfg.get(config_type):
                    return type('ConfigFile', (), {'cfg': default_cfg})()

            return None

        except (FileNotFoundError, json.JSONDecodeError) as exc:
            print(f"Error loading configuration: {exc}")
            return None

    def save_window_config(self, window: QMainWindow) -> None:
        """
        Saves the current window configuration to the user's config file.

        Args:
            window (QMainWindow): The window to save configuration for.

        Raises:
            SystemExit: If unable to load or create a configuration file.
        """
        try:
            # attempt to load existing configuration
            with open(self.config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # if user config doesn't exist, load default config
            try:
                with open(self.readonly_config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                raise SystemExit("Could not find or load configuration file.") from exc

        # ensure 'window' section exists
        if 'window' not in cfg:
            cfg['window'] = {}

        # get window dimensions and position
        win_size = self.__get_window_size(window)
        win_offset = self.__get_window_offset(window)

        # update configuration
        cfg['window']['size'] = {
            'width': int(win_size.x),
            'height': int(win_size.y)
        }
        cfg['window']['offset'] = {
            'x': int(win_offset.x),
            'y': int(win_offset.y)
        }

        # save updated configuration
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=4)
        except IOError as exc:
            print(f"Error saving window configuration: {exc}")

    def load_window_config(self, window: QMainWindow) -> None:
        """
        Loads and applies window configuration from the config file.

        Args:
            window (QMainWindow): The window to apply configuration to.

        Raises:
            FileNotFoundError: If no valid configuration is found.
        """
        # set default window title
        window.setWindowTitle("KAG Map Maker")

        # attempt to retrieve window configuration
        window_cfg_file = self._get_config_file('window', self.config_path)
        if window_cfg_file is None:
            # if no user config, try default config
            window_cfg_file = self._get_config_file('window', self.readonly_config_path)

        if window_cfg_file is None:
            # no configuration found, use default sizing
            default_width = int(1920 * 0.75)
            default_height = int(1080 * 0.75)
            window.resize(default_width, default_height)
            return

        # extract configuration
        window_cfg = window_cfg_file.cfg.get("window", {})

        # default values with fallback
        offset_x = window_cfg.get("offset", {}).get("x", 100)
        offset_y = window_cfg.get("offset", {}).get("y", 100)

        size_width = window_cfg.get("size", {}).get("width", int(1920 * 0.75))
        size_height = window_cfg.get("size", {}).get("height", int(1080 * 0.75))

        # set window geometry
        window.setGeometry(
            int(offset_x),
            int(offset_y),
            int(size_width),
            int(size_height)
        )

    def __get_window_size(self, window: QMainWindow):
        size = window.size()
        return Vec2f(size.width(), size.height())

    def __get_window_offset(self, window: QMainWindow):
        offset = window.geometry()
        return Vec2f(offset.x(), offset.y())

"""
config_handler = ConfigHandler()

# load items from a mod file
mod_items = config_handler.load_modded_items("mods/custom_mod/items.json")

# get the mod folder name for a specific item
first_item = mod_items[0]
print(f"Item {first_item.display_name} is from mod folder: {first_item.mod_info.folder_name}")

# get all items from a specific mod folder
mod_folder_items = config_handler.get_items_from_mod("custom_mod")

# get a list of all loaded mod folders
mod_folders = config_handler.get_loaded_mod_folders()
print("Loaded mod folders:", mod_folders)
"""
