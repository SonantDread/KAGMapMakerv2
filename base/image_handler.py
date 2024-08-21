"""
Handles all image loading.
"""
import inspect
import os
from typing import Union

from PIL import Image
from PyQt6.QtGui import QPixmap
from utils.file_handler import FileHandler

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

class ImageHandler(metaclass = SingletonMeta):
    """
    Used to handle all image loading.
    """
    def __init__(self) -> None:
        self.file_handler = FileHandler()
        self.loaded_images = {}
        self.tile_indexes = { # should just be from ctile_list but circular import error
            "tile_empty": int(0),
            "tile_ground": int(16),
            "tile_grassy_ground": int(23),
            "tile_grass": int(25),
            "tile_ground_back": int(32),
            "tile_castle": int(48),
            "tile_castle_back": int(64),
            "tile_gold": int(80),
            "tile_stone": int(96),
            "tile_bedrock": int(106),
            "tile_wood_back": int(173),
            "tile_wood": int(196),
            "tile_thickstone": int(208),
            "tile_castle_moss": int(224),
            "tile_castle_back_moss": int(227),
            "sky": int(400),
        }
        exec_path = os.path.dirname(os.path.realpath(__file__))
        self.basepath = os.path.join(exec_path, "Sprites", "MapMaker")

    def get_image(self, name: Union[str, int]) -> QPixmap:
        """
        Retrieves an image based on the provided name or index.

        Args:
            name (Union[str, int]): The name or index of the image to retrieve.

        Returns:
            QPixmap: The retrieved image, or None if the image does not exist.
        """
        if isinstance(name, int): # handle input of index for a block
            name = self._get_tile_name_by_index(name)

        if self.loaded_images.get(name) is not None:
            return self.loaded_images.get(name)

        # image doesnt exist
        img = self._get_item_png_by_name(name)

        if img is not None:
            return img

        line = inspect.currentframe().f_lineno
        fn = os.path.basename(__file__)
        print(f"Image not found: {name}. Unable to load in line {line} of {fn}")
        return None

    def _get_item_png_by_name(self, name: str) -> QPixmap:
        if name in self.tile_indexes:
            return self._get_tile_png_by_index(self.tile_indexes[name])

        return self._load_image(name)

    def _load_image(self, name: str) -> QPixmap:
        path = os.path.join(self.basepath, name + ".png")

        if not self.file_handler.does_path_exist(path):
            # todo: uncomment this when water_backdirt is available
            # raise FileNotFoundError(f"File not found: {path}")
            return None

        img = Image.open(path)
        img.convert("RGBA")
        img.load()

        self.loaded_images.update({name: img.toqpixmap()})
        return img.toqpixmap()

    def _get_tile_png_by_index(self, index: int) -> QPixmap:
        world = self.file_handler.get_world_path()
        image = Image.open(world)
        image = image.convert("RGBA") # prevent errors with alpha translation

        width = image.size[0]
        sections_w = width // 8

        # calculate coordinates for the specified index
        x = (index % sections_w) * 8
        y = (index // sections_w) * 8

        # crop the png to get the correct image
        img: QPixmap = image.crop((x, y, x + 8, y + 8)).toqpixmap()
        self.loaded_images.update({self._get_tile_name_by_index(index): img})
        return img

    def _get_tile_name_by_index(self, index: int) -> str:
        names: dict = {v: k for k, v in self.tile_indexes.items()}

        if index in names:
            return names[index]
        raise ValueError(f"Index {index} not found in tile_indexes.")
