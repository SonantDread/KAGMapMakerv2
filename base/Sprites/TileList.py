from PyQt6.QtGui import QPixmap
from base.Tile import Tile
from utils.vec import vec
from base.KagColor import KagColor

class TileList:
    # def __init__(self, img: QPixmap, tile_name: str, tile_pos: vec, layer: int, solid: bool)
    def __init__(self) -> None:
        self.tile_colors = KagColor()

        n = False # 2head python
        y = True
        self.vanilla_tiles_collection = [
            # Tile(QPixmap(None), "", vec(0,0), -1, n),
            Tile(QPixmap(None), "tile_empty", vec(0,0), -5000, n),
            Tile(QPixmap(None), "tile_ground", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_ground_back", vec(0,0), -1, n),
            Tile(QPixmap(None), "tile_grass", vec(0,0), 500, n),
            Tile(QPixmap(None), "tile_castle", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_castle_moss", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_castle_back", vec(0,0), -1, n),
            Tile(QPixmap(None), "tile_castle_back_moss", vec(0,0), -1, n),
            Tile(QPixmap(None), "tile_gold", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_stone", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_thickstone", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_bedrock", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_wood", vec(0,0), -1, y),
            Tile(QPixmap(None), "tile_wood_back", vec(0,0), -1, n)
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