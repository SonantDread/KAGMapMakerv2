"""
Holds basic information for tiles.
"""
from PyQt6.QtGui import QPixmap
from utils.vec import Vec2f

class CTile:
    """
    A class representing a tile in a game.

    Attributes:
        img (QPixmap): The image of the tile.
        name (str): The name of the tile.
        pos (tuple): The position of the tile.
        layer (int): The layer of the tile.
        z (int): The depth of the tile in the background rendering.
    """
    def __init__(self, img: QPixmap, name: str, pos: Vec2f, layer: int, z: int = 0) -> None:
        self.img: QPixmap = img
        self.name: str = name
        self.pos: tuple = pos
        self.layer: int = layer
        self.z: int = z # how far to render in the background
