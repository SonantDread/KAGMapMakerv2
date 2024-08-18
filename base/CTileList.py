import io

from PIL import Image
from PyQt6.QtGui import QPixmap
from base.CTile import CTile
from utils.vec import vec
from base.KagColor import KagColor
from base.ImageHandler import ImageHandler

tile_size = vec(8, 8)

class CTileList:
    def __init__(self) -> None:
        self.tile_colors = KagColor()
        self.Images = ImageHandler()

        self.vanilla_tiles_collection = [
            CTile(self.Images.getImage(0  ), "tile_empty",            vec(0,0), -5000),
            CTile(self.Images.getImage(16 ), "tile_ground",           vec(0,0), -1   ),
            CTile(self.Images.getImage(32 ), "tile_ground_back",      vec(0,0), -1   ),
            CTile(self.Images.getImage(25 ), "tile_grass",            vec(0,0), 500  ),
            CTile(self.Images.getImage(48 ), "tile_castle",           vec(0,0), -1   ),
            CTile(self.Images.getImage(224), "tile_castle_moss",      vec(0,0), -1   ),
            CTile(self.Images.getImage(64 ), "tile_castle_back",      vec(0,0), -1   ),
            CTile(self.Images.getImage(227), "tile_castle_back_moss", vec(0,0), -1   ),
            CTile(self.Images.getImage(80 ), "tile_gold",             vec(0,0), -1   ),
            CTile(self.Images.getImage(96 ), "tile_stone",            vec(0,0), -1   ),
            CTile(self.Images.getImage(208), "tile_thickstone",       vec(0,0), -1   ),
            CTile(self.Images.getImage(106), "tile_bedrock",          vec(0,0), -1   ),
            CTile(self.Images.getImage(196), "tile_wood",             vec(0,0), -1   ),
            CTile(self.Images.getImage(173), "tile_wood_back",        vec(0,0), -1   )
        ]

        self.vanilla_tiles_indexes = {
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
    
    def getTileByName(self, name: str) -> CTile:
        for tile in self.vanilla_tiles_collection:
            if tile.name is name:
                return tile
        
        return None

    def getTileByColor(self, color: tuple) -> CTile:
        colors = self.tile_colors.getTileColors()
        index = colors.find(color)
        if index != -1:
            return self.tile_colors.vanilla_colors[index]
        else:
            return self.getTile("tile_empty")

    def does_tile_exist(self, name: str) -> bool:
        for tile in self.vanilla_tiles_collection:
            if tile.name is name:
                return True

        return False

    def isTileBackground(self, tile) -> bool:
        return tile.layer <= 500