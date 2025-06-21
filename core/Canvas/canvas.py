"""
Used to display images and interact with the map.
"""

import atexit
import math
import os
from datetime import datetime

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QBrush, QColor, QCursor, QKeySequence, QPainter, QPen, QShortcut
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QSizePolicy

from base.citem import CItem
from base.citemlist import CItemList
from base.kag_image import KagImage
from base.renderer import Renderer
from core.Canvas.canvas_input_handler import CanvasInputHandler
from core.Canvas.canvas_history_manager import HistoryManager
from core.Canvas.canvas_grid_manager import GridManager
from core.Canvas.canvas_commands import PlaceTileCommand
from core.communicator import Communicator
from utils.vec2f import Vec2f

class Canvas(CanvasInputHandler):
    """
    The main drawing and interaction surface within the map maker.
    It manages the display and manipulation of map elements while handling user input.
    """
    def __init__(self, size: Vec2f) -> None:
        super().__init__()
        self.gpu_rendering = True
        self.exec_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir)
        self.canvas = QGraphicsScene()
        self.renderer = Renderer(self)

        self.setViewport(QOpenGLWidget())
        self.canvas.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex) # disable warnings
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

        self.communicator = Communicator()
        self.setScene(self.canvas)
        self.size = size # map size

        self.zoom_change_factor = 1.1

        self.default_zoom_scale = 3 # scales zoom level up from small to comfortable

        self.setMouseTracking(True) # allow for constant update of cursor position (mouseMoveEvent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, False)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(165, 189, 200, 255)) # background color
        self.setMinimumSize(200, 200)
        self.setMaximumSize(1000, 1000)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.grid_spacing = math.floor(self.default_zoom_scale * 8)

        self.history_manager = HistoryManager()

        self._build_background_rect()

        # list of CItems
        self.tilemap = {}
        # list of sprites on the canvas
        self.graphics_items = {}

        self.grid_manager = GridManager(self)
        self.grid_manager.build_grid()

        self.item_list = CItemList()
        self.rotation = 0

        # save map on exiting the app
        atexit.register(self._save_map_at_exit, datetime.now())

        # create shortcuts for handling key events
        self.create_shortcuts()

        self.add_panning_space()

    def recenter_canvas(self) -> None:
        self.centerOn(self.size.x * self.grid_spacing / 2, self.size.y * self.grid_spacing / 2)

    def add_panning_space(self):
        # internal map size
        internal_map_width = self.size.x * self.grid_spacing
        internal_map_height = self.size.y * self.grid_spacing

        # desired view size (ie: viewport size)
        desired_view_width = self.viewport().width()
        desired_view_height = self.viewport().height()

        # calculate the extra space for panning
        s = .8 # as a percentage
        extra_width = desired_view_width * s
        extra_height = desired_view_height * s

        # set the scene rect to allow panning
        self.scene().setSceneRect(
            -extra_width, -extra_height,
            internal_map_width + 2 * extra_width,
            internal_map_height + 2 * extra_height
        )

        self.setSceneRect(self.scene().sceneRect())
        self.centerOn(internal_map_width / 2, internal_map_height / 2)

    def create_shortcuts(self):
        """
        Creates global shortcuts to rotation.
        """
        # r key
        r_shortcut = QShortcut(QKeySequence(Qt.Key.Key_R), self)
        r_shortcut.activated.connect(lambda: self.rotate(False))

        # shift + r
        modifier = Qt.KeyboardModifier.ShiftModifier
        shift_r_shortcut = QShortcut(QKeySequence(modifier | Qt.Key.Key_R), self)
        shift_r_shortcut.activated.connect(lambda: self.rotate(True))

        # ctrl + z
        modifier = Qt.KeyboardModifier.ControlModifier
        ctrl_z_shortcut = QShortcut(QKeySequence(modifier | Qt.Key.Key_Z), self)
        ctrl_z_shortcut.activated.connect(self._undo)

        # ctrl + y
        ctrl_y_shortcut = QShortcut(QKeySequence(modifier | Qt.Key.Key_Y), self)
        ctrl_y_shortcut.activated.connect(self._redo)

    def _undo(self) -> None:
        """
        Undoes the last action performed on the canvas.
        Moves back one step in the canvas history if available.

        Returns:
            None
        """
        self.history_manager.undo()

    def _redo(self) -> None:
        """
        Redoes the previously undone action on the canvas.
        Moves forward one step in the canvas history if available.

        Returns:
            None
        """
        self.history_manager.redo()

    def wipe_history(self) -> None:
        """
        Wipes future history entries when a new action is performed after undoing.

        Returns:
            None
        """
        self.history_manager.clear()

    def force_rerender(self) -> None:
        """
        Re-renders the entire canvas by re-drawing all items in the tilemap.

        Args:
            None

        Returns:
            None
        """
        self.canvas.clear()
        self._build_background_rect()

        # clear the graphics_items dictionary
        if hasattr(self, 'graphics_items'):
            self.graphics_items.clear()

        # redraw all items
        # needs to be a copy because they can change here
        for pos, item in list(self.tilemap.items()):
            if pos is None or item is None:
                continue

            x, y = pos
            scene_pos = Vec2f(x, y) * self.grid_spacing

            self.renderer.render_item(item, scene_pos, Vec2f(x, y), False, item.sprite.rotation)

    def set_grid_visible(self, show: bool = None) -> None:
        self.grid_manager.set_grid_visible(show)

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

    def _save_map_at_exit(self, timestamp: datetime) -> None:
        """
        Save the map at the specified timestamp if the map is not blank.

        Args:
            timestamp (datetime): The timestamp to use for the file name.

        Returns:
            None
        """
        # check if map is blank
        if not self.tilemap:
            print("Map is blank. Not saving.")
            return

        date_str = timestamp.strftime("%d-%m-%Y")
        path = os.path.join(self.exec_path, "Maps", "Autosave", date_str)

        # ensure the directory exists, create it if it doesn't
        os.makedirs(path, exist_ok=True)

        file_name = timestamp.strftime("%d-%m-%Y_%H-%M-%S")
        file_path = os.path.join(path, file_name)

        KagImage().save_map(file_path + ".png")

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
        rect.setZValue(-1000000)
        self.canvas.addItem(rect)

    def add_item(self, event, click_index: int) -> None:
        """
        Requests to add an item at a position, and interpolates to draw a line
        of items between the last position and the current one.
        """
        recent_pos = self.communicator.mouse_pos
        pos = self.get_grid_pos(event)

        # if the mouse hasn't moved to a new grid cell, do nothing.
        if pos == recent_pos:
            return

        # check if the positions are valid before proceeding
        # the 'or not recent_pos' part handles the very first click of a drag
        if not pos or not recent_pos:
            return

        # --- line drawing logic ---
        delta = (pos[0] - recent_pos[0], pos[1] - recent_pos[1])
        steps = max(abs(delta[0]), abs(delta[1]))

        # if the mouse only moved one cell away, just place one item
        if steps <= 1:
            self.place_item(pos, click_index)

        else:
            # draw a line of tiles between the last point and the current one
            for i in range(steps + 1):
                # linear interpolation to find each point on the line
                x = round(recent_pos[0] + i * delta[0] / steps)
                y = round(recent_pos[1] + i * delta[1] / steps)
                grid_pos = (x, y)

                self.place_item(grid_pos, click_index)

        # update the mouse position after the line has been drawn
        self.update_mouse_pos(event)

    def perform_place_item(self, grid_pos: tuple, placing_item: CItem):
        """
        The RAW action of placing a tile. It modifies the tilemap and calls the renderer.
        """
        placing_item = placing_item.copy()
        eraser: bool = placing_item.is_eraser()
        mirror = self.communicator.settings.get("mirrored over x", False)

        if self.is_out_of_bounds(grid_pos):
            return

        tilemap_x, tilemap_y = grid_pos
        snapped_pos = Vec2f(tilemap_x, tilemap_y)

        # --- ERASE LOGIC ---
        if eraser:
            if snapped_pos not in self.tilemap:
                return # nothing to erase

            # update data
            self.tilemap.pop(snapped_pos)

            # calculate scene position
            scene_pos = Vec2f(tilemap_x * self.grid_spacing, tilemap_y * self.grid_spacing)

            # call renderer with the 'eraser' item and the calculated scene_pos
            self.renderer.render_item(placing_item, scene_pos, snapped_pos, eraser=True, rot=0)

            # handle mirrored erasing
            if mirror:
                mirrored_x = self.size.x - 1 - tilemap_x
                if not self.is_out_of_bounds((mirrored_x, tilemap_y)) and mirrored_x != tilemap_x:
                    mirrored_snapped_pos = Vec2f(mirrored_x, tilemap_y)
                    # calculate scene position for the mirrored tile as well
                    mirrored_scene_pos = Vec2f(mirrored_x * self.grid_spacing, tilemap_y * self.grid_spacing)
                    self.renderer.render_item(placing_item, mirrored_scene_pos, mirrored_snapped_pos, eraser=True, rot=0)

            return

        # --- PLACE LOGIC ---
        # update data
        self.tilemap[snapped_pos] = placing_item

        # update renderer (visual)
        scene_pos = Vec2f(tilemap_x * self.grid_spacing, tilemap_y * self.grid_spacing)
        if placing_item.sprite.properties.is_rotatable:
            placing_item.sprite.rotation = self.rotation
        self.renderer.render_item(placing_item, scene_pos, snapped_pos, eraser=False, rot=self.rotation)

        # handle mirrored placing
        if mirror:
            mirrored_x = self.size.x - 1 - tilemap_x
            if not self.is_out_of_bounds((mirrored_x, tilemap_y)) and mirrored_x != tilemap_x:
                mirrored_scene_pos = Vec2f(mirrored_x * self.grid_spacing, scene_pos.y)
                mirrored_snapped_pos = Vec2f(mirrored_x, tilemap_y)
                mirrored_item = placing_item.copy()

                self.renderer.render_item(mirrored_item, mirrored_scene_pos, mirrored_snapped_pos, eraser=False, rot=self.rotation)

    def _get_merged_item(self, placing_item: CItem, grid_pos: tuple) -> CItem:
        """
        Checks if a tile should be merged and returns the final CItem to be placed.
        Returns the original item if no merge occurs.
        """
        snapped_pos = Vec2f(*grid_pos)
        tile_at_pos = self.tilemap.get(snapped_pos)

        # no existing tile, or items are not mergeable
        if not tile_at_pos or not (placing_item.is_mergeable() or tile_at_pos.is_mergeable()):
            return placing_item # return the original item

        # --- perform merge logic ---
        # try merging the new tile onto the old one
        merged_name = placing_item.merge_with(tile_at_pos.name_data.name)
        new_item = self.item_list.get_item_by_name(merged_name)

        # if that didn't work, try merging the old item onto the new one
        if new_item is None:
            merged_name = tile_at_pos.merge_with(placing_item.name_data.name)
            new_item = self.item_list.get_item_by_name(merged_name)

        if new_item:
            if new_item.name_data.name == tile_at_pos.name_data.name:
                # return the existing tile to signify no change
                return tile_at_pos

            # return the new, merged item
            return new_item.copy()

        # return the original if merge fails to produce a valid item
        return placing_item

    def place_item(self, grid_pos, click_index: int, item: CItem = None, add_to_history: bool = True) -> None:
        """
        Creates a PlaceTileCommand and executes it via the history manager.
        Handles high-level logic like merging before performing the action.
        """
        if self.is_out_of_bounds(grid_pos):
            return

        # --- determine the initial item to place ---
        initial_item = item
        # new action from the user
        if add_to_history:
            initial_item = self.communicator.get_selected_tile(click_index).copy()

        # handle the case where an undo/redo action passes a None item (erasing)
        if initial_item is None:
            initial_item = self.item_list.get_item_by_name('sky').copy()

        # --- perform the merge check to get the final item ---
        final_item = self._get_merged_item(initial_item, grid_pos)

        # --- check if anything needs to be done ---
        snapped_pos = Vec2f(*grid_pos)
        previous_item = self.tilemap.get(snapped_pos)

        # if the final item is the same as what's already there, do nothing.
        # this prevents creating unnecessary history entries.
        if previous_item and previous_item.name_data.name == final_item.name_data.name:
            # also check rotation for rotatable items
            if not final_item.sprite.properties.is_rotatable or previous_item.sprite.rotation == self.rotation:
                return

        # if the user is trying to erase an empty space, do nothing.
        if previous_item is None and (final_item.is_eraser() or final_item.name_data.name == 'sky'):
            return

        # --- execute the action ---
        if not add_to_history:
            # undo/redo
            self.perform_place_item(grid_pos, final_item)
        else:
            # this is a new user action, create a command and execute it
            # IMPORTANT: the command stores the state *before* the merge.
            command = PlaceTileCommand(self, grid_pos, final_item, previous_item)
            self.history_manager.execute_command(command)

    def snap_to_grid(self, pos) -> tuple:
        """
        Snaps a given position to the nearest grid point.

        Args:
            pos (tuple): The position to be snapped to the grid.

        Returns:
            tuple: The snapped position as a tuple of two integers.
        """
        x, y = pos
        return (int(x // self.grid_spacing), int(y // self.grid_spacing))

    def get_grid_pos(self, event) -> tuple:
        """
        Gets the grid position of the given event.

        Args:
            event: The event to get the grid position from.

        Returns:
            tuple: The grid position as a tuple of two integers.
        """

        pos = self.mapToScene(event.pos())
        return self.snap_to_grid((pos.x(), pos.y()))

    def update_mouse_pos(self, event) -> None:
        """
        Updates the mouse position to the given event.

        Args:
            event: The event to update the mouse position to.

        Returns:
            None
        """

        self.communicator.old_mouse_pos = self.communicator.mouse_pos
        self.communicator.mouse_pos = self.get_grid_pos(event)

    def resize_canvas(self, size: Vec2f, tilemap: dict[Vec2f, CItem] = None) -> None:
        self.size = size
        if tilemap is None:
            tilemap = {}

        self.tilemap = tilemap
        self.force_rerender()
        self.add_panning_space()
        print(f"New map created with dimensions: {size.x}x{size.y}")
        self.wipe_history()
        self.grid_manager.build_grid()

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

    def get_cursor_pos_on_canvas(self) -> QPoint:
        return self.mapFromGlobal(QCursor.pos())
