"""
Handles the configuration saving and loading for the app.
"""
import json

from PyQt6.QtWidgets import QMainWindow

from utils.file_handler import FileHandler
from utils.vec import Vec2f

class SingletonMeta(type):
    """
    Used to share code between all instances of the class.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class ConfigHandler(metaclass = SingletonMeta):
    """
    Handles the configuration saving and loading for the app.
    """
    def __init__(self):
        self.fh = FileHandler()
        self.config_path = self.fh.get_config_path()
        self.default_config_path = self.fh.get_default_config_path()

    def save_config(self, cfg: QMainWindow) -> None:
        """
        Saves the configuration of the QMainWindow `cfg` to a JSON file.

        Args:
            cfg (QMainWindow): The QMainWindow object whose configuration is to be saved.

        Returns:
            None
        """
        try:
            with open(self.config_path, 'r', encoding = 'utf-8') as f:
                config = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        # update window size and offset
        if 'window' not in config:
            config['window'] = {}

        window_size = self.__get_window_size(cfg)
        window_offset = self.__get_window_offset(cfg)

        config['window']['size'] = {
            'width': window_size.x,
            'height': window_size.y
        }
        config['window']['offset'] = {
            'x': window_offset.x,
            'y': window_offset.y
        }

        # save updated config back to the file
        with open(self.config_path, 'w', encoding = 'utf-8') as f:
            json.dump(config, f, indent = 4)
        
        print("Config saved to file.", f'x: {window_offset.x}, y: {window_offset.y}')

    def save_config_item(self, item: str, val):
        """
        Saves a specific configuration item to the JSON file.

        Args:
            item (str): The name of the item to save.
            val: The value to save for the item.

        Returns:
            None
        """
        try:
            with open(self.config_path, 'r', encoding = 'utf-8') as f:
                config = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        # update the specific item
        keys = item.split('.')
        current = config
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = val

        # save the updated config back to the file
        with open(self.config_path, 'w', encoding = 'utf-8') as f:
            json.dump(config, f, indent = 4)

    def get_config_item(self, name: str):
        """
        Retrieves a specific configuration item from the JSON file.

        Args:
            name (str): The name of the item to retrieve.

        Returns:
            The value of the configuration item, or None if not found.
        """
        try:
            with open(self.config_path, 'r', encoding = 'utf-8') as f:
                config = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            return None

        keys = name.split('.')
        current = config
        for key in keys:
            if key not in current:
                return None
            current = current[key]
        return current

    def _reset_config_item(self, item: str):
        """
        Resets a specific configuration item to its default value.

        Args:
            item (str): The name of the item to reset.

        Returns:
            None
        """
        try:
            with open(self.default_config_path, 'r', encoding = 'utf-8') as f:
                default_config = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Could not load default config from {self.default_config_path}")
            return

        try:
            with open(self.config_path, 'r', encoding = 'utf-8') as f:
                config = json.load(f)

        except (FileNotFoundError, json.JSONDecodeError):
            config = {}

        # get default value
        keys = item.split('.')
        default_value = default_config
        for key in keys:
            if key not in default_value:
                print(f"Item '{item}' not found in default config")
                return
            default_value = default_value[key]

        # update config with the default value
        current = config
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = default_value

        # Save the updated config back to the file
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)

    def load_config(self, window: QMainWindow) -> None:
        """
        Loads the configuration and applies it to the given QMainWindow.

        Args:
            window (QMainWindow): The window to apply the configuration to.

        Returns:
            None
        """
        try:
            with open(self.config_path, 'r', encoding = 'utf-8') as f:
                cfg = json.load(f)

        except FileNotFoundError:
            print("Could not find the config file. Attempting to load default.")
            try:
                with open(self.default_config_path, 'r', encoding = 'utf-8') as f:
                    cfg = json.load(f)

            except FileNotFoundError as exc:
                raise FileNotFoundError("Could not find config or default config file.") from exc

        except json.JSONDecodeError:
            print("Could not load config.")
            return None

        # default, can't change
        window.setWindowTitle('KAG Map Maker')
        cfg = cfg.get('window', {})

        offset = Vec2f(cfg.get('offset', {}).get('x', 0), cfg.get('offset', {}).get('y', 0))
        size = Vec2f(cfg.get('size', {}).get('width', 1920), cfg.get('size', {}).get('height', 1080))

        window.setGeometry(offset.x, offset.y, size.x, size.y)

    def __get_window_size(self, window: QMainWindow):
        size = window.size()
        return Vec2f(size.width(), size.height())

    def __get_window_offset(self, window: QMainWindow):
        offset = window.geometry()
        return Vec2f(offset.x(), offset.y())
