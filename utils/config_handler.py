"""
Handles configuration loading and custom item management for the application.
"""
import json

from utils.file_handler import FileHandler
from base.citem import CItem

class ConfigHandler:
    """
    Handles configuration loading and management for the application.
    """
    def __init__(self):
        self.fh = FileHandler()
        self.readonly_config_path = self.fh.paths.get("default_config_path")
        self.config_path = self.fh.paths.get("config_path")
        self.loaded_citem_configs: dict[str, list[CItem]] = {}
        self.loaded_configs: dict[str, dict] = {}

    def load_config_file(self, config_path: str, config_name: str) -> dict:
        """
        Loads a configuration file and stores it in loaded_configs.

        Args:
            config_path (str): Path to the configuration file
            config_name (str): Name of the configuration file

        Returns:
            dict: The loaded configuration data or None if loading fails
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self.loaded_configs[config_name] = config_data
                return config_data

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading configuration file {config_name}: {e}")
            return None

    def get_config_item(self, config_name: str, item_key: str) -> any:
        """
        Retrieves a specific item from a loaded configuration.

        Args:
            config_name (str): Name of the configuration file
            item_key (str): Key to retrieve from the configuration

        Returns:
            any: The value associated with the key, or None if not found
        """
        config = self.loaded_configs.get(config_name)
        if config is None:
            return None

        return config.get(item_key)

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
