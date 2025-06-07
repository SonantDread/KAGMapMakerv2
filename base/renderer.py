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

        canvas = self.communicator.get_canvas()

        # merge two items if applicable
        did_merge, old_name = False, placing.name_data.name
        tile = canvas.tilemap.get(tm_pos)
        if tile is not None and (placing.is_mergeable() or tile.is_mergeable()):
            name = placing.merge_with(tile.name_data.name)
            new_item: CItem = self.item_list.get_item_by_name(name)

            if new_item is None:
                name = tile.merge_with(placing.name_data.name)
                new_item: CItem = self.item_list.get_item_by_name(name)

            if new_item is not None:
                placing: CItem = new_item.copy()
                did_merge = True

        # items merging into itself dont place
        if did_merge and old_name == placing.name_data.name:
            return

        # remove rendered item if it exists
        if canvas.tilemap.get(tm_pos) is not None:
            self.remove_existing_item_from_scene(tm_pos)

        if eraser:
            return

        current_team = self.communicator.team
        can_change_teams = placing.sprite.properties.can_swap_teams
        if can_change_teams and placing.sprite.team != current_team:
            placing.swap_team(current_team)

        pixmap: QPixmap = placing.sprite.image
        if pixmap is None:
            line = inspect.currentframe().f_lineno
            fn = os.path.basename(__file__)
            print(f"Warning: Failed to get image for {placing} at line {line} of {fn}")
            return

        if placing.sprite.properties.is_rotatable:
            pixmap = self._rotate_blob(pixmap, rot)

        pixmap_item = self.add_to_canvas(placing, pixmap, pos, rot)

        if pixmap_item is not None:
            canvas.tilemap[tm_pos] = placing

    def remove_existing_item_from_scene(self, pos: Vec2f) -> None:
        """
        Removes an existing item from the scene at the specified position (in tilemap coordinates).

        Args:
            pos (tuple): The position of the item to be removed.

        Returns:
            None
        """
        canvas = self.communicator.get_canvas()

        if pos in canvas.tilemap:
            if pos in canvas.graphics_items:
                canvas.canvas.removeItem(canvas.graphics_items[pos])
                del canvas.graphics_items[pos]

            del canvas.tilemap[pos]

    def add_to_canvas(self, placing: CItem, img: QPixmap, pos: Vec2f, rot: int) -> QGraphicsPixmapItem:
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
        tm_pos = Vec2f(x, y)

        # remove existing item if present
        if canvas.tilemap.get(pos) is not None:
            self.remove_existing_item_from_scene(pos)

        if img is None:
            print(f"Warning: img is None for item {placing.name_data.name} at position {pos}")
            return None

        # create new item
        pixmap_item = QGraphicsPixmapItem(img)
        scale = canvas.default_zoom_scale
        pixmap_item.setScale(scale)

        adjusted_x, adjusted_y = pos

        w, h = img.width() * scale, img.height() * scale
        if rot in (90, 270):
            adjusted_x += (h - w) / 2
            adjusted_y += (w - h) / 2

        offset_x, offset_y = placing.sprite.offset
        pixmap_item.setPos(float(adjusted_x + offset_x), float(adjusted_y + offset_y))

        pixmap_item.setZValue(placing.sprite.z)

        canvas.canvas.addItem(pixmap_item)
        canvas.graphics_items[tm_pos] = pixmap_item

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
        cursor_image = self.images.get_image("cursor")
        if cursor_image is None:
            raise ValueError("Cursor image not found. Ensure 'cursor.png' asset is available.")

        # create main cursor
        main_cursor = QGraphicsPixmapItem(cursor_image)
        main_cursor.setZValue(1000000)
        base_scale = canvas.default_zoom_scale
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
        return pixmap.transformed(QTransform().rotate(degrees))
