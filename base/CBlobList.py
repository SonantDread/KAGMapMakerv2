from PIL import Image
from utils.vec import vec
from base.CBlob import CBlob
from PyQt6.QtGui import QPixmap
from base.ImageHandler import ImageHandler
import os

class CBlobList:
    def __init__(self):
        self.exec_path = os.path.dirname(os.path.realpath(__file__)) # where this file is
        self.sprite_path = os.path.join(self.exec_path, "Sprites")
        self.Images = ImageHandler()
        self.vanilla_maploader_blobs = [self._toBlobClass(name) for name in self.getBlobList()]
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

    def getBlobList(self) -> list:
        names = []

        with open(os.path.join(self.exec_path, "Bloblist.txt")) as f:
            for item in f.readlines():
                names.append(item.strip())

        if len(names) == 0:
            return

        return list(set(names))

    def _toBlobClass(self, name: str) -> CBlob:
        return CBlob(self.Images.getImage(name), name, vec(0, 0), 0, 0, self._handle_get_fakez(name))
    
    # until we have a good way to get the z indexes of blobs we can use this
    # TODO: maybe in bloblist.txt, allow for adding a ', #' for a Z index
    def _handle_get_fakez(self, name: str) -> int:
        if "shop" in name: # see CTileList.py line 33
            return -500
        
        if name == "archer" or name == "knight": # todo: be able to place these
            return -100
        
        if name == "spikes":
            return 1500
        
        sprite = self.Images.getImage(name)
        size = sprite.width() + sprite.height()
        
        # clamp to range of -499 -> 499
        return max(min(size, 499), -499)

    def doesBlobExist(self, name: str) -> bool:
        for blob in self.vanilla_maploader_blobs:
            if blob.name == name:
                return True

        return False