"""
Used to display images and interact with the map.
"""

import atexit
import math
import os
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap, QShortcut, QKeySequence
from PyQt6.QtWidgets import (QGraphicsItemGroup, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsView, QSizePolicy)

from base.cblob import CBlob
from base.cblob_list import CBlobList
from base.ctile import CTile
from base.ctile_list import CTileList
from base.kag_image import KagImage
from base.renderer import Renderer
from core.communicator import Communicator
from utils.vec2f import Vec2f


class Canvas(QGraphicsView):
    """
    The main drawing and interaction surface within the map maker.
    It manages the display and manipulation of map elements while handling user input.
    """
    def __init__(self, size: Vec2f) -> None:
        super().__init__()
        self.exec_path = os.path.dirname(os.path.realpath(__file__))
        self.renderer = Renderer()
        self.canvas = QGraphicsScene()
        self.canvas.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex) # disable warnings
        self.communicator = Communicator()
        self.setScene(self.canvas)
        # self.geometry = Vec2f(300, 300)
        self.size = size # map size
        self.grid_group = QGraphicsItemGroup()

        self.zoom_change_factor = 1.1

        self.default_zoom_scale = 3 # scales zoom level up from small to comfortable
        self.zoom_factor = 1        # current zoom

        self.setMouseTracking(True) # allow for constant update of cursor position (mouseMoveEvent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(165, 189, 200, 255)) # background color
        self.setMinimumSize(200, 200)
        self.setMaximumSize(1000, 1000)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.grid_spacing = math.floor(self.zoom_factor * self.default_zoom_scale * 8)

        self._build_background_rect()

        self.holding_lmb = False
        self.holding_rmb = False
        self.holding_scw = False
        self.holding_shift = False

        self._last_pan_point = None

        self.tilemap = [[None for _ in range(self.size.y)] for _ in range(self.size.x)]
        self.graphics_items = {}

        self._build_tile_grid()
        self.set_grid_visible(False) # should be a setting but disabled by default

        self.tile_list = CTileList()
        self.blob_list = CBlobList()

        self.rotation = 0

        # SAVE MAP WHEN EXITING MAP MAKER
        atexit.register(self._save_map_at_exit, datetime.now())

        # create shortcuts for handling key events
        self.create_shortcuts()

    def create_shortcuts(self):
        """
        Creates global shortcuts to rotation.
        """
        # space key
        space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        space_shortcut.activated.connect(self.handle_space_press)

        # shift + space
        modifier = Qt.KeyboardModifier.ShiftModifier
        shift_space_shortcut = QShortcut(QKeySequence(modifier | Qt.Key.Key_Space), self)
        shift_space_shortcut.activated.connect(self.handle_shift_space_press)

    def handle_space_press(self):
        """
        Handles Space key press.
        """
        self.rotate(False)

    def handle_shift_space_press(self):
        """
        Handles Shift + Space key press.
        """
        self.rotate(True)

    def get_tilemap(self) -> list:
        """
        Returns the current tilemap of the canvas.

        Args:
            None

        Returns:
            list: A 2D list representing the map.
        """
        return self.tilemap

    def get_size(self) -> tuple:
        """
        Returns the size of the canvas as a tuple.

        Args:
            None

        Returns:
            tuple: A tuple containing the width and height of the canvas.
        """
        return self.size

    def set_grid_visible(self, show: bool = None) -> None:
        """
        Toggles the visibility of the grid on the canvas.

        Args:
            show (bool): Whether to show or hide the grid, or toggle if not specified.

        Returns:
            None
        """
        is_visible: bool = self.grid_group.isVisible()
        if self.grid_group:
            self.grid_group.setVisible(show if show is not None else not is_visible)

    def force_rerender(self) -> None:
        """
        Re-renders the entire canvas by re-drawing all items in the tilemap.

        Args:
            None

        Returns:
            None
        """
        # Clear the canvas
        self.canvas.clear()

        self._build_background_rect()

        # Clear the graphics_items dictionary
        if hasattr(self, 'graphics_items'):
            self.graphics_items.clear()

        # Redraw all items
        for x in range(self.size.x):
            for y in range(self.size.y):
                item = self.tilemap[x][y]
                if item is not None:
                    scene_x = x * self.grid_spacing
                    scene_y = y * self.grid_spacing
                    scene_pos = Vec2f(scene_x, scene_y)
                    self.renderer.render(item.name, scene_pos, Vec2f(x, y), False, self.rotation)

    def rotate(self, rev: bool) -> None:
        """
        Rotates the selected item by 90 degrees, either clockwise or counter-clockwise.

        Args:
            rev (bool): Whether to rotate clockwise (True) or counter-clockwise (False).

        Returns:
            None
        """
        r = self.rotation
        add = -90 if rev else 90

        r = (r + add) % 360

        if r < 0:
            r += 360
        elif r >= 360:
            r -= 360

        self.rotation = r

    def _using_eraser(self, name) -> bool:
        """
        Check if a name for a tile or blob exists.

        Args:
            name (str): The name of the tile or blob to check for.

        Returns:
            bool: True if the position is empty, False otherwise.
        """
        if isinstance(name, CTile) or isinstance(name, CBlob):
            name = name.name

        if name == "tile_empty":
            return True

        if self.tile_list.does_tile_exist(name):
            return False

        if self.blob_list.does_blob_exist(name):
            return False

        return True

    def _build_tile_grid(self) -> None:
        """
        Builds a tile grid on the canvas by creating grid lines.

        Args:
            None

        Returns:
            None
        """
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)

        self.grid_group = QGraphicsItemGroup()

        for x in range(0, self.size.x * self.grid_spacing + 1, self.grid_spacing):
            line = self.canvas.addLine(x, 0, x, self.size.x * self.grid_spacing, pen)
            self.grid_group.addToGroup(line)

        # Create horizontal grid lines
        for y in range(0, self.size.y * self.grid_spacing + 1, self.grid_spacing):
            line = self.canvas.addLine(0, y, self.size.y * self.grid_spacing, y, pen)
            self.grid_group.addToGroup(line)

        self.canvas.addItem(self.grid_group)

    def _save_map_at_exit(self, timestamp: datetime) -> None:
        """
        Save the map at the specified timestamp if the map is not blank.

        Args:
            timestamp (datetime): The timestamp to use for the file name.

        Returns:
            None
        """
        # check if map is blank
        if all(all(tile is None for tile in row) for row in self.tilemap):
            print("Map is blank. Not saving.")
            return

        date_str = timestamp.strftime("%d-%m-%Y")
        path = os.path.join(self.exec_path, "Maps", "Autosave", date_str)

        # ensure the directory exists, create it if it doesn't
        os.makedirs(path, exist_ok=True)

        file_name = timestamp.strftime("%d-%m-%Y_%H-%M-%S")
        file_path = os.path.join(path, file_name)

        KagImage().save_map(file_path + ".png")
        print(f"Map saved to: {file_path}")

    def _build_background_rect(self) -> None:
        """
        Builds a background rectangle for the canvas.

        Args:
            None

        Returns:
            None
        """
        background_color = QColor(200, 220, 240)
        width, height = self.size.x * self.grid_spacing, self.size.y * self.grid_spacing
        pen = QPen(Qt.GlobalColor.transparent)
        rect = self.canvas.addRect(0, 0, width, height, pen, QBrush(background_color))
        self.canvas.addItem(rect)

    def _place_item(self, event, click_index: int) -> None:
        """
        Places an item on the canvas based on the given event and click index.

        Args:
            event: The event that triggered the item placement.
            click_index: The index of the click that triggered the item placement.

        Returns:
            None
        """
        pos = self.mapToScene(event.pos())
        pos = self._snap_to_grid((pos.x(), pos.y()))

        placing_tile = self.communicator.get_selected_tile(click_index)

        eraser: bool = self._using_eraser(placing_tile)

        # do nothing if out of bounds
        if self.is_out_of_bounds(pos):
            return

        tilemap_x, tilemap_y = pos
        scene_x = tilemap_x * self.grid_spacing # for the location on the canvas
        scene_y = tilemap_y * self.grid_spacing

        scene_pos = Vec2f(scene_x, scene_y)
        snapped_pos = Vec2f(tilemap_x, tilemap_y)
        self.renderer.render(placing_tile, scene_pos, snapped_pos, eraser, self.rotation)

    def remove_existing_item_from_scene(self, pos: tuple) -> None:
        """
        Removes an existing item from the scene at the specified position (in tilemap coordinates).

        Args:
            pos (tuple): The position of the item to be removed.

        Returns:
            None
        """
        x, y = pos
        if self.tilemap[x][y] is not None:
            if (x, y) in self.graphics_items:
                self.canvas.removeItem(self.graphics_items[(x, y)])
                del self.graphics_items[(x, y)]
            self.tilemap[x][y] = None

    def add_to_canvas(self, img: QPixmap, pos: tuple, z: int, name: str) -> QGraphicsPixmapItem:
        """
        Adds an item to the canvas at the specified position.

        Args:
            img (QPixmap): The pixmap to be added to the canvas.
            pos (tuple): The position of the item in the canvas.
            z (int): The z-value of the item.
            name (str): The name of the item.

        Returns:
            QGraphicsPixmapItem: The added pixmap item, or None if the pixmap is None.
        """
        x, y = self._snap_to_grid(pos)

        # remove existing item if present
        if self.tilemap[x][y] is not None:
            self.remove_existing_item_from_scene((x, y))

        if img is None:
            print(f"Warning: img is None for item {name} at position {pos}")
            return None

        # create new item
        pixmap_item = QGraphicsPixmapItem(img)
        pixmap_item.setScale(self.zoom_factor * self.default_zoom_scale)

        # TODO: fix this code with proper offsets
        newpos = self.__get_offset(name, img)
        pixmap_item.setPos(int(pos[0] - newpos.x), int(pos[1] - newpos.y))
        pixmap_item.setZValue(z)

        self.canvas.addItem(pixmap_item)

        self.graphics_items[(x, y)] = pixmap_item

        return pixmap_item

    # using this function until better solution is found so mapmaker is usable
    # TODO: (MAYBE) each of the blobs should have a template, and include offset position
    # TODO: these should snap to the grid
    def __get_offset(self, name: str, sprite: QPixmap) -> Vec2f:
        w, h = sprite.width(), sprite.height()
        zf, zs = self.zoom_factor, self.default_zoom_scale

        # TODO: check if these offsets correctly load into KAG with how they currently are viewed
        # place from bottom center + offset
        if name == "tree" or name == "grain" or name == "tent":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "ballista":
            return Vec2f(w + (8 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "catapult":
            return Vec2f(w + (4 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "bomber":
            return Vec2f(w + (4 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "airship":
            return Vec2f(w + (8 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "bison":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "chest":
            return Vec2f(w - (2 * zf * zs), ((h * zf * zs) - (10 * zf * zs)))

        if name == "chicken":
            return Vec2f(w - (2 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "crate":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "ctf_flag":
            return Vec2f(w + (14 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "dinghy":
            return Vec2f(w, ((h * zf * zs) - (12 * zf * zs)))

        if name == "dummy":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "ladder":
            return Vec2f(w - (2 * zf * zs), ((h * zf * zs) - (16 * zf * zs)))

        if name == "keg":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "longboat":
            return Vec2f(w, ((h * zf * zs) - (12 * zf * zs)))

        if name == "mine":
            return Vec2f(w - (2 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "mounted_bow":
            return Vec2f(w - (6 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "necromancer" or name == "princess":
            return Vec2f(w - (8 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        if name == "nursery":
            return Vec2f(w + (2 * zf * zs), ((h * zf * zs) - (16 * zf * zs)))

        if name == "raft":
            return Vec2f(w + (4 * zf * zs), ((h * zf * zs) - (14 * zf * zs)))

        if name == "saw":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "shark":
            return Vec2f(w, ((h * zf * zs) - (12 * zf * zs)))

        if name == "trampoline":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "workbench":
            return Vec2f(w, ((h * zf * zs) - (8 * zf * zs)))

        if name == "bush":
            return Vec2f(w - (2 * zf * zs), ((h * zf * zs) - (12 * zf * zs)))

        if "door" in name:
            return Vec2f(w - (2 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        names = [
            "mat_gold",
            "mat_stone",
            "mat_wood"
        ]

        if name in names:
            return Vec2f(w - (2 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        names = [
            "mat_firearrows",
            "mat_waterarrows",
            "mat_bombarrows"
        ]

        if name in names:
            return Vec2f(w - (3 * zf * zs), ((h * zf * zs) - (8 * zf * zs)))

        names = [
            "knight_shop",
            "builder_shop",
            "archer_shop",
            "barracks",
            "factory",
            "tunnel",
            "storage",
            "quarters",
            "kitchen",
            "boat_shop"
        ]

        # place from center
        if name in names:
            return Vec2f(w * 0.5 + (9 * zf * zs), h * 0.5 + (4 * zf * zs))

        return Vec2f(0, 0)

    def _snap_to_grid(self, pos) -> tuple:
        """
        Snaps a given position to the nearest grid point.

        Args:
            pos (tuple): The position to be snapped to the grid.

        Returns:
            tuple: The snapped position as a tuple of two integers.
        """
        x, y = pos
        return (int(x // self.grid_spacing), int(y // self.grid_spacing))

    def mousePressEvent(self, event) -> None:
        """
        Handles mouse press events on the canvas.

        Parameters:
            event: A Qt mouse event object containing information about the mouse press.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton: # place blocks
            self.holding_lmb = True

            self._place_item(event, 1)

        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = True

            self._place_item(event, 0)

        if event.button() == Qt.MouseButton.MiddleButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self._last_pan_point = event.pos()
            self.holding_scw = True
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event) -> None:
        """
        Handles mouse release events on the canvas.

        Parameters:
            event: A Qt mouse event object containing information about the mouse release.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.holding_lmb = False

        # elif to prevent placing two tiles at once
        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = False

        elif event.button() == Qt.MouseButton.MiddleButton:
            self.holding_scw = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().unsetCursor()

    def mouseMoveEvent(self, event) -> None:
        """
        Handles mouse movement events on the canvas.

        Parameters:
            event: A Qt mouse event object containing information about the mouse move.

        Returns:
            None
        """
        if self.holding_lmb:
            self._place_item(event, 1)

        elif self.holding_rmb:
            self._place_item(event, 0)

        if self.holding_scw:
            # Calculate how much the mouse has moved
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()

            # Scroll the view accordingly
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

    # todo: fully fix it still kind of snapping to edges
    def wheelEvent(self, event) -> None:
        """
        Handles wheel events on the canvas,
        allowing for zooming and panning without snapping to edges.

        Parameters:
            event: A Qt event object containing information about the wheel event.

        Returns:
            None
        """
        if event.angleDelta().y() > 0:
            factor = self.zoom_change_factor
        else:
            factor = 1 / self.zoom_change_factor

        view_pos = event.position()
        scene_pos = self.mapToScene(view_pos.toPoint())

        original_scene_rect = self.sceneRect()
        self.scale(factor, factor)

        new_pos = self.mapFromScene(scene_pos)
        delta = new_pos - view_pos.toPoint()

        # adjust scene rect to prevent snapping
        adjusted_scene_rect = self.mapToScene(self.viewport().rect()).boundingRect()

        # ensure adjusted rect is not smaller than the original
        adjusted_scene_rect = adjusted_scene_rect.united(original_scene_rect)
        self.setSceneRect(adjusted_scene_rect)

        # scroll the view to maintain the same relative position
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x())
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y())

    def is_out_of_bounds(self, pos: tuple) -> bool:
        """
        Check if the given position is out of bounds.

        Args:
            pos (tuple): The position to check, represented as a tuple of (x, y) coordinates.

        Returns:
            bool: True if the position is out of bounds, False otherwise.
        """
        x, y = pos
        return x < 0 or y < 0 or x >= self.size.x or y >= self.size.y
