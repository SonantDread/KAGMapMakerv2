from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItemGroup
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QImage, QTransform, QBrush
from PyQt6.QtCore import Qt
from base.KagImage import KagImage
from base.Tile import Tile
from utils.vec import vec
import io
import math
from core.scripts.cursor import Cursor
from base.Tile import Tile
from utils.vec import vec
from base.TileList import TileList

class Canvas(QGraphicsView):
    def __init__(self, size: tuple):
        super().__init__()
        self.canvas = QGraphicsScene()
        self.cursorcomm = Cursor()
        self.setScene(self.canvas)
        self.geometry = vec(300, 300)
        self.size = size # map size

        self.tile_images = KagImage()

        self.zoom_change_factor = 1.1   # todo: make it configurable
        self.zoom_change_factor = 1.1

        self.default_zoom_scale = 3        # default value for grid zoom, practically offsets scale from very small natural size to "comfortable"
        self.zoom_factor = 1               # current zoom, todo
        self.zoom_minmax = [0.1, 5]        # max zoom (count default_zoom_scale as 1), todo

        self.setMouseTracking(True) # allow for constant update of cursor position (call to mouseMoveEvent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QColor(165, 189, 200, 255))  # background color
        self.setMinimumSize(200, 200)  # cannot be smaller than this todo: should depend on minmax zoom, same as maxsize
        self.setMaximumSize(1000, 1000)

        self.holding_lmb = False
        self.holding_rmb = False
        self.holding_scw = False
        self.holding_shift = False

        self.current_cursor_pos = [0, 0] # updates every frame to current cursor position

        self.locked_pos = [0, 0] # x, y position of where user is placing when shift is first held
        self.locked_direction = -1 # True = left / right, False = up / down, None = not locked
        self.last_placed_tile_pos = [0, 0]

        self.blocks = [[None for _ in range(self.size[0])] for _ in range(self.size[1])] # should have the tile class of every placed tile in here
        self.blockimages = {}

        self.grid_spacing = math.floor(self.zoom_factor * self.default_zoom_scale * 8) # 8 being 8x8 pixels in kag
        self.buildTileGrid()
        self.Ctile_list = TileList()

    def isTileEmpty(self, tile: str) -> bool:
        return tile is None or tile == "" or tile == "sky" or tile == "tile_empty" or not self.Ctile_list.getTileByName(tile)

    def buildTileGrid(self) -> None:
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        self.buildGridLines(pen)

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

    def placeTile(self, event, tile_index: int) -> None:
        pos = event.pos()
        pos = self.mapToScene(pos)
        pos = self.snapToGrid((pos.x(), pos.y()))

        placing_tile: str = self.getSelectedBlock()[tile_index].tile_name
        empty_tile: bool = self.isTileEmpty(placing_tile)

        if self.holding_shift: # todo: move this into a function
            locked_x, locked_y = self.snapToGrid((self.locked_pos.x(), self.locked_pos.y()))
            current_x, current_y = pos

            if self.locked_direction is None:
                if abs(current_x - locked_x) > abs(current_y - locked_y):
                    self.locked_direction = True  # Lock horizontal
                else:
                    self.locked_direction = False  # Lock vertical

            if self.locked_direction:
                pos = (current_x, locked_y) # lock Y
            else:
                pos = (locked_x, current_y)  # lock X

        # do nothing if out of bounds
        if self.isOutOfBounds(pos):
            return

        grid_x, grid_y = pos
        scene_x = grid_x * self.grid_spacing
        scene_y = grid_y * self.grid_spacing
        print(f"empty tile: {empty_tile}")

        if empty_tile and self.blocks[grid_x][grid_y] is not None: # eraser
            self.canvas.removeItem(self.blocks[grid_x][grid_y].pixmap_item)
            self.blocks[grid_x][grid_y] = None
            return

        if empty_tile:
            return

        if self.blocks[grid_x][grid_y] is not None:
            # remove existing block from scene
            self.canvas.removeItem(self.blocks[grid_x][grid_y].pixmap_item)
            self.blocks[grid_x][grid_y] = None

        pixmap = self.getTileImage(placing_tile)
        tile = self.makeTile(placing_tile, (grid_x, grid_y))

        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setScale(self.zoom_factor * self.default_zoom_scale)
        pixmap_item.setPos(scene_x, scene_y)
        self.canvas.addItem(pixmap_item)

        tile.pixmap_item = pixmap_item
        self.blocks[grid_x][grid_y] = tile

        self.last_placed_tile_pos = [grid_x, grid_y]

    def getSelectedBlock(self) -> list:
        return self.cursorcomm.getSelectedTiles()

    def makeTile(self, tile_name: str, tile_pos: tuple) -> Tile:
        img = self.getTileImage(tile_name)

        x, y = tile_pos
        tile_pos = vec(x, y)

        return Tile(img, tile_name, tile_pos, 0, True) # last 2 vars are currently dummy vars, change later
    
    def getTileImage(self, tile_name: str) -> QPixmap: # returns the image of given tile name
        img = None

        if(tile_name in self.blockimages): # image exists
            img = self.blockimages[tile_name]

        else: # image doesnt exist
            img = self.loadBlockImage(tile_name)
            self.blockimages[tile_name] = img

        return img if img is not None else None

    def snapToGrid(self, pos) -> tuple:
        x, y = pos
        return (int(x // self.grid_spacing), int(y // self.grid_spacing))
    
    def loadBlockImage(self, blockName: str) -> QPixmap:
        """
            Loads a block's PNG from its name

            Args:
                blockName (str): the name of the block you want to load

            Returns:
                QPixmap: The block's image as a QPixmap
        """

        block = self.tile_images.getTilePNGByName(blockName)
        byte_array = io.BytesIO()
        block.save(byte_array, format='PNG')

        qimage = QImage()
        qimage.loadFromData(byte_array.getvalue())

        return QPixmap.fromImage(qimage)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: # place blocks
            self.holding_lmb = True

            self.placeTile(event, 1)

        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = True

            self.placeTile(event, 0)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.holding_lmb = False

        elif event.button() == Qt.MouseButton.RightButton: # elif to prevent placing two tiles at once
            self.holding_rmb = False

    def mouseMoveEvent(self, event):
        self.current_cursor_pos = event.pos()
        if self.holding_lmb:
            self.placeTile(event, 1)

        elif self.holding_rmb:
            self.placeTile(event, 0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Shift: # locking cursor pos when holding shift
            self.holding_shift = True

            self.locked_pos = self.current_cursor_pos
            self.locked_direction = None

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            self.holding_shift = False

            self.locked_direction = None

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