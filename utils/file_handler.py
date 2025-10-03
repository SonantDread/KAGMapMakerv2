"""
Used to handle file paths and file loading.
"""
import os
from pathlib import Path

class FileHandler:
    """
    Handles consistent file paths across the project.
    """
    def __init__(self) -> None:
        join_paths = lambda *parts: os.path.abspath(os.path.join(*parts))
        # main folder path
        root = join_paths(os.path.dirname(os.path.abspath(__file__)), "..")
        vanilla_items = join_paths(root, "base", "Items")
        sprites = join_paths(root, "base", "Sprites")

        self.paths = {
            "default_path": root,
            "world_path": join_paths(sprites, "Default", "world.png"),
            "vanilla_items": vanilla_items,
            "mapmaker_images": join_paths(sprites, "MapMaker"),
            "config_path": join_paths(root, "settings", "config.json"),
            "default_config_path": join_paths(root, "settings", "readonly_config.json"),
            "maps_path": join_paths(root, "Maps"),
            "modded_items_path": join_paths(root, "Modded"),
            "tilelist_path": join_paths(vanilla_items, "tiles.json"),
            "bloblist_path": join_paths(vanilla_items, "blobs.json"),
            "otherlist_path": join_paths(vanilla_items, "others.json"),
            "merge_items_path": join_paths(vanilla_items, "merge_items.json"),
            "team_palette_path": join_paths(sprites, "Default", "TeamPalette.png"),
        }

    def does_path_exist(self, path: str) -> bool:
        """
        Normalizes the provided path and checks if it exists.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        if not isinstance(path, str):
            path = str(path)

        return os.path.exists(path)

    def get_maps_path(self) -> str:
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

        Returns:
            str: The name of the file
        """
        return Path(fp).name.split(".")[0]

    def get_modded_item_path(self, name: str, fp: str) -> str:
        """
        Returns the full path to the modded item with the given name in the given path

        Returns:
            str: The full path to the modded item if found, None otherwise
        """
        for root, _, files in os.walk(fp):
            if name in files:
                return os.path.join(root, name)

        return None

    def get_modded_items_paths(self, fp: str = None) -> list[str]:
        """
        Returns a list of all modded item file paths in the modded items directory.

        Returns:
            list[str]: A list of file paths to modded items.
        """
        if fp is None:
            fp = self.paths.get("modded_items_path")

        blacklisted_folders = ["_ExampleMod"]
        files: list[str] = []

        for root, _, filenames in os.walk(fp):
            if any(blacklisted in root.split(os.sep) for blacklisted in blacklisted_folders):
                continue

            for f in filenames:
                if f.strip().endswith(".json"):
                    files.append(os.path.join(root, f.strip()))

        return files
