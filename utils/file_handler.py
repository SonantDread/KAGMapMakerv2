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
        # path to the main folder
        default_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        vanilla_items = os.path.abspath(os.path.join(default_path, "base", "Items"))
        self.paths = {
            "default_path": default_path,
            "world_path": os.path.abspath(os.path.join(default_path, "base", "Sprites", "Default", "world.png")),
            "vanilla_items": vanilla_items,
            "mapmaker_images": os.path.abspath(os.path.join(default_path, "base", "Sprites", "MapMaker")),
            "config_path": os.path.abspath(os.path.join(default_path, "settings", "config.json")),
            "default_config_path": os.path.abspath(os.path.join(default_path, "settings", "readonly_config.json")),
            "gui_modules_path": os.path.abspath(os.path.join(default_path, "core", "modules")),
            "maps_path": os.path.abspath(os.path.join(default_path, "Maps")),
            "modded_items_path": os.path.abspath(os.path.join(default_path, "Modded")),
            "tilelist_path": os.path.abspath(os.path.join(vanilla_items, "tiles.json")),
            "bloblist_path": os.path.abspath(os.path.join(vanilla_items, "blobs.json")),
            "otherlist_path": os.path.abspath(os.path.join(vanilla_items, "others.json")),
            "team_palette_path": os.path.abspath(os.path.join(default_path, "base", "Sprites", "Default", "TeamPalette.png")),
        }

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

    def get_maps_path(self):
        """
        Returns the path to the maps directory.

        Returns:
            str: Returns the path to the maps directory.
        """
        path = self.paths.get("maps_path")
        if not self.does_path_exist(path):
            os.mkdir(path)

        return path

    def does_sprite_exist(self, name: str, fp: str = None) -> bool:
        """
        Checks if a sprite with the given name exists in the sprites directory.

        Args:
            name (str): The name of the sprite to check for.
            fp (str): The path to search for the sprite. If None, the default path is used.

        Returns:
            bool: True if the sprite exists, False otherwise.
        """
        if not isinstance(name, str):
            name = str(name)

        if fp is None:
            fp = os.path.join(self.paths.get("default_path"), "base", "Sprites")

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

    def get_vanilla_items_paths(self) -> list[str]:
        return self._get_files_from_dir(self.paths.get("vanilla_items"), lambda x: True)

    def get_modded_items_paths(self) -> list[str]:
        return self._get_files_from_dir(self.paths.get("modded_items_path"), 
                        lambda x: x.split("\\")[-1] != "_ExampleMod")

    def _get_files_from_dir(self, fp: str, condition: callable) -> list[str]:
        files = []
        for r, _, fn in os.walk(fp):
            files.extend([os.path.join(r, f.strip()) for f in fn if f.strip().endswith(".json") and condition(r)])

        return files
