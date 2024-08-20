"""
Stores a list of all the available blobs.
"""

import os

from base.cblob import CBlob
from base.image_handler import ImageHandler
from utils.vec import vec


class CBlobList:
    """
    Stores a list of all the available blobs.
    """
    def __init__(self):
        self.exec_path = os.path.dirname(os.path.realpath(__file__)) # where this file is
        self.sprite_path = os.path.join(self.exec_path, "Sprites")
        self.images = ImageHandler()
        self.vanilla_maploader_blobs = [self._to_blob_class(name) for name in self.get_blob_list()]
        # this line of code is required otherwise they are just random
        # still don't know why they are random but this is a temp fix
        self.vanilla_maploader_blobs.sort(key = lambda item: item.name)

        # -----
        # special tab
        # necromancer_teleport
        # redbarrier
        # mook_knight
        # mook_archer
        # mook_spawner
        # mook_spawner_10
        # -----

        # TODO: make dirt backwall + water = automatically going to the water_backdirt
        # "water_air",
        # "water_backdirt",

    def get_blob_list(self) -> list:
        """
        Reads a list of blob names from a file and returns a list of unique blob names.

        Returns:
            list: A list of unique blob names. If the file is empty, an empty list is returned.

        """
        names = []

        with open(os.path.join(self.exec_path, "Bloblist.txt"), encoding = 'utf-8') as f:
            for item in f.readlines():
                names.append(item.strip())

        if len(names) == 0:
            return

        return list(set(names))

    def _to_blob_class(self, name: str) -> CBlob:
        return CBlob(self.images.get_image(name), name, vec(0, 0), 0, 0, self._get_fakez(name))

    # until we have a good way to get the z indexes of blobs we can use this
    # TODO: maybe in bloblist.txt, allow for adding a ', #' for a Z index
    def _get_fakez(self, name: str) -> int:
        if "shop" in name: # see CTileList.py line 33
            return -500

        if name == "archer" or name == "knight": # todo: be able to place these
            return -100

        if name == "spikes":
            return 1500

        sprite = self.images.get_image(name)
        size = sprite.width() + sprite.height()

        # clamp to range of -499 -> 499
        return max(min(size, 499), -499)

    def does_blob_exist(self, name: str) -> bool:
        """
        Check if a blob with the given name exists in the list of vanilla maploader blobs.

        Args:
            name (str): The name of the blob to check for.

        Returns:
            bool: True if a blob with the given name exists, False otherwise.
        """
        for blob in self.vanilla_maploader_blobs:
            if blob.name == name:
                return True

        return False
