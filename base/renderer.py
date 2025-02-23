"""
Handles the rendering of objects for the canvas class.
"""

import inspect
import os

from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsPixmapItem

from base.citem import CItem
from base.citemlist import CItemList
from base.image_handler import ImageHandler

from core.communicator import Communicator
from utils.vec2f import Vec2f

class Renderer:
    """
    Renders items on the screen for the canvas.
    """
    def __init__(self) -> None:
        self.communicator = Communicator()
        self.images = ImageHandler()
        self.item_list = CItemList()
        self.cursor_graphics_item = None

    def render_item(self, placing: CItem, pos: Vec2f, tm_pos: Vec2f, eraser: bool, rot: int) -> None:
        """
        Handles the rendering of an object on the canvas.

        Args:
            placing (CItem): The object to render.
            pos (Vec2f): The position of the object on the canvas.
            tm_pos (Vec2f): The snapped position of the object on the canvas.
            eraser (bool): Whether or not to erase the object.
        """
        z = placing.sprite.z

        canvas = self.communicator.get_canvas()

        # remove rendered item if it exists
        if canvas.tilemap[tm_pos.x][tm_pos.y] is not None:
            self.remove_existing_item_from_scene((tm_pos.x, tm_pos.y))

        if eraser:
            return

        pixmap: QPixmap = placing.sprite.image
        if pixmap is None:
            line = inspect.currentframe().f_lineno
            fn = os.path.basename(__file__)
            print(f"Warning: Failed to get image for {placing} at line {line} of {fn}")
            return

        if placing.sprite.properties.is_rotatable:
            pixmap = self._rotate_blob(pixmap, rot)

        pixmap_item = self.add_to_canvas(pixmap, (pos.x, pos.y), z, placing.name_data.name, placing.sprite.offset)

        if pixmap_item is not None:
            canvas.tilemap[tm_pos.x][tm_pos.y] = placing

    def remove_existing_item_from_scene(self, pos: tuple) -> None:
        """
        Removes an existing item from the scene at the specified position (in tilemap coordinates).

        Args:
            pos (tuple): The position of the item to be removed.

        Returns:
            None
        """
        canvas = self.communicator.get_canvas()
        x, y = pos
        if canvas.tilemap[x][y] is not None:
            if (x, y) in canvas.graphics_items:
                canvas.canvas.removeItem(canvas.graphics_items[(x, y)])
                del canvas.graphics_items[(x, y)]
            canvas.tilemap[x][y] = None

    def add_to_canvas(self, img: QPixmap, pos: tuple, z: int, name: str, offset: Vec2f) -> QGraphicsPixmapItem:
        """
        Adds an item to the canvas at the specified position.

        Args:
            img (QPixmap): The pixmap to be added to the canvas.
            pos (tuple): The position of the item in the canvas.
            z (int): The z-value of the item.
            name (str): The name of the item.
            offset (Vec2f): The offset to apply to the item's position.

        Returns:
            QGraphicsPixmapItem: The added pixmap item, or None if the pixmap is None.
        """
        canvas = self.communicator.get_canvas()
        x, y = canvas.snap_to_grid(pos)

        # remove existing item if present
        if canvas.tilemap[x][y] is not None:
            self.remove_existing_item_from_scene((x, y))

        if img is None:
            print(f"Warning: img is None for item {name} at position {pos}")
            return None

        # create new item
        pixmap_item = QGraphicsPixmapItem(img)
        pixmap_item.setScale(canvas.zoom_factor * canvas.default_zoom_scale)

        pixmap_item.setPos(int(pos[0] - offset.x), int(pos[1] - offset.y))
        pixmap_item.setZValue(z)

        canvas.canvas.addItem(pixmap_item)
        canvas.graphics_items[(x, y)] = pixmap_item

        return pixmap_item

    def render_cursor(self, pos: Vec2f) -> None:
        """
        Renders the cursor on the canvas at the given position.

        Args:
            pos (Vec2f): The position where the cursor should be rendered.
        """
        canvas = self.communicator.get_canvas()
        if self.cursor_graphics_item is None:
            self.setup_cursor()

        try:
            self.cursor_graphics_item[0].setPos(pos.x, pos.y)

            if self.communicator.settings.get("mirrored over x", False):
                # calculate mirrored position
                grid_x = pos.x / canvas.grid_spacing
                mirrored_grid_x = canvas.size.x - 1 - grid_x
                mirrored_scene_x = mirrored_grid_x * canvas.grid_spacing

                # show mirrored cursor
                self.cursor_graphics_item[1].setPos(mirrored_scene_x, pos.y)
                self.cursor_graphics_item[1].setOpacity(1)
            else:
                self.cursor_graphics_item[1].setOpacity(0)

        except RuntimeError:
            self.setup_cursor()
            self.render_cursor(pos)

    def setup_cursor(self) -> None:
        canvas = self.communicator.get_canvas()
        cursor_image = self.images.get_image("cursor.png")
        if cursor_image is None:
            raise ValueError("Cursor image not found. Ensure 'cursor.png' asset is available.")

        # create main cursor
        main_cursor = QGraphicsPixmapItem(cursor_image)
        main_cursor.setZValue(1000000)
        base_scale = canvas.zoom_factor * canvas.default_zoom_scale
        main_cursor.setScale(base_scale * (8 / 10))

        # create mirrored cursor
        mirror_cursor = QGraphicsPixmapItem(cursor_image)
        mirror_cursor.setZValue(1000000)
        mirror_cursor.setScale(base_scale * (8 / 10))
        mirror_cursor.setOpacity(0)

        canvas.canvas.addItem(main_cursor)
        canvas.canvas.addItem(mirror_cursor)

        self.cursor_graphics_item = [main_cursor, mirror_cursor]

    def _rotate_blob(self, pixmap: QPixmap, degrees: int) -> None:
        rotated_pixmap = QTransform().rotate(degrees)
        pixmap = pixmap.transformed(rotated_pixmap)
        return pixmap
