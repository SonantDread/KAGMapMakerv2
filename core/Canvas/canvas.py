"""
Used to interact with the map.
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

from core.communicator import Communicator
from core.Canvas.canvas_input_handler import CanvasInputHandler
from core.Canvas.canvas_history_manager import HistoryManager
from core.Canvas.canvas_grid_manager import GridManager
from core.Canvas.canvas_commands import PlaceTileCommand

from utils.vec2f import Vec2f
from utils.file_handler import FileHandler

class Canvas(CanvasInputHandler):
    """
    The main drawing and interaction surface within the map maker.
    Manages the manipulation of map elements, handling user input.
    """
    def __init__(self, map_size: Vec2f) -> None:
        super().__init__()
        self.canvas = QGraphicsScene()
        self.renderer = Renderer(self)
        self.file_handler = FileHandler()

        self.setViewport(QOpenGLWidget())
        self.canvas.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex) # disable warnings
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate)

        self.communicator = Communicator()
        self.setScene(self.canvas)
        self.map_size = map_size

        self.zoom_change_factor = 1.1
        self.default_zoom_scale = 3

        self.setMouseTracking(True) # constant update of mouseMoveEvent
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

        # list of CItem
        self.tilemap = {}
        # list of sprites on the canvas
        self.graphics_items = {}

        self.grid_manager = GridManager(self)
        self.grid_manager.build_grid()

        self.item_list = CItemList()
        self.rotation = 0

        atexit.register(self._save_map_at_exit, datetime.now())
        self.create_shortcuts()
        self.add_panning_space()

    def recenter_canvas(self) -> None:
        """
        Centers the view of the canvas to the center.
        """
        pos_x = self.map_size.x * self.grid_spacing / 2
        pos_y = self.map_size.y * self.grid_spacing / 2
        self.centerOn(pos_x, pos_y)

    def add_panning_space(self) -> None:
        """
        Adds extra panning space to the canvas so users don't feel locked.
        """
        map_width = self.map_size.x * self.grid_spacing
        map_height = self.map_size.y * self.grid_spacing

        desired_view_width = self.viewport().width()
        desired_view_height = self.viewport().height()

        s = .8 # as a percentage
        extra_width = desired_view_width * s
        extra_height = desired_view_height * s

        scene = self.scene()
        scene.setSceneRect(
            -extra_width, -extra_height,
            map_width + 2 * extra_width,
            map_height + 2 * extra_height
        )

        self.setSceneRect(scene.sceneRect())
        self.centerOn(map_width / 2, map_height / 2)

    def create_shortcuts(self) -> None:
        """
        Binds keyboard shortcuts to canvas actions.
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
        """
        self.history_manager.undo()

    def _redo(self) -> None:
        """
        Redoes the previously undone action on the canvas.
        Moves forward one step in the canvas history if available.
        """
        self.history_manager.redo()

    def wipe_history(self) -> None:
        """
        Wipes future history entries when a new action is performed after undoing.
        """
        self.history_manager.clear()

    def force_rerender(self) -> None:
        """
        Re-renders the entire canvas by re-drawing all items in the tilemap.
        """
        self.canvas.clear()

        if self.renderer:
            self.renderer.cursor_graphics_item = None

            if self.renderer.render_overlays:
                self.renderer.render_overlays.overlay_item = None

        self._build_background_rect()
        self.grid_manager.build_grid()
        self.renderer.render_overlays.build_overlays()

        if hasattr(self, 'graphics_items'):
            self.graphics_items.clear()

        # redraw all items
        # needs to be a copy because they can change here
        for pos, item in list(self.tilemap.items()):
            if pos is None or item is None:
                continue

            scene_pos = pos * self.grid_spacing
            self.renderer.render_item(item, scene_pos, pos, False, item.sprite.rotation)

        if self.renderer and self.renderer.render_overlays:
            self.renderer.render_overlays.render_extra_overlay()

    def set_grid_visible(self, show: bool = None) -> None:
        """
        Sets the visibility of the grid on the canvas.
        """
        self.grid_manager.set_grid_visible(show)

    def rotate(self, rev: bool) -> None:
        """
        Rotates the selected item by 90 degrees, either clockwise or counter-clockwise.
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
        """
        if not self.tilemap:
            print("Map is blank. Not saving.")
            return

        date_str = timestamp.strftime("%d-%m-%Y")
        path = os.path.join(self.file_handler.paths.get("autosave_path"), date_str)

        os.makedirs(path, exist_ok=True)

        file_name = timestamp.strftime("%d-%m-%Y_%H-%M-%S")
        file_path = os.path.join(path, file_name)

        KagImage().save_map(file_path + ".png")

    def _build_background_rect(self) -> None:
        """
        Builds a background rectangle for the canvas.
        """
        background_color = QColor(200, 220, 240)
        width, height = self.map_size * self.grid_spacing
        pen = QPen(Qt.GlobalColor.transparent)
        rect = self.canvas.addRect(0, 0, width, height, pen, QBrush(background_color))
        rect.setZValue(-1000000)
        self.canvas.addItem(rect)

    def draw_to_cursor(self, event, click_index: int) -> None:
        """
        Draws a line from the cursor's last position to its current position.
        Used to prevent gaps when the user is drawing quickly.
        """
        old_pos = self.communicator.mouse_pos
        pos = self.get_grid_pos(event)

        if pos == old_pos:
            return

        if not pos or not old_pos:
            return

        delta = Vec2f(pos.x - old_pos.x, pos.y - old_pos.y)
        steps = max(abs(delta.x), abs(delta.y))

        if steps <= 1:
            self.place_item(pos, click_index=click_index)

        else:
            for i in range(steps + 1):
                # linear interpolation
                x = round(old_pos.x + i * delta.x / steps)
                y = round(old_pos.y + i * delta.y / steps)
                grid_pos = (x, y)

                self.place_item(grid_pos, click_index=click_index)

        self.update_mouse_pos(event)

    def _get_merged_item(self, placing_item: CItem, grid_pos: Vec2f) -> CItem:
        """
        Checks if a tile should be merged and returns the final CItem to be placed.
        Returns the original item if no merge occurs.
        """
        snapped_pos = Vec2f(*grid_pos)
        tile_at_pos = self.tilemap.get(snapped_pos)

        if not tile_at_pos or not (placing_item.is_mergeable() or tile_at_pos.is_mergeable()):
            return placing_item

        merged_name = placing_item.merge_with(tile_at_pos.name_data.name)
        new_item = self.item_list.get_item_by_name(merged_name)

        if new_item is None:
            merged_name = tile_at_pos.merge_with(placing_item.name_data.name)
            new_item = self.item_list.get_item_by_name(merged_name)

        if new_item:
            if new_item.name_data.name == tile_at_pos.name_data.name:
                return tile_at_pos

            return new_item.copy()

        return placing_item

    def place_item(self, grid_pos: Vec2f, item: CItem = None, click_index: int = 1, add_to_history: bool = True) -> None:
        """
        Handles placing or erasing tiles, merging logic, mirroring and history management.
        Ignores 'item' parameter if 'add_to_history' is True and 'item' is None.
        """
        if self.is_out_of_bounds(grid_pos):
            return

        mirror = self.communicator.settings.get("mirrored over x", False)

        placing_item = item
        if add_to_history and placing_item is None:
            placing_item = self.communicator.get_selected_tile(click_index).copy()

        if placing_item is None:
            placing_item = self.item_list.get_item_by_name('sky').copy()

        snapped_pos = Vec2f(*grid_pos)
        prev_item = self.tilemap.get(snapped_pos)
        final_item = self._get_merged_item(placing_item, grid_pos)

        # redundant placement check
        if prev_item and prev_item.name_data.name == final_item.name_data.name:
            skip_rest = False
            if mirror:
                mirrored_x = self.map_size.x - 1 - snapped_pos.x
                if not self.is_out_of_bounds((mirrored_x, snapped_pos.y)) and mirrored_x != snapped_pos.x:
                    mirrored_tile = self.tilemap.get(Vec2f(mirrored_x, snapped_pos.y))
                    if mirrored_tile is None:
                        skip_rest = True

            if not skip_rest:
                can_rotate = final_item.sprite.properties.is_rotatable
                same_rotation = prev_item.sprite.rotation == final_item.sprite.rotation
                same_team = prev_item.sprite.team == final_item.sprite.team
                if (not can_rotate and same_rotation) and same_team:
                    return

        # skip erasing empty space
        if prev_item is None and final_item.is_eraser():
            return

        if add_to_history:
            command = PlaceTileCommand(self, grid_pos, final_item, prev_item)
            self.history_manager.execute_command(command)
            return

        # place/erase
        placing_item = final_item.copy()
        eraser = placing_item.is_eraser()

        tilemap_x, tilemap_y = grid_pos
        snapped_pos = Vec2f(tilemap_x, tilemap_y)
        scene_pos = Vec2f(tilemap_x * self.grid_spacing, tilemap_y * self.grid_spacing)

        if eraser:
            if snapped_pos not in self.tilemap:
                return

            self.tilemap.pop(snapped_pos, None)

        else:
            if placing_item.sprite.properties.is_rotatable:
                placing_item.sprite.rotation = self.rotation

            self.tilemap[snapped_pos] = placing_item

        self.renderer.render_item(placing_item, scene_pos, snapped_pos, eraser, self.rotation)

        if not mirror:
            return

        mirrored_x = self.map_size.x - 1 - tilemap_x
        if not self.is_out_of_bounds((mirrored_x, tilemap_y)) and mirrored_x != tilemap_x:
            mirrored_snapped_pos = Vec2f(mirrored_x, tilemap_y)
            mirrored_scene_pos = Vec2f(mirrored_x * self.grid_spacing, tilemap_y * self.grid_spacing)
            mirrored_item = placing_item.copy()

            if eraser:
                self.tilemap.pop(mirrored_snapped_pos, None)
            else:
                self.tilemap[mirrored_snapped_pos] = mirrored_item

            self.renderer.render_item(mirrored_item, mirrored_scene_pos, mirrored_snapped_pos, eraser, self.rotation)

    def snap_to_grid(self, pos) -> Vec2f:
        """
        Snaps a given position to the nearest grid point.
        """
        x, y = pos
        return Vec2f(int(x // self.grid_spacing), int(y // self.grid_spacing))

    def get_grid_pos(self, event) -> Vec2f:
        """
        Gets the grid position of the given event.
        """
        pos = self.mapToScene(event.pos())
        return self.snap_to_grid((pos.x(), pos.y()))

    def update_mouse_pos(self, event) -> None:
        """
        Updates the mouse position to the given event.
        """
        self.communicator.old_mouse_pos = self.communicator.mouse_pos
        self.communicator.mouse_pos = self.get_grid_pos(event)

    def resize_canvas(self, size: Vec2f, tilemap: dict[Vec2f, CItem] = None) -> None:
        """
        Creates a new map with the specified size and optional map data.
        """
        self.map_size = size
        if tilemap is None:
            tilemap = {}

        self.tilemap = tilemap
        self.wipe_history()

        self.force_rerender()

        self.add_panning_space()
        print(f"New map created with dimensions: {size.x}x{size.y}")

    def is_out_of_bounds(self, pos: Vec2f) -> bool:
        """
        Check if the given position is out of bounds.
        """
        x, y = pos
        return x < 0 or y < 0 or x >= self.map_size.x or y >= self.map_size.y

    def get_cursor_pos_on_canvas(self) -> QPoint:
        """
        Retrives the cursor position on the canvas.
        """
        return self.mapFromGlobal(QCursor.pos())
