import os
from PIL import Image

class KagImage:
    def __init__(self):
        self.tile_indexes = {
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

    def getTilePNGByIndex(self, index: int):
        # Open world.png
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sprites", "Default", "world.png")
        image = Image.open(image_path)

        # Get sizes for image parsing
        width, height = image.size
        sections_w, sections_h = width // 8, height // 8

        # Calculate the coordinates for the specified index
        x = (index % sections_w) * 8
        y = (index // sections_w) * 8

        # Crop the world.png to get the correct image
        return image.crop((x, y, x + 8, y + 8))
    
    def getTilePNGByName(self, name):
        if(type(name) != str): # assume tile class
            name = name.tile_name

        return self.getTilePNGByIndex(self.tile_indexes[name])