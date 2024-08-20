"""
Stores a list of all the available tiles.
"""
from base.ctile import CTile
from base.image_handler import ImageHandler
from base.kag_color import KagColor
from utils.vec import vec

tile_size = vec(8, 8)

class CTileList:
    """
    Stores a list of all the available tiles.
    """
    def __init__(self) -> None:
        self.tile_colors = KagColor()
        self.images = ImageHandler()

        self.vanilla_tiles_collection = [
            CTile(self.images.get_image(0  ), "tile_empty",            vec(0,0), 0, -5000),
            CTile(self.images.get_image(16 ), "tile_ground",           vec(0,0), 0, 500  ),
            CTile(self.images.get_image(32 ), "tile_ground_back",      vec(0,0), 0, -600 ),
            CTile(self.images.get_image(25 ), "tile_grass",            vec(0,0), 0, 500  ),
            CTile(self.images.get_image(48 ), "tile_castle",           vec(0,0), 0, 500  ),
            CTile(self.images.get_image(224), "tile_castle_moss",      vec(0,0), 0, 500  ),
            CTile(self.images.get_image(64 ), "tile_castle_back",      vec(0,0), 0, -600 ),
            CTile(self.images.get_image(227), "tile_castle_back_moss", vec(0,0), 0, -600 ),
            CTile(self.images.get_image(80 ), "tile_gold",             vec(0,0), 0, 500  ),
            CTile(self.images.get_image(96 ), "tile_stone",            vec(0,0), 0, 500  ),
            CTile(self.images.get_image(208), "tile_thickstone",       vec(0,0), 0, 500  ),
            CTile(self.images.get_image(106), "tile_bedrock",          vec(0,0), 0, 500  ),
            CTile(self.images.get_image(196), "tile_wood",             vec(0,0), 0, 500  ),
            CTile(self.images.get_image(173), "tile_wood_back",        vec(0,0), 0, -600 )
        ]
        ## for KAG but will also use here to try to keep it similar,
        # can be changed later if its a problem
        # -600 = behind background
        # -500 = in front of background, behind shops
        # -100 = in front of shops, behind players
        #  100 = in front of players, behind solid tiles
        #  500 = in front of solid tiles (and basically everything else except trees and spikes)
        # 1500 = in front of spikes

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

    def get_tile_by_name(self, name: str) -> CTile:
        """
        Retrieves a CTile object from the vanilla_tiles_collection by its name.

        Args:
            name (str): The name of the tile to retrieve.

        Returns:
            CTile: The CTile object with the matching name, or None if no match is found.
        """
        for tile in self.vanilla_tiles_collection:
            if tile.name is name:
                return tile

        return None

    def does_tile_exist(self, name: str) -> bool:
        """
        Checks if a tile with the given name exists in the vanilla tiles collection.

        Args:
            name (str): The name of the tile to check for.

        Returns:
            bool: True if the tile exists, False otherwise.
        """
        for tile in self.vanilla_tiles_collection:
            if tile.name is name:
                return True

        return False
