from PyQt6.QtGui import QPixmap
from utils.vec import vec

class Tile:
    def __init__(self, img: QPixmap, tile_name: str, tile_pos: vec, layer: float, solid: bool) -> None:
        self.img = img
        self.tile_name = tile_name
        self.tile_pos = tile_pos
        self.solid = solid
        
        if layer != 1: self.layer = layer
        elif self.solid: self.layer = 500
        else: self.layer = -500