from PyQt6.QtGui import QPixmap

class Tile:
    def __init__(self, img: QPixmap, tile_name: str, tile_pos: tuple, rotation: int, team: int, z: int, layer: int) -> None:
        self.img = img
        self.tile_name = tile_name
        self.tile_pos = tile_pos
        self.rotation = rotation
        self.team = team
        self.z = z
        self.layer = layer