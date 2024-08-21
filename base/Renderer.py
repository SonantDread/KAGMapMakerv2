"""
Handles the rendering of objects for the canvas class.
"""

import inspect
import os
from typing import Union

from PyQt6.QtGui import QPixmap

from base.cblob import CBlob
from base.ctile import CTile
from base.ctile_list import CTileList
from base.image_handler import ImageHandler
from core.scripts.communicator import Communicator
from utils.vec import Vec2f

class Renderer:
    """
    Renders items on the screen for the canvas.
    """
    def __init__(self) -> None:
        self.communicator = Communicator()
        self.images = ImageHandler()
        self.tile_list = CTileList()

    def render(self, placing: str, pos: Vec2f, tm_pos: Vec2f, eraser: bool) -> None:
        """
        Handles the rendering of an object on the canvas.

        Args:
            placing (Union[str, CTile, CBlob]): The object to render.
            pos (Vec2f): The position of the object on the canvas.
            tm_pos (Vec2f): The snapped position of the object on the canvas.
            eraser (bool): Whether or not to erase the object.
        """
        z = 0
        if isinstance(placing, (CTile, CBlob)):
            if z == 0: # default z
                z = placing.z

            placing = placing.name

        canvas = self.communicator.get_canvas()

        # remove rendered item if it exists
        if canvas.tilemap[tm_pos.x][tm_pos.y] is not None:
            canvas.remove_existing_item_from_scene((tm_pos.x, tm_pos.y))

        if eraser:
            return

        pixmap: QPixmap = self.images.get_image(placing)

        if pixmap is None:
            line = inspect.currentframe().f_lineno
            fn = os.path.basename(__file__)
            print(f"Warning: Failed to get image for {placing} at line {line} of {fn}")
            return

        item: Union[CTile, CBlob] = self.__make_item(placing, (tm_pos.x, tm_pos.y))

        pixmap_item = canvas.add_to_canvas(pixmap, (pos.x, pos.y), z, placing)

        if pixmap_item is not None:
            canvas.tilemap[tm_pos.x][tm_pos.y] = item

    def __make_item(self, name: str, pos: tuple) -> Union[CTile, CBlob]:
        """
        Creates a new item (CTile or CBlob) based on the provided name and position.

        Args:
            name (str): The name of the item to create.
            pos (tuple): The position of the item to create.

        Returns:
            Union[CTile, CBlob]: The created item, either a CTile or a CBlob.
        """
        img: QPixmap = self.images.get_image(name)

        x, y = pos
        pos = Vec2f(x, y)

        if self.tile_list.get_tile_by_name(name) is None:
            return CBlob(img, name, pos, 0)
        return CTile(img, name, pos, 0, True)
