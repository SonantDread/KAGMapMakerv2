from PyQt6.QtGui import QPixmap
from utils.vec import vec

class CTile:
    def __init__(self, img: QPixmap, name: str, pos: vec, layer: int, z: int = 0, color: str = "0xFFA5BDC8") -> None:
        self.img: QPixmap = img
        self.name: str = name
        self.pos: tuple = pos
        self.layer: int = layer # current layer block is on, useful for trying to draw over sprites
        self.z: int = z # how far to render in the background
        self.color: tuple = color # ARGB color of the tile