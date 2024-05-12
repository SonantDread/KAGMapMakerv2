import io

from PIL import Image
from PyQt6.QtGui import QPixmap
from base.Tile import Tile
from utils.vec import vec
from base.KagColor import KagColor

tile_size = vec(8,8)

class TileList:
    # def __init__(self, img: QPixmap, tile_name: str, tile_pos: vec, layer: int, solid: bool)
    def __init__(self) -> None:
        self.tile_colors = KagColor()

        n = False # 2head python
        y = True
        self.vanilla_tiles_collection = [
            # Tile(QPixmap(None), "", vec(0,0), -1, n),
            Tile(self.craftIconFromPNG(tile_size, 15),     "tile_empty",               vec(0,0), -5000, n),
            Tile(self.craftIconFromPNG(tile_size, 16),     "tile_ground",              vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 32),     "tile_ground_back",         vec(0,0), -1, n),
            Tile(self.craftIconFromPNG(tile_size, 25),     "tile_grass",               vec(0,0), 500, n),
            Tile(self.craftIconFromPNG(tile_size, 48),     "tile_castle",              vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 224),    "tile_castle_moss",         vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 64),     "tile_castle_back",         vec(0,0), -1, n),
            Tile(self.craftIconFromPNG(tile_size, 227),    "tile_castle_back_moss",    vec(0,0), -1, n),
            Tile(self.craftIconFromPNG(tile_size, 80),     "tile_gold",                vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 96),     "tile_stone",               vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 208),    "tile_thickstone",          vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 106),    "tile_bedrock",             vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 196),    "tile_wood",                vec(0,0), -1, y),
            Tile(self.craftIconFromPNG(tile_size, 205),    "tile_wood_back",           vec(0,0), -1, n)
        ]
        # todo: make tile lists external so people can add their custom tile lists
    
    def getTileByName(self, tile_name: str) -> Tile:
        for tile in self.vanilla_tiles_collection:
            if tile.tile_name is tile_name:
                return tile
    
    def getTileByColor(self, color: tuple) -> Tile:
        colors = self.tile_colors.getTileColors()
        index = colors.find(color)
        if index != -1:
            return self.tile_colors.vanilla_colors[index]
        else:
            return self.getTile("tile_empty")
    
    def isTileSolid(self, tile) -> bool:
        return tile.solid

    def isTileBackground(self, tile) -> bool:
        return tile.layer <= 500

    def isTileGrass(self, tile) -> bool:
        return tile.tile_name is "tile_grass"

    def craftIconFromPNG(self, size: vec, index: int, file="base/Sprites/Default/world.png") -> QPixmap:
        image = Image.open(file)

        img_width, img_height = image.size

        frame_width = size.x
        frame_height = size.y
        x_offset = (index * frame_width) % img_width
        y_offset = ((index * frame_width) // img_width) * frame_height

        frame = image.crop((x_offset, y_offset, x_offset + frame_width, y_offset + frame_height))

        img_byte_array = io.BytesIO()
        frame.save(img_byte_array, format='PNG')

        q_pixmap = QPixmap()
        q_pixmap.loadFromData(img_byte_array.getvalue())

        return q_pixmap