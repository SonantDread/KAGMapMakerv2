class KagColor:
    def __init__(self):
        self.vanilla_colors = {
            "tile_ground": (255, 132, 71, 21),
            "tile_ground_back": (255, 59, 20, 6),
            "tile_stone": (255, 139, 104, 73),
            "tile_thickstone": (255, 66, 72, 75),
            "tile_bedrock": (255, 45, 52, 45),
            "tile_gold": (255, 254, 165, 61),
            "tile_castle": (255, 100, 113, 96),
            "tile_castle_back": (255, 49, 52, 18),
            "tile_castle_moss": (255, 100, 143, 96),
            "tile_castle_back_moss": (255, 49, 82, 18),
            "tile_grass": (255, 100, 155, 13),
            "tile_wood": (255, 196, 135, 21),
            "tile_wood_back": (255, 85,  42, 17),
            "water_air": (255, 46, 129, 166),
            "water_backdirt": (255, 51, 85, 102),
        }

    # return ARGB color
    def getColor(self, tile_name: str) -> tuple:
        return self.vanilla_colors[tile_name]
    
    # return RGB color
    def getColorRGB(self, tile_name: str) -> tuple:
        return self.tiles[tile_name][1:]
    
    def getTileNames(self) -> list:
        return list(self.tiles.keys())
    
    def getTileColors(self) -> list:
        return list(self.tiles.values())