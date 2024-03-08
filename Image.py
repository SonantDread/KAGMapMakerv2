import os
import re
from PIL import Image as PILImage
class Image:
    indexes = {
        "unused": int(0),
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

    def __init__(self, filepath: str = r"C:\Program Files (x86)\Steam\steamapps\common\King Arthur's Gold\Base\Scripts\MapLoaders\LoaderColors.as") -> None:
        self.filepath = filepath
        self.names = None

        self.getNames()

    @staticmethod
    def get_block_names():
        return list(Image.indexes.keys())

    def hexToARGB(self, hex_code):
        hex_code = hex_code[2:]
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4, 6))

    def RGBtoHex(self, RGB) -> str:
        return "0x{:02X}{:02X}{:02X}".format(*RGB)

    def getNames(self):
        with open(self.filepath, "r") as f:
            data = f.read() # todo: error handling

            matches = re.findall(r"\b(\w+)\s*=\s*(0x[0-9A-Fa-f]+)\b", data)

            dictionary = {}
            reversed_dictionary = {}

            keys = []

            for match in matches:
                dictionary[match[0]] = self.hexToARGB(match[1])
                reversed_dictionary[self.hexToARGB(match[1])] = match[0]
                keys.append(match[0])

            self.names = dictionary
            self.reversed_names = reversed_dictionary
            self.keys = keys

    # TODO: automatically get a block's index by name
    def getTileIndexByName(self, tile: str) -> int:

        # TODO: auto get this from customblock.as, and append to this too?

        return Image.indexes[tile]

    # returns an ARGB color from the given name
    def getKAGMapPixelColorByName(self, name: str):
        return self.names[name]

    def getAllKAGItems(self):
        return self.keys

    # returns a name from an ARGB pixel color
    def getKAGMapNameByPixelColor(self, color: str):
        return self.reversed_names[color]

    def getBlockPNGByIndex(self, index: int):
        # Open world.png
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sprites", "world.png")
        image = PILImage.open(image_path)

        # Get sizes for image parsing
        width, height = image.size
        sections_w, sections_h = width // 8, height // 8

        # Calculate the coordinates for the specified index
        x = (index % sections_w) * 8
        y = (index // sections_w) * 8

        # Crop the world.png to get the correct image
        return image.crop((x, y, x + 8, y + 8))

if __name__ == "__main__":
    Image()