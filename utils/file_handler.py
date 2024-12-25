"""
Used to handle file paths and file loading.
"""
import os
from pathlib import Path

class FileHandler:
    """
    Used to handle file paths and file loading.
    """
    def __init__(self) -> None:
        # path to the map maker folder
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        self.world_path = os.path.join(self.base_path, "base", "Sprites", "Default", "world.png")
        self.mapmaker_images = os.path.join(self.base_path, "base", "Sprites", "MapMaker")

        self.config_path = os.path.join(self.base_path, "settings", "config.json")
        self.default_config_path = os.path.join(self.base_path, "settings", "readonly_config.json")
        self.gui_modules_path = os.path.join(self.base_path, "core", "modules")
        self.maps_path = os.path.join(self.base_path, "Maps")
        self.modded_items_path = os.path.join(self.base_path, "Modded")

    def does_path_exist(self, path: str):
        """
        Checks if a given file path exists.

        Args:
            path (str): The file path to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        if not isinstance(path, str):
            path = str(path)

        return os.path.exists(path)

    def get_world_path(self):
        """
        Returns the path to the world file.

        Returns:
            str: The path to the world file.
        """
        return self.world_path

    def get_config_path(self):
        """
        Returns the path to the configuration file.

        Returns:
            str: The path to the configuration file.
        """
        return self.config_path

    def get_default_config_path(self):
        """
        Returns the path to the default configuration file.

        Returns:
            str: The path to the default configuration file.
        """
        return self.default_config_path

    def get_maps_path(self):
        """
        Returns the path to the maps directory.

        Returns:
            str: Returns the path to the maps directory.
        """
        if not self.does_path_exist(self.maps_path):
            os.mkdir(self.maps_path)

        return self.maps_path

    def get_gui_modules_path(self):
        """
        Returns the path to the modules directory for the GUI.

        Returns:
            str: Returns the path to the modules directory for the GUI.
        """
        return self.gui_modules_path

    def get_modded_items_path(self) -> str:
        """
        Returns the path to the modded items.

        Returns:
            str: Returns the path to the modded items.
        """
        return self.modded_items_path

    def does_sprite_exist(self, name: str, fp: str = None) -> bool:
        """
        Checks if a sprite with the given name exists in the sprites directory.

        Args:
            name (str): The name of the sprite to check for.

        Returns:
            bool: True if the sprite exists, False otherwise.
        """
        if not isinstance(name, str):
            name = str(name)

        if fp is None:
            fp = os.path.join(self.base_path, "base", "Sprites")

        for _, _, files in os.walk(fp):
            if name in files:
                return True
        return False

    def get_file_truename(self, fp: str) -> str:
        """
        Returns the actual name of the file provided
        
        Args:
            fp (str): The filepath
            
        Returns:
            str: The name of the file
        """
        return Path(fp).name.split(".")[0]

    def get_modded_item_path(self, name: str, fp: str) -> str:
        """
        Returns the full path to the modded item with the given name in the given path

        Args:
            name (str): The name of the modded item to find
            fp (str): The path to search for the modded item

        Returns:
            str: The full path to the modded item if found, None otherwise
        """

        for root, _, files in os.walk(fp):
            if name in files:
                return os.path.join(root, name)

        return None
