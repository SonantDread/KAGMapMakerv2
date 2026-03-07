# KAGMapMakerV2 - An unofficial map maker for King Arthur's Gold.
# Copyright (C) 2026 SonantDread
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
Handles the rendering of objects for the canvas class.
This class is responsible for all direct manipulation of the QGraphicsScene
and synchronizing the visual state with the tilemap.
"""

import inspect
import os

from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtWidgets import QGraphicsPixmapItem

from base.citem import CItem
from base.citemlist import CItemList
from base.image_handler import ImageHandler
from core.communicator import Communicator
from core.renderer_render_overlays import RenderOverlays
from utils.vec2f import Vec2f

class Renderer:
    """
    Renders items on the screen for the canvas.
    It takes the canvas instance as a dependency to directly interact with it.
    """
    def __init__(self, canvas) -> None:
        self.canvas = canvas
        self.communicator = Communicator()
        self.images = ImageHandler()
        self.item_list = CItemList()
        self.cursor_graphics_item = None
        self.render_overlays = RenderOverlays(self, self.communicator)

    def render_item(self, placing: CItem, scene_pos: Vec2f, grid_pos: Vec2f, eraser: bool, rot: int) -> None:
        """
        Handles the complete rendering logic for an item. It erases or places
        an item, and updates the visual scene.
        """
        if eraser:
            if grid_pos in self.canvas.graphics_items:
                item_to_remove = self.canvas.graphics_items.pop(grid_pos)
                self.canvas.canvas.removeItem(item_to_remove)
                self.render_overlays.on_erase_block(grid_pos)

            return

        if grid_pos in self.canvas.graphics_items:
            old_item = self.canvas.graphics_items.pop(grid_pos)
            self.canvas.canvas.removeItem(old_item)

        current_team = self.communicator.team
        if placing.sprite.properties.can_swap_teams and placing.sprite.team != current_team:
            placing.swap_team(current_team)

        pixmap: QPixmap = placing.sprite.image
        if pixmap is None:
            line = inspect.currentframe().f_lineno
            fn = os.path.basename(__file__)
            print(f"Warning: Failed to get image for {placing.name_data.name} at line {line} of {fn}")
            return

        if placing.sprite.properties.is_rotatable:
            pixmap = self._rotate_blob(pixmap, rot)

        pixmap_item = QGraphicsPixmapItem(pixmap)
        scale = self.canvas.default_zoom_scale
        pixmap_item.setScale(scale)

        # adjust position for rotation to keep it centered in the grid cell
        w, h = pixmap.width() * scale, pixmap.height() * scale
        adjusted_x, adjusted_y = scene_pos.x, scene_pos.y
        if rot in (90, 270):
            adjusted_x += (h - w) / 2
            adjusted_y += (w - h) / 2

        offset_x, offset_y = placing.sprite.offset
        pixmap_item.setPos(float(adjusted_x + offset_x), float(adjusted_y + offset_y))
        pixmap_item.setZValue(placing.sprite.z)

        self.canvas.canvas.addItem(pixmap_item)
        self.canvas.graphics_items[grid_pos] = pixmap_item

        self.render_overlays.on_place_block(placing, grid_pos)

    def render_cursor(self, pos: Vec2f) -> None:
        """
        Renders the cursor on the canvas at the given scene position.
        """
        if self.cursor_graphics_item is None:
            self.setup_cursor()

        try:
            self.cursor_graphics_item[0].setPos(pos.x, pos.y)
            self.cursor_graphics_item[0].show()

            if self.communicator.settings.get("mirrored over x", False):
                grid_x = pos.x / self.canvas.grid_spacing
                mirrored_grid_x = self.canvas.map_size.x - 1 - grid_x
                mirrored_scene_x = mirrored_grid_x * self.canvas.grid_spacing

                self.cursor_graphics_item[1].setPos(mirrored_scene_x, pos.y)
                self.cursor_graphics_item[1].show()

            else:
                self.cursor_graphics_item[1].hide()

        except (RuntimeError, IndexError):
            self.cursor_graphics_item = None
            self.setup_cursor()

    def setup_cursor(self) -> None:
        """
        Creates the QGraphicsPixmapItems for the main and mirrored cursors.
        """
        cursor_image = self.images.get_image("cursor")
        if cursor_image is None:
            print("Warning: 'cursor.png' not found. Cursor will not be rendered.")
            return

        items = []
        for _ in range(2): # 0 for main, 1 for mirrored
            cursor = QGraphicsPixmapItem(cursor_image)
            cursor.setZValue(1_000_000)
            scale = self.canvas.default_zoom_scale * (8 / 10)
            cursor.setScale(scale)
            self.canvas.canvas.addItem(cursor)
            items.append(cursor)

        items[1].hide() # hide mirrored cursor by default
        self.cursor_graphics_item = items

    def _rotate_blob(self, pixmap: QPixmap, degrees: int) -> QPixmap:
        """
        Rotates a QPixmap by a given number of degrees.
        """
        if degrees == 0:
            return pixmap

        return pixmap.transformed(QTransform().rotate(degrees))
