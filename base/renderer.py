"""
Handles the rendering of objects for the canvas class.
This class is responsible for all direct manipulation of the QGraphicsScene
and synchronizing the visual state with the data model (tilemap).
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
        """
        Initializes the Renderer.

        Args:
            canvas: The main Canvas instance. This is a required dependency.
        """
        self.canvas = canvas
        self.communicator = Communicator()
        self.images = ImageHandler()
        self.item_list = CItemList()
        self.cursor_graphics_item = None
        self.render_overlays = RenderOverlays(self, self.communicator)

    def render_item(self, placing: CItem, scene_pos: Vec2f, grid_pos: Vec2f, eraser: bool, rot: int) -> None:
        """
        Handles the complete rendering logic for an item. It erases or places
        an item, handles merging, and updates both the visual scene and data model.

        Args:
            placing (CItem): The CItem object to be placed.
            scene_pos (Vec2f): The target position in scene (pixel) coordinates.
            grid_pos (Vec2f): The snapped position in grid coordinates.
            eraser (bool): If True, performs an erase operation.
            rot (int): The rotation to apply to the item.
        """
        # --- HANDLE ERASING ---
        # if the eraser is active, our only job is to remove the visual item,
        # the Canvas is responsible for removing the item from the data model (`tilemap`)
        if eraser:
            if grid_pos in self.canvas.graphics_items:
                item_to_remove = self.canvas.graphics_items.pop(grid_pos)
                self.canvas.canvas.removeItem(item_to_remove)
                self.render_overlays.on_erase_block(grid_pos)

            return

        # --- HANDLE PLACING / UPDATING ---
        # first, remove any old visual item at the target location
        if grid_pos in self.canvas.graphics_items:
            old_item = self.canvas.graphics_items.pop(grid_pos)
            self.canvas.canvas.removeItem(old_item)

        # handle team swapping for the item
        current_team = self.communicator.team
        if placing.sprite.properties.can_swap_teams and placing.sprite.team != current_team:
            placing.swap_team(current_team)

        # get the pixmap and apply rotation if needed
        pixmap: QPixmap = placing.sprite.image
        if pixmap is None:
            line = inspect.currentframe().f_lineno
            fn = os.path.basename(__file__)
            print(f"Warning: Failed to get image for {placing.name_data.name} at line {line} of {fn}")
            return

        if placing.sprite.properties.is_rotatable:
            pixmap = self._rotate_blob(pixmap, rot)

        # --- ADD THE NEW ITEM TO THE SCENE AND UPDATE MODELS ---
        # create the new QGraphicsPixmapItem
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scale = self.canvas.default_zoom_scale
        pixmap_item.setScale(scale)

        # adjust position for rotation to keep it centered in the grid cell
        w, h = pixmap.width() * scale, pixmap.height() * scale
        adjusted_x, adjusted_y = scene_pos.x, scene_pos.y
        if rot in (90, 270):
            adjusted_x += (h - w) / 2
            adjusted_y += (w - h) / 2

        # apply the item's specific pixel offset
        offset_x, offset_y = placing.sprite.offset
        pixmap_item.setPos(float(adjusted_x + offset_x), float(adjusted_y + offset_y))
        pixmap_item.setZValue(placing.sprite.z)

        # finally, add the item to the scene and update our tracking dictionaries
        self.canvas.canvas.addItem(pixmap_item)
        self.canvas.graphics_items[grid_pos] = pixmap_item
        self.canvas.tilemap[grid_pos] = placing

        self.render_overlays.on_place_block(placing, grid_pos)

    def render_cursor(self, pos: Vec2f) -> None:
        """
        Renders the cursor on the canvas at the given scene position.

        Args:
            pos (Vec2f): The position where the cursor should be rendered.
        """
        if self.cursor_graphics_item is None:
            self.setup_cursor()

        # this can fail if the scene was cleared, so we wrap it in a try-except
        try:
            # main cursor
            self.cursor_graphics_item[0].setPos(pos.x, pos.y)
            self.cursor_graphics_item[0].show()

            # mirrored cursor
            if self.communicator.settings.get("mirrored over x", False):
                grid_x = pos.x / self.canvas.grid_spacing
                mirrored_grid_x = self.canvas.size.x - 1 - grid_x
                mirrored_scene_x = mirrored_grid_x * self.canvas.grid_spacing

                self.cursor_graphics_item[1].setPos(mirrored_scene_x, pos.y)
                self.cursor_graphics_item[1].show()

            else:
                self.cursor_graphics_item[1].hide()

        except (RuntimeError, IndexError):
            # underlying C++ object was deleted, likely on a map resize/clear, recreate it
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
            cursor.setZValue(1_000_000) # ensure cursor is always on top
            scale = self.canvas.default_zoom_scale * (8 / 10)
            cursor.setScale(scale)
            self.canvas.canvas.addItem(cursor)
            items.append(cursor)

        items[1].hide() # hide mirrored cursor by default
        self.cursor_graphics_item = items

    def _rotate_blob(self, pixmap: QPixmap, degrees: int) -> QPixmap:
        """Rotates a QPixmap by a given number of degrees."""
        if degrees == 0:
            return pixmap
        return pixmap.transformed(QTransform().rotate(degrees))
