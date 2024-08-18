# core implementation of the lazy image loading, shared between every instance
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QImage
from base.CTile import CTile
from base.CBlob import CBlob
from typing import Union
import os
import inspect
from PIL import Image

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class ImageHandler(metaclass = SingletonMeta):
    def __init__(self) -> None:
        self.loaded_images = {}
        self.tile_indexes = { # used to get correct sprite in world.png
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
        }
        exec_path = os.path.dirname(os.path.realpath(__file__))
        self.basepath = os.path.join(exec_path, "Sprites", "MapMaker")

    def getImage(self, name: Union[str, int]) -> QPixmap:
        if isinstance(name, int): # handle input of index for a block
            name = self._getTileNameByIndex(name)

        if self.loaded_images.get(name) is not None:
            return self.loaded_images.get(name)

        # image doesnt exist
        img = self._getItemPNGByName(name)

        if img is not None:
            return img

        print(f"Image not found: {name}. Unable to load in line {inspect.currentframe().f_lineno} of {os.path.basename(__file__)}")
        return None

    def _getItemPNGByName(self, name: str) -> QPixmap:
        if name in self.tile_indexes:
            return self._getTilePNGByIndex(self.tile_indexes[name])

        return self._loadImage(name)

    def _loadImage(self, name: str) -> QPixmap:
        try:
            path = os.path.join(self.basepath, name + ".png")

            img = Image.open(path)
            img.convert("RGBA")
            img.load()

            self.loaded_images.update({name: img.toqpixmap()})
            return img.toqpixmap()

        except:
            print(f"Image not found: {name}")
            return None # img not found

    def _getTilePNGByIndex(self, index: int) -> QPixmap:
        # open world.png
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sprites", "Default", "world.png")
        image = Image.open(image_path)
        image = image.convert("RGBA") # prevent errors with alpha translation

        width, height = image.size
        sections_w, sections_h = width // 8, height // 8

        # calculate coordinates for the specified index
        x = (index % sections_w) * 8
        y = (index // sections_w) * 8

        # crop the world.png to get the correct image
        img: QPixmap = image.crop((x, y, x + 8, y + 8)).toqpixmap()
        self.loaded_images.update({self._getTileNameByIndex(index): img})
        return img
    
    def _getTileNameByIndex(self, index: int) -> str:
        names: dict = {v: k for k, v in self.tile_indexes.items()}
        
        if index in names:
            return names[index]
        raise ValueError(f"Index {index} not found in tile_indexes.")