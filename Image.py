import os
import regex as re
from PIL import Image

class Image:
    def __init__(self, filepath: str = r"C:\Program Files (x86)\Steam\steamapps\common\King Arthur's Gold\Base\Scripts\MapLoaders\LoaderColors.as") -> None:
        self.filepath = filepath
        self.ARGB = None

        self.getARGB()
    
    def hexToARGB(self, hex_code):
        hex_code = hex_code[2:]
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4, 6))

    def RGBtoHex(self, RGB) -> str:
        return "0x{:02X}{:02X}{:02X}".format(*RGB)

    def getARGB(self):
        with open(self.filepath, "r") as f:
            data = f.read() # todo: error handling

            matches = re.findall(r"\b(\w+)\s*=\s*(0x[0-9A-Fa-f]+)\b", data)
            dictionary = {}

            for match in matches:
                dictionary[match[0]] = self.hexToARGB(match[1])
            
            self.ARGB = dictionary

    # TODO: automatically get a block's index by name
    def getTileIndexByName(tile: str) -> int:
        indexes = {
            "unused"                 : int(0),
            "tile_ground"            : int(16),
            "tile_grassy_ground"     : int(23),
            "tile_grass"             : int(25),
            "tile_ground_back"       : int(32),
            "tile_castle"            : int(48),
            "tile_castle_back"       : int(64),
            "tile_gold"              : int(80),
            "tile_stone"             : int(96),
            "tile_bedrock"           : int(106),
            "tile_wood_back"         : int(173),
            "tile_wood"              : int(196),
            "tile_thickstone"        : int(208),
            "tile_castle_moss"       : int(224),
            "tile_castle_back_moss"  : int(227),
            "sky"                    : int(400),
        }

        # TODO: auto get this from customblock.as, and append to this too?

        return indexes[tile]

    def getBlockPNGByIndex(index: int):
        # open world.png
        image = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "world.png"))

        # get sizes for image parsing
        width, height = image.size
        sections_w, sections_h = width // 8, height // 8

        # represent the images in order
        sections = []

        # TODO: optimize this to just get the 8x8 square at a png instead of using a for loop
        # parse the image
        for y in range(sections_h):
            for x in range(sections_w):
                # define our boundaries for where to crop, basically just 2 (x, y) points
                left = x * 8
                upper = y * 8
                right = left + 8
                lower = upper + 8

                # crop the world.png to get the correct image
                section = image.crop((left, upper, right, lower))
                sections.append(section)

        # return the image
        return sections[index]

if __name__ == "__main__":
    Image()