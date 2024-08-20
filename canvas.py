"""
Used to display images and interact with the map.
"""

import atexit
import math
import os
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap, QTransform
from PyQt6.QtWidgets import (QGraphicsItemGroup, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView)

from base.cblob_list import CBlobList
from base.ctile_list import CTileList
from base.kag_image import KagImage
from base.renderer import Renderer
from core.scripts.communicator import Communicator
from utils.vec import vec

class Canvas(QGraphicsView):
    """
    The main drawing and interaction surface within the map maker.
    It manages the display and manipulation of map elements while handling user input.
    """
    def __init__(self, size: tuple) -> None:
        super().__init__()
        self.exec_path = os.path.dirname(os.path.realpath(__file__))
        self.renderer = Renderer()
        self.canvas = QGraphicsScene()
        self.canvas.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex) # disable warnings
        self.communicator = Communicator()
        self.communicator.set_canvas(self)
        self.setScene(self.canvas)
        self.geometry = vec(300, 300)
        self.size = size # map size
        self.grid_group = QGraphicsItemGroup()

        self.zoom_change_factor = 1.1

        self.default_zoom_scale = 3 # scales zoom level up from small to comfotable
        self.zoom_factor = 1        # current zoom
        self.zoom_minmax = [0.1, 5] # max zoom (count default_zoom_scale as 1)

        self.setMouseTracking(True) # allow for constant update of cursor position (mouseMoveEvent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(165, 189, 200, 255)) # background color
        self.setMinimumSize(200, 200) # cannot be smaller than this
        self.setMaximumSize(1000, 1000) # TODO: should be resizable but isnt?
        self.grid_spacing = math.floor(self.zoom_factor * self.default_zoom_scale * 8)
        self._build_background_rect()

        self.holding_lmb = False
        self.holding_rmb = False
        self.holding_scw = False
        self.holding_shift = False

        self.current_cursor_pos = [0, 0] # updates every frame to current cursor position
        self._last_pan_point = None

        # TODO: this should be a dictionary of positions instead of a 2d array
        self.tilemap = [[None for _ in range(self.size[1])] for _ in range(self.size[0])]
        self.graphics_items = {}

        self._build_tile_grid()
        self.set_grid_visible(False) # should be a setting but disabled by default

        self.tile_list = CTileList()
        self.blob_list = CBlobList()

        # TODO: be able to resize canvas for the 'new' map button

        # SAVE MAP WHEN EXITING MAP MAKER
        atexit.register(self._save_map_at_exit, datetime.now())

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

    # TODO: need to verify this chatgpt code isnt trash
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

        # Clear the graphics_items dictionary
        if hasattr(self, 'graphics_items'):
            self.graphics_items.clear()

        # Rebuild the grid
        self._build_tile_grid()

        # Redraw all items
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                item = self.tilemap[x][y]
                if item is not None:
                    scene_x = x * self.grid_spacing
                    scene_y = y * self.grid_spacing
                    scene_pos = vec(scene_x, scene_y)
                    self.renderer.render(item.name, scene_pos, vec(x, y), False)

    # TODO: shouldnt pass name string, instead should just use communicator to get name
    def _using_eraser(self, name: str) -> bool:
        """
        Check if a name for a tile or blob exists.

        Args:
            name (str): The name of the tile or blob to check for.

        Returns:
            bool: True if the position is empty, False otherwise.
        """
        if self.tile_list.get_tile_by_name(name): # TODO: doestileexist method
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

        for x in range(0, self.size[0] * self.grid_spacing + 1, self.grid_spacing):
            line = self.canvas.addLine(x, 0, x, self.size[0] * self.grid_spacing, pen)
            self.grid_group.addToGroup(line)

        # Create horizontal grid lines
        for y in range(0, self.size[1] * self.grid_spacing + 1, self.grid_spacing):
            line = self.canvas.addLine(0, y, self.size[1] * self.grid_spacing, y, pen)
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
        width, height = self.size[0] * self.grid_spacing, self.size[1] * self.grid_spacing
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

        placing_tile: str = self.communicator.get_selected_tile(click_index)
        eraser: bool = self._using_eraser(placing_tile)

        # do nothing if out of bounds
        if self.is_out_of_bounds(pos):
            return

        grid_x, grid_y = pos # for the 2d array 'tilemap' # TODO: should be more clear w/ var name
        scene_x = grid_x * self.grid_spacing # for the actual location on the canvas
        scene_y = grid_y * self.grid_spacing

        scene_pos = vec(scene_x, scene_y)
        snapped_pos = vec(grid_x, grid_y)
        self.renderer.render(placing_tile, scene_pos, snapped_pos, eraser)

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

        # Remove existing item if present
        if self.tilemap[x][y] is not None:
            self.remove_existing_item_from_scene((x, y))

        if img is None:
            print(f"Warning: img is None for item {name} at position {pos}")
            return None

        # create new item
        pixmap_item = QGraphicsPixmapItem(img)
        pixmap_item.setScale(self.zoom_factor * self.default_zoom_scale)
        width, height = img.width(), img.height()
        pixmap_item.setPos(int(pos[0] - width), int(pos[1] - height))
        pixmap_item.setZValue(z)

        self.canvas.addItem(pixmap_item)

        self.graphics_items[(x, y)] = pixmap_item

        return pixmap_item

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
        self.current_cursor_pos = event.pos()
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

    def keyPressEvent(self, event) -> None:
        """
        Handles key press events on the canvas.

        Parameters:
            event: A Qt event object containing information about the key press.

        Returns:
            None
        """
        if event.key() == Qt.Key.Key_Shift:
            self.holding_shift = True

    def keyReleaseEvent(self, event) -> None:
        """
        Handles key release events on the canvas.

        Parameters:
            event: A Qt event object containing information about the key release.

        Returns:
            None
        """
        if event.key() == Qt.Key.Key_Shift:
            self.holding_shift = False

    # TODO: fix this chatgpt code so it zooms into cursor and not randomly on canvas
    def wheelEvent(self, event) -> None:
        """
        Handles wheel events on the canvas, allowing for zooming and panning.

        Parameters:
            event: A Qt event object containing information about the wheel event.

        Returns:
            None
        """
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoom_in_factor = self.zoom_change_factor
            zoom_out_factor = 1 / zoom_in_factor

            # Get the position before scaling, in scene coords
            old_pos = self.mapToScene(self.current_cursor_pos)

            scale_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
            # Calculate the new scale factor and clamp it
            new_scale = self.transform().m11() * scale_factor
            min_scale = self.zoom_minmax[0]  # Minimum zoom level
            max_scale = self.zoom_minmax[1]   # Maximum zoom level

            if min_scale <= new_scale <= max_scale:
                self.scale(scale_factor, scale_factor)

                # Get the position after scaling, in scene coords
                new_pos = self.mapToScene(self.current_cursor_pos)

                # Move scene to old position
                delta = new_pos - old_pos
                self.translate(delta.x(), delta.y())

            else:
                # Keep the scene fixed if at zoom limits
                if new_scale < min_scale:
                    self.setTransform(QTransform().scale(min_scale, min_scale))

                elif new_scale > max_scale:
                    self.setTransform(QTransform().scale(max_scale, max_scale))
        else:
            # Determine the current spacing considering the zoom factor
            curr_space = self.grid_spacing / self.transform().m11()

            vscrollval = self.verticalScrollBar().value()
            hscrollval = self.horizontalScrollBar().value()

            if event.angleDelta().y() > 0: # move view down
                self.verticalScrollBar().setValue(vscrollval - int(curr_space))
            else: # move view up
                self.verticalScrollBar().setValue(vscrollval + int(curr_space))

            if event.angleDelta().x() > 0: # move view right
                self.horizontalScrollBar().setValue(hscrollval - int(curr_space))
            elif event.angleDelta().x() < 0: # move view left
                self.horizontalScrollBar().setValue(hscrollval + int(curr_space))

        super().wheelEvent(event)

    def is_out_of_bounds(self, pos: tuple) -> bool:
        """
        Check if the given position is out of bounds.

        Args:
            pos (tuple): The position to check, represented as a tuple of (x, y) coordinates.

        Returns:
            bool: True if the position is out of bounds, False otherwise.
        """
        x, y = pos
        return x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]
