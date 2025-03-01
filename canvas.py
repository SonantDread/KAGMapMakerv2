"""
Used to display images and interact with the map.
"""

import atexit
import math
import os
from datetime import datetime

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QShortcut, QKeySequence, QKeyEvent, QCursor
from PyQt6.QtWidgets import QGraphicsItemGroup, QGraphicsScene, QGraphicsView, QSizePolicy

from base.citem import CItem
from base.citemlist import CItemList
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
        self.holding_space = False
        self.holding_shift = False

        self._last_pan_point = None

        self.tilemap = [[None for _ in range(self.size.y)] for _ in range(self.size.x)]
        self.graphics_items = {}

        self._build_tile_grid()
        self.set_grid_visible(False) # should be a setting but disabled by default

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

    def resizeEvent(self, event) -> None:
        """
        Handles the resize event of the QGraphicsView to adjust the scene accordingly.

        Parameters:
            event: A Qt resize event object containing information about the resize.

        Returns:
            None
        """
        super().resizeEvent(event)

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
        self.canvas.clear()
        self._build_background_rect()

        # clear the graphics_items dictionary
        if hasattr(self, 'graphics_items'):
            self.graphics_items.clear()

        # redraw all items
        for x in range(self.size.x):
            for y in range(self.size.y):
                item = self.tilemap[x][y]
                if item is not None:
                    scene_x = x * self.grid_spacing
                    scene_y = y * self.grid_spacing
                    scene_pos = Vec2f(scene_x, scene_y)
                    rotation = None
                    if isinstance(item, CItem):
                        rotation = item.sprite.rotation

                    self.renderer.render_item(item, scene_pos, Vec2f(x, y), False, rotation)

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
        Requests to add an item at position

        Args:
            event: The event that triggered the item placement.
            click_index: The index of the click that triggered the item placement.

        Returns:
            None
        """
        recent_pos = self.communicator.mouse_pos
        self.communicator.recent_mouse_pos = recent_pos

        pos = self.get_grid_pos(event)
        # place items between frames
        if (len(pos) == 0 or len(recent_pos) == 0):
            return

        delta = (pos[0] - recent_pos[0], pos[1] - recent_pos[1])
        steps = max(abs(delta[0]), abs(delta[1]))

        if steps == 0:
            self.place_item(pos, click_index)
            return

        for i in range(steps + 1):
            x = recent_pos[0] + i * delta[0] / steps
            y = recent_pos[1] + i * delta[1] / steps

            self.place_item((int(x), int(y)), click_index)

        self.update_mouse_pos(event)

    def place_item(self, grid_pos, click_index: int) -> None:
        """
        Places an item on the canvas based on the given event and click index.

        Args:
            grid_pos: The grid position to place the item at.
            click_index: The index of the click that triggered the item placement.

        Returns:
            None
        """

        # calculate the distance of mouse swipe and fill items inbetween
        placing_item: CItem = self.communicator.get_selected_tile(click_index).copy()
        eraser: bool = placing_item.is_eraser()

        # do nothing if out of bounds
        if self.is_out_of_bounds(grid_pos):
            return

        tilemap_x, tilemap_y = grid_pos
        scene_x = tilemap_x * self.grid_spacing # for the location on the canvas
        scene_y = tilemap_y * self.grid_spacing

        scene_pos = Vec2f(scene_x, scene_y)
        snapped_pos = Vec2f(tilemap_x, tilemap_y)

        self.renderer.render_item(placing_item, scene_pos, snapped_pos, eraser, self.rotation)

        if self.communicator.settings.get("mirrored over x", False):
            # calculate mirrored position
            mirrored_x = self.size.x - 1 - tilemap_x
            mirrored_scene_x = mirrored_x * self.grid_spacing

            # only place if mirrored position is valid
            if not self.is_out_of_bounds((mirrored_x, tilemap_y)) and mirrored_x != tilemap_x:
                mirrored_scene_pos = Vec2f(mirrored_scene_x, scene_y)
                mirrored_snapped_pos = Vec2f(mirrored_x, tilemap_y)

                self.renderer.render_item(placing_item, mirrored_scene_pos, mirrored_snapped_pos, eraser, self.rotation)

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

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handles key press events on the canvas.

        Args:
            event: The key event to handle.

        Returns:
            None
        """
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self._last_pan_point = self.get_cursor_pos_on_canvas()
            self.holding_space = True

    def keyReleaseEvent(self, event: QKeyEvent):
        """
        Handles key release events on the canvas.

        Args:
            event: The key event to handle.

        Returns:
            None
        """
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            self.holding_space = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().unsetCursor()

    def mouseDoubleClickEvent(self, event) -> None:
        """
        Handles mouse press events on the canvas.

        Parameters:
            event: A Qt mouse event object containing information about the mouse press.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.holding_lmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos, 1)

        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos, 0)

    def mousePressEvent(self, event) -> None:
        """
        Handles mouse press events on the canvas.

        Parameters:
            event: A Qt mouse event object containing information about the mouse press.

        Returns:
            None
        """

        self.update_mouse_pos(event)

        if event.button() == Qt.MouseButton.LeftButton: # place blocks
            self.holding_lmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos, 1)

        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = True

            grid_pos = self.get_grid_pos(event)
            self.place_item(grid_pos, 0)

        if not self.holding_lmb:
            self.communicator.recent_mouse_pos = self.communicator.mouse_pos

        if event.button() == Qt.MouseButton.MiddleButton:
            self._last_pan_point = event.pos()
            self.holding_scw = True

    def mouseReleaseEvent(self, event) -> None:
        """
        Handles mouse release events on the canvas.

        Parameters:
            event: A Qt mouse event object containing information about the mouse release.

        Returns:
            None
        """

        self.update_mouse_pos(event)

        if event.button() == Qt.MouseButton.LeftButton:
            self.holding_lmb = False

        # elif to prevent placing two tiles at once
        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = False

        elif event.button() == Qt.MouseButton.MiddleButton:
            self.holding_scw = False

    def mouseMoveEvent(self, event) -> None:
        """
        Handles mouse movement events on the canvas.

        Parameters:
            event: A Qt mouse event object containing information about the mouse move.

        Returns:
            None
        """
        if self.holding_lmb:
            self.add_item(event, 1)

        elif self.holding_rmb:
            self.add_item(event, 0)

        if self.holding_scw or self.holding_space:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)

            # calculate how much the mouse has moved
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()

            # scroll view accordingly
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

        else:
            self.setCursor(Qt.CursorShape.ArrowCursor) # todo: should be a function that is called here & in mouseReleaseEvent
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().unsetCursor()
        # render the cursor
        scene_pos = self.mapToScene(event.pos())
        x, y = self.snap_to_grid((scene_pos.x(), scene_pos.y()))
        self.renderer.render_cursor(Vec2f(x * self.grid_spacing, y * self.grid_spacing))

    def update_mouse_pos(self, event) -> None:
        """
        Updates the mouse position to the given event.

        Args:
            event: The event to update the mouse position to.

        Returns:
            None
        """

        self.communicator.mouse_pos = self.get_grid_pos(event)
        self.communicator.recent_mouse_pos = self.communicator.mouse_pos

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
        self.scale(factor, factor) # todo: fix this being weird and making lines
        # todo: when using a trackpad, its extremely hard to zoom in and out properly because it uses it too fast

        new_scene_pos = self.mapToScene(view_pos.toPoint())
        delta = new_scene_pos - scene_pos

        self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - delta.x()))
        self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - delta.y()))

    def resize_canvas(self, size: Vec2f, tilemap: list[list[CItem]] = None) -> None:
        self.size = size
        if tilemap is None:
            tilemap = [[None for _ in range(size.y)] for _ in range(size.x)]
        self.tilemap = tilemap
        self.force_rerender()
        self.add_panning_space()
        print(f"New map created with dimensions: {size.x}x{size.y}")

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
