from typing import Union

from utils.config_handler import ConfigHandler
from utils.file_handler import FileHandler
from core.communicator import Communicator

# indexes in KAG but will also use here to try to keep it similar,
# can be changed later if its a problem
# -600 = behind background
# -500 = in front of background, behind shops
# -100 = in front of shops, behind players
#  100 = in front of players, behind solid tiles
#  500 = in front of solid tiles (and basically everything else except trees and spikes)
# 1500 = in front of spikes

class CItemList:
    def __init__(self) -> None:
        self.file_handler = FileHandler()
        self.config_handler = ConfigHandler()

        self.vanilla_tiles: list['CItem'] = self.__setup_tiles()
        Communicator().picked_tiles = self.__get_selected_tiles()
        self.vanilla_blobs: list['CItem'] = self.__setup_blobs()
        self.vanilla_others: list['CItem'] = self.__setup_others()
        tiles, blobs, other = self.__setup_modded_items()
        self.modded_tiles: list['CItem'] = tiles
        self.modded_blobs: list['CItem'] = blobs
        self.modded_others: list['CItem'] = other
        all_items = [
            self.vanilla_tiles,
            self.vanilla_blobs,
            self.vanilla_others,
            self.modded_tiles,
            self.modded_blobs,
            self.modded_others
        ]
        self.all_items = [item for sublist in all_items for item in sublist]

        self.pixel_color_map: dict[tuple[int, int, int, int], 'CItem'] = self.__create_pixel_color_map()
        # todo: these all should be sorted

        # -----
        # "Other" tab:
        # necromancer_teleport
        # mook_knight
        # mook_archer
        # mook_spawner
        # mook_spawner_10
        # -----

    def does_tile_exist(self, name: Union[str, 'CItem']) -> bool:
        if isinstance(name, CItem):
            name = name.name_data.name

        if any(item.name_data.name == name for item in self.vanilla_tiles):
            return True

        if any(item.name_data.name == name for item in self.modded_tiles):
            return True

        return False

    def does_blob_exist(self, name: Union[str, 'CItem']) -> bool:
        if isinstance(name, CItem):
            name = name.name_data.name

        if any(item.name_data.name == name for item in self.vanilla_blobs):
            return True

        if any(item.name_data.name == name for item in self.modded_blobs):
            return True

        return False

    def does_other_exist(self, name: Union[str, 'CItem']) -> bool:
        if isinstance(name, CItem):
            name = name.name_data.name

        if any(item.name_data.name == name for item in self.vanilla_others):
            return True

        if any(item.name_data.name == name for item in self.modded_others):
            return True

        return False

    def get_item_by_name(self, name: str) -> 'CItem':
        name = str(name)
        for item in self.all_items:
            if item.name_data.name == name:
                return item

    def get_item_by_color(self, color: tuple[int, int, int, int]) -> 'CItem':
        return self.pixel_color_map.get(color)

    def __setup_modded_items(self) -> tuple[list['CItem'], list['CItem'], list['CItem']]:
        fh, ch = FileHandler(), ConfigHandler()
        items = fh.get_modded_items_paths()
        items = [item for item in items if not item.split("\\")[-1].strip().startswith("_")]

        tiles, blobs, other = [], [], []
        for mod in items:
            for item in ch.load_modded_items(mod):
                if item.type == "tile":
                    tiles.append(item)
                elif item.type == "blob":
                    blobs.append(item)
                else:
                    other.append(item)

        return tiles, blobs, other

    def __create_pixel_color_map(self) -> dict[tuple[int, int, int, int], 'CItem']:
        color_map = {}
        for item in self.all_items:
            if item is None or not hasattr(item.pixel_data, 'colors'):
                continue

            for key, color in item.pixel_data.colors.items():
                # skip non-color entries
                if not isinstance(color, list) or len(color) != 4:
                    continue

                split = key.split("_")
                rotation, team = split[0][len("rotation"):], split[1][len("team"):]

                item = item.copy()
                item.sprite.rotation = int(rotation)
                item.swap_team(int(team))

                color_tuple = tuple(color) # (a, r, g, b)
                color_map[color_tuple] = item

        return color_map

    def __setup_tiles(self) -> list['CItem']:
        path = self.file_handler.paths.get("tilelist_path")
        items = self.config_handler.load_modded_items(path)
        # swap sky from being last to first
        items.insert(0, items.pop())
        return items

    def __setup_blobs(self) -> list['CItem']:
        path = self.file_handler.paths.get("bloblist_path")
        return self.config_handler.load_modded_items(path)

    def __setup_others(self) -> list['CItem']:
        path = self.file_handler.paths.get("otherlist_path")
        return self.config_handler.load_modded_items(path)

    def __get_selected_tiles(self) -> list['CItem']:
        t = self.vanilla_tiles
        tiles = []
        for item in t:
            if item.name_data.name in ("tile_ground", "sky"):
                tiles.append(item)

        return tiles
