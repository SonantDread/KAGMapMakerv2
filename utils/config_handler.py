"""
Handles the configuration saving and loading for the app.
"""
import json

from PyQt6.QtWidgets import QMainWindow

from utils.file_handler import FileHandler
from utils.vec2f import Vec2f


class ConfigFile:
    """
    Stores the name, values, and path of a configuration file.
    """
    def __init__(self, name: str, values: str, path: str):
        self.name = name
        self.cfg = values
        self.path = path

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

class ConfigHandler(metaclass=SingletonMeta):
    """
    Handles the configuration saving and loading for the app.
    """
    def __init__(self):
        self.fh = FileHandler()
        self.default_config_path = self.fh.get_default_config_path()
        self.config_path = self.fh.get_config_path()
        self.configs = {}
        self._iterator = None

    def save_window_config(self, window: QMainWindow) -> None:
        """
        Saves the configuration of the application to a JSON file.

        Args:
            cfg (QMainWindow): The window to save the configuration of.

        Returns:
            None
        """
        try:
            # load user's config
            with open(self.config_path, 'r', encoding = 'utf-8') as f:
                cfg = json.load(f)

        except FileNotFoundError:
            try:
                # load default config
                with open(self.default_config_path, 'r', encoding = 'utf-8') as f:
                    cfg = json.load(f)

            except FileNotFoundError as exc:
                raise SystemExit("Could not find user config or default config file.") from exc

        # check if window config is empty
        if not cfg.get("window"):
            raise SystemExit("Could not find user config or default config file.")

        # assume any error below this point is fault of user for
        # not having a config file or having an invalid config file
        win_size = self.__get_window_size(window)
        win_offset = self.__get_window_offset(window)

        cfg['window']['size'] = {
            'width': win_size.x,
            'height': win_size.y
        }

        cfg['window']['offset'] = {
            'x': win_offset.x,
            'y': win_offset.y
        }

        with open(self.config_path, 'w', encoding = 'utf-8') as f:
            json.dump(cfg, f, indent = 4)

    def load_window_config(self, window: QMainWindow) -> None:
        """
        Loads the configuration of the window from a file and
        applies it to the application.

        Args:
            window (QMainWindow): The window to apply the configuration to.

        Returns:
            None
        """
        window_cfg_file = self._get_config_file('window', self.fh.get_config_path())
        if window_cfg_file is None:
            raise FileNotFoundError("Window configuration not found.")

        window_cfg = window_cfg_file.cfg.get("window", {})
        window.setWindowTitle("KAG Map Maker")

        offset = Vec2f()
        offset.x = window_cfg.get("offset", -1).get("x", 0)
        offset.y = window_cfg.get("offset", -1).get("y", 0)

        size = Vec2f()
        size.x = window_cfg.get("size", -1).get("width", 1920 * 0.75)
        size.y = window_cfg.get("size", -1).get("height", 1080 * 0.75)

        # if invalid values, do nothing instead
        if(offset.x == -1 or offset.y == -1 or size.x == -1 or size.y == -1):
            return None

        window.setGeometry(offset.x, offset.y, size.x, size.y)

    def save_config_file(self, name: str) -> None:
        """
        Saves a config to a file.

        Args:
            name (str): The name of the configuration to save.

        Returns:
            None
        """
        cfg = self._get_config_file(name).cfg
        if cfg == {} or cfg is None:
            return

        with open(self.config_path, 'w', encoding = 'utf-8') as f:
            json.dump(cfg, f, indent = 4)

    def unload_config(self, name: str) -> None:
        """
        Unloads a config by its loaded name.

        Args:
            name (str): The name of the configuration to unload.

        Returns:
            None
        """
        if name in self.configs:
            del self.configs[name]

    def update_config_item(self, cfg_file: str, item: str, val: any) -> None:
        if self._get_config_file(cfg_file) is None:
            raise FileNotFoundError(f"Configuration file {cfg_file} not found.")

        cfg = self._get_cfg(cfg_file)
        # split into config paths
        keys = item.split(".")
        for key in keys:
            cfg = cfg[key]

        cfg = val

    def load_config_file(self, file_path: str, name: str) -> None:
        try:
            with open(file_path, 'r', encoding = 'utf-8') as f:
                print('cfg')
                cfg = json.load(f)

        except FileNotFoundError as exc:
            raise FileNotFoundError("File not found.") from exc

        self.configs.update({name: ConfigFile(name, cfg, file_path)})

    def get_config_item(self, name: str, item: str) -> any:
        cfg = self._get_cfg(name)
        if cfg is None:
            raise NotImplementedError("Config item not found.")

        keys = item.split(".")
        for key in keys:
            cfg = cfg.get(key)
            if cfg is None:
                raise NotImplementedError(f"Configuration item '{item}' not found in '{name}'.")

        return cfg

    def reload_config_file(self, file: str) -> None:
        with open(file, 'r', encoding = 'utf-8') as f:
            cfg = json.load(f)

        self._get_config_file(file).cfg = cfg

    def get_modded_data(self, config_name: str) -> list:
        cfg_list = self._get_cfg(config_name)
        if not cfg_list:
            raise FileNotFoundError(f"Configuration '{config_name}' not found.")

        # use only the first dictionary in the list
        cfg = cfg_list[0]

        sprite = cfg.get("sprite", {})
        properties = sprite.get("properties", {})

        data = [
            cfg.get("type"),
            cfg.get("name"),
            cfg.get("displayName"),
            cfg.get("section_name"),
            sprite.get("image"),
            sprite.get("z_index"),
            properties.get("is_rotatable"),
            properties.get("can_swap_teams"),
            properties.get("team"),
            sprite.get("offset"),
            cfg.get("search_keywords")
        ]

        return data

    def _get_config_file(self, cfg: str, fp = None) -> ConfigFile:
        if cfg in self.configs:
            return self.configs.get(cfg)

        # attempt to load config
        if fp is not None:
            self.load_config_file(fp, cfg)
            return self.configs.get(cfg)

        # config not found
        return None

    def _get_cfg(self, name: str, fp: str = None) -> dict:
        cfg_file = self._get_config_file(name, fp)
        return cfg_file.cfg if cfg_file else None

    def __get_window_size(self, window: QMainWindow):
        size = window.size()
        return Vec2f(size.width(), size.height())

    def __get_window_offset(self, window: QMainWindow):
        offset = window.geometry()
        return Vec2f(offset.x(), offset.y())