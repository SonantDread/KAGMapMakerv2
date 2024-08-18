from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItemGroup, QGraphicsItem
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QTransform, QBrush
from PyQt6.QtCore import Qt
from base.ImageHandler import ImageHandler
from base.CTile import CTile
from utils.vec import vec
import math
from core.scripts.Communicator import Communicator
from utils.vec import vec
from base.CTileList import CTileList
from base.Renderer import Renderer
from base.CBlobList import CBlobList
from base.KagImage import KagImage

import atexit
from datetime import datetime
import os

class Canvas(QGraphicsView):
    def __init__(self, size: tuple):
        super().__init__()
        self.exec_path = os.path.dirname(os.path.realpath(__file__))
        self.Renderer = Renderer()
        self.canvas = QGraphicsScene()
        self.canvas.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex) # disable warnings
        self.Communicator = Communicator()
        self.Communicator.setCanvas(self)
        self.setScene(self.canvas)
        self.geometry = vec(300, 300)
        self.size = size # map size

        self.Images = ImageHandler()

        self.zoom_change_factor = 1.1

        self.default_zoom_scale = 3        # default value for grid zoom, practically offsets scale from very small natural size to "comfortable"
        self.zoom_factor = 1               # current zoom
        self.zoom_minmax = [0.1, 5]        # max zoom (count default_zoom_scale as 1)

        self.setMouseTracking(True) # allow for constant update of cursor position (call to mouseMoveEvent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(165, 189, 200, 255))  # background color
        self.setMinimumSize(200, 200)  # cannot be smaller than this
        self.setMaximumSize(1000, 1000)

        self.holding_lmb = False
        self.holding_rmb = False
        self.holding_scw = False
        self.holding_shift = False

        self.current_cursor_pos = [0, 0] # updates every frame to current cursor position

        self.last_placed_pos = [0, 0]

        # TODO: this should be a dictionary of positions instead of a 2d array
        self.tilemap = [[None for _ in range(self.size[0])] for _ in range(self.size[1])] # should have the tile class of every placed tile in here

        self.grid_spacing = math.floor(self.zoom_factor * self.default_zoom_scale * 8) # 8 being 8x8 pixels in kag
        self.buildTileGrid()
        self.tile_list = CTileList()
        self.blob_list = CBlobList()
        
        # TODO: be able to resize canvas for the 'new' map button

        # SAVE MAP WHEN EXITING MAP MAKER
        atexit.register(self.writeMapToFile, datetime.now())

    def writeMapToFile(self, timestamp: datetime):
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

        KagImage()._save_map(file_path + ".png")
        print(f"Map saved to: {file_path}")
    
    def get_tilemap(self) -> list:
        return self.tilemap
    
    def get_size(self) -> tuple:
        return self.size

    def isPositionEmpty(self, name: str) -> bool:
        if self.tile_list.getTileByName(name):
            return False

        if self.blob_list.doesBlobExist(name):
            return False

        return True

    def buildTileGrid(self) -> None:
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        self.buildGridLines(pen)

        self.toggleGrid()

    def buildGridLines(self, pen: QPen):
        self.grid_group = QGraphicsItemGroup()

        # create background rectangle with different color
        background_color = QColor(200, 220, 240)
        rect = self.canvas.addRect(0, 0, self.size[0] * self.grid_spacing, self.size[1] * self.grid_spacing, QPen(Qt.GlobalColor.transparent), QBrush(background_color))
        self.canvas.addItem(rect)

        # Create vertical grid lines
        for x in range(0, self.size[0] * self.grid_spacing + 1, self.grid_spacing):
            line = self.canvas.addLine(x, 0, x, self.size[0] * self.grid_spacing, pen)
            self.grid_group.addToGroup(line)

        # Create horizontal grid lines
        for y in range(0, self.size[1] * self.grid_spacing + 1, self.grid_spacing):
            line = self.canvas.addLine(0, y, self.size[1] * self.grid_spacing, y, pen)
            self.grid_group.addToGroup(line)

        self.canvas.addItem(self.grid_group)

    def showGridLines(self):
        if self.grid_group:
            self.grid_group.setVisible(True)

    def hideGridLines(self):
        if self.grid_group:
            self.grid_group.setVisible(False)

    def placeItem(self, event, click_index: int) -> None:
        pos = self.mapToScene(event.pos())
        pos = self.snapToGrid((pos.x(), pos.y()))

        placing_tile: str = self.Communicator.getSelectedTile(click_index)
        eraser: bool = self.isPositionEmpty(placing_tile)

        # do nothing if out of bounds
        if self.isOutOfBounds(pos):
            return

        grid_x, grid_y = pos # for the 2d array 'tilemap'
        scene_x = grid_x * self.grid_spacing # for the actual location on the canvas
        scene_y = grid_y * self.grid_spacing

        self.Renderer.handleRender(placing_tile, vec(scene_x, scene_y), vec(grid_x, grid_y), click_index, eraser)

    def force_rerender(self):
        # Clear the canvas
        self.canvas.clear()
        
        # Clear the graphics_items dictionary
        if hasattr(self, 'graphics_items'):
            self.graphics_items.clear()
        
        # Rebuild the grid
        self.buildTileGrid()
        
        # Redraw all items
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                item = self.tilemap[x][y]
                if item is not None:
                    scene_x = x * self.grid_spacing
                    scene_y = y * self.grid_spacing
                    self.Renderer.handleRender(item.name, vec(scene_x, scene_y), vec(x, y), 1, False, item.z)

    def removeExistingItemFromScene(self, pos: tuple) -> None:
        x, y = pos
        if self.tilemap[x][y] is not None:
            if hasattr(self, 'graphics_items') and (x, y) in self.graphics_items:
                self.canvas.removeItem(self.graphics_items[(x, y)])
                del self.graphics_items[(x, y)]
            self.tilemap[x][y] = None

    def addItemToCanvas(self, pixmap: QPixmap, pos: tuple, z: int, name: str):
        x, y = self.snapToGrid(pos)
        
        # Remove existing item if present
        if self.tilemap[x][y] is not None:
            self.removeExistingItemFromScene((x, y))

        if pixmap is None:
            print(f"Warning: Pixmap is None for item {name} at position {pos}")
            return None

        # create new item
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setScale(self.zoom_factor * self.default_zoom_scale)
        width, height = pixmap.width(), pixmap.height()
        pixmap_item.setPos(int(pos[0] - width), int(pos[1] - height))
        pixmap_item.setZValue(z)

        self.canvas.addItem(pixmap_item)

        # update tilemap with CTile storing the QPixmap
        self.tilemap[x][y] = CTile(pixmap, name, vec(x, y), 0, z)  # Assuming layer is 0

        # store the QGraphicsPixmapItem separately
        if not hasattr(self, 'graphics_items'):
            self.graphics_items = {}
        self.graphics_items[(x, y)] = pixmap_item

        return pixmap_item

    def toggleGrid(self):
        if self.grid_group:
            self.grid_group.setVisible(not self.grid_group.isVisible())

    def snapToGrid(self, pos) -> tuple:
        x, y = pos
        return (int(x // self.grid_spacing), int(y // self.grid_spacing))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: # place blocks
            self.holding_lmb = True

            self.placeItem(event, 1)

        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = True

            self.placeItem(event, 0)
            
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self._pan_start_x, self._pan_start_y = event.pos().x(), event.pos().y()
            self._last_pan_point = event.pos()
            self.holding_scw = True
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.holding_lmb = False

        elif event.button() == Qt.MouseButton.RightButton: # elif to prevent placing two tiles at once
            self.holding_rmb = False
            
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.holding_scw = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().unsetCursor()

    def mouseMoveEvent(self, event):
        self.current_cursor_pos = event.pos()
        if self.holding_lmb:
            self.placeItem(event, 1)

        elif self.holding_rmb:
            self.placeItem(event, 0)
            
        if self.holding_scw:
            # Calculate how much the mouse has moved
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()

            # Scroll the view accordingly
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Shift: # locking cursor pos when holding shift
            self.holding_shift = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            self.holding_shift = False

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            zoomInFactor = self.zoom_change_factor
            zoomOutFactor = 1 / zoomInFactor

            # Get the position before scaling, in scene coords
            oldPos = self.mapToScene(self.current_cursor_pos)

            scaleFactor = zoomInFactor if event.angleDelta().y() > 0 else zoomOutFactor
            # Calculate the new scale factor and clamp it
            newScale = self.transform().m11() * scaleFactor
            minScale = self.zoom_minmax[0]  # Minimum zoom level
            maxScale = self.zoom_minmax[1]   # Maximum zoom level

            if minScale <= newScale <= maxScale:
                self.scale(scaleFactor, scaleFactor)

                # Get the position after scaling, in scene coords
                newPos = self.mapToScene(self.current_cursor_pos)

                # Move scene to old position
                delta = newPos - oldPos
                self.translate(delta.x(), delta.y())

            else:
                # Keep the scene fixed if at zoom limits
                if newScale < minScale:
                    self.setTransform(QTransform().scale(minScale, minScale))

                elif newScale > maxScale:
                    self.setTransform(QTransform().scale(maxScale, maxScale))
        else:
            # Determine the current spacing considering the zoom factor
            current_spacing = self.grid_spacing / self.transform().m11()

            if event.angleDelta().y() > 0: # move view down
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(current_spacing))
            else: # move view up
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + int(current_spacing))

            if event.angleDelta().x() > 0: # move view right
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(current_spacing))
            elif event.angleDelta().x() < 0: # move view left
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + int(current_spacing))

        super().wheelEvent(event)

    def isOutOfBounds(self, pos: tuple) -> bool:
        x, y = pos
        return x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]