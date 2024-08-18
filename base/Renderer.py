from base.CTile import CTile
from base.CBlob import CBlob
from typing import Union
from core.scripts.Communicator import Communicator
from utils.vec import vec
from PyQt6.QtGui import QPixmap
from base.ImageHandler import ImageHandler
from base.CTileList import CTileList
import inspect
import os

class Renderer:
    def __init__(self) -> None:
        self.communicator = Communicator()
        self.Images = ImageHandler()
        self.TileList = CTileList()

    def handleRender(self, placing: Union[str, CTile, CBlob], scene_pos: vec, snapped_pos: vec, click_index: int, eraser: bool, z: int = 0) -> None:
        if isinstance(placing, (CTile, CBlob)):
            placing = placing.name
            try: # idk why but this apparently crashes app sometimes
                z = placing.z
            except: pass

        canvas = self.communicator.getCanvas()

        if canvas.tilemap[snapped_pos.x][snapped_pos.y] is not None:
            canvas.removeExistingItemFromScene((snapped_pos.x, snapped_pos.y))
        if eraser: 
            return

        pixmap: QPixmap = self.Images.getImage(placing)
        
        if pixmap is None:
            print(f"Warning: Failed to get image for {placing} at line {inspect.currentframe().f_lineno} of {os.path.basename(__file__)}")
            return

        item: Union[CTile, CBlob] = self.__makeItem(placing, (snapped_pos.x, snapped_pos.y))

        pixmap_item = canvas.addItemToCanvas(pixmap, (scene_pos.x, scene_pos.y), z, placing)

        if pixmap_item is not None:
            canvas.tilemap[snapped_pos.x][snapped_pos.y] = item
            canvas.last_placed_pos = [snapped_pos.x, snapped_pos.y]

    def __makeItem(self, name: str, pos: tuple) -> Union[CTile, CBlob]:
        img: QPixmap = self.Images.getImage(name)

        x, y = pos
        pos = vec(x, y)

        if self.TileList.getTileByName(name) is None:
            return CBlob(img, name, pos, 0)
        return CTile(img, name, pos, 0, True)