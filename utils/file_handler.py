"""
Used to handle file paths and file loading.
"""
import os
from pathlib import Path
import json
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

        config_path = join_paths(root, "settings", "config.json")
        default_config_path = join_paths(root, "settings", "readonly_config.json")
        maps_path = join_paths(root, "Maps")

        self.paths = {
            "default_path": root,
            "world_path": join_paths(sprites, "Default", "world.png"),
            "vanilla_items": vanilla_items,
            "mapmaker_images": join_paths(sprites, "MapMaker"),
            "config_path": config_path,
            "default_config_path": default_config_path,
            "maps_path": maps_path,
            "autosave_path": join_paths(maps_path, "Autosave"),
            "modded_items_path": join_paths(root, "Modded"),
            "tilelist_path": join_paths(vanilla_items, "tiles.json"),
            "bloblist_path": join_paths(vanilla_items, "blobs.json"),
            "otherlist_path": join_paths(vanilla_items, "others.json"),
            "merge_items_path": join_paths(vanilla_items, "merge_items.json"),
            "team_palette_path": join_paths(sprites, "Default", "TeamPalette.png"),
            "kag_path": self.get_kag_path(config_path, default_config_path), # todo: this should probably save on exit
            "autostart_script_path": join_paths(root, "base", "MapMaker_Autostart.as"),
        }

    def get_kag_autostart_path(self, path: str) -> str:
        """
        Provides the path to where the MapMaker_Autostart.as script should
        be placed in the user's KAG installation.

        Returns:
            str: The path to the KAG autostart script.
        """
        return os.path.join(path, "Base", "Scripts", "MapMaker_Autostart.as")

    def get_kag_maps_path(self, path: str) -> str:
        """
        Provides the path to where the MapMaker_Autostart.as script should
        be placed in the user's KAG installation.

        Returns:
            str: The path to the KAG autostart script.
        """
        return os.path.join(path, "Base", "Maps", "MapMaker_Map.png")

    def get_kag_path(self, config_path: str, readonly_config_path: str) -> str:
        """
        Find's the user's KAG installation path.

        Returns:
            str: The path to the KAG installation, or an empty string if not found.
        """
        kag_path = None
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config_data = json.load(f)
                kag_path = config_data.get("kag_path")

            except json.JSONDecodeError:
                pass

        if kag_path is None:
            with open(readonly_config_path, 'r', encoding='utf-8') as f:
                try:
                    config_data = json.load(f)
                    kag_path = config_data.get("kag_path")

                except json.JSONDecodeError:
                    pass

        if kag_path is not None:
            kag_path = str(kag_path).strip('"').strip()
            return os.path.dirname(kag_path)

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
