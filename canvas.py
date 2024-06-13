from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItemGroup
from PyQt6.QtGui import QKeyEvent, QPainter, QColor, QPen, QPixmap, QBrush, QImage, QCursor
from PyQt6.QtCore import Qt, QRectF
from base.KagImage import KagImage
from base.Tile import Tile
from utils.vec import vec
import io, os
import math

#todo: blocks are hidden when topleft is not on screen
class Canvas(QGraphicsView):
    def __init__(self, size: tuple):
        super().__init__()
        self.canvas = QGraphicsScene()
        self.setScene(self.canvas)
        self.geometry = vec(300, 300)
        self.size = size # todo: canvas outside size should be differently coloured and not be able to contain tiles
        self.tile_images = KagImage()
        self.tile_size = 8
        self.setMouseTracking(True) # allow for constant update of cursor position (call to mouseMoveEvent)

        self.default_zoom_scale = 3        # default value for grid zoom, practically offsets scale from very small natural size to "comfortable"
        self.zoom_factor = 1               # current zoom, todo
        self.zoom_minmax = [0.1, 5]        # max zoom (count default_zoom_scale as 1), todo

        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setBackgroundBrush(QColor(165, 189, 200, 255))  # background color
        self.setMinimumSize(200, 200)  # cannot be smaller than this todo: should depend on minmax zoom, same as maxsize
        self.setMaximumSize(1000, 1000)

        self.holding_lmb = False # is key pressed todo: swiping
        self.scw = False
        self.holding_rmb = False # right mouse button todo: secondary brush (default selection should be eraser (empty tile))
        self.holding_shift = False
        self.locked_pos = [0, 0] # x, y position of where user is placing when shift is first held

        self.current_cursor_pos = [0, 0] # updates every frame to current cursor position

        self.locked_direction = -1 # True = left / right, False = up / down, None = not locked
        self.last_placed_tile_pos = [0, 0]

        self.blocks = [[None for _ in range(self.size[0])] for _ in range(self.size[1])] # should have the tile class of every placed tile in here
        self.usedblocks = []
        self.blockimages = {}

        self.updateSpacing()
        self.selected_block = "tile_ground"

        self.buildTileGrid()
        self.updateGrid()
        # self.hideGridLines() # disabled by default

    def buildTileGrid(self):
        # Clear the scene to rebuild the grid
        self.canvas.clear()
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        self.buildGridLines(pen)

    def buildGridLines(self, pen):
        self.grid_group = QGraphicsItemGroup()
        
        # Create vertical grid lines
        for x in range(0, self.size[0] * self.grid_spacing, self.grid_spacing):
            line = self.canvas.addLine(x, 0, x, self.size[0] * self.grid_spacing, pen)
            self.grid_group.addToGroup(line)

        # Create horizontal grid lines
        for y in range(0, self.size[1] * self.grid_spacing, self.grid_spacing):
            line = self.canvas.addLine(0, y, self.size[1] * self.grid_spacing, y, pen)
            self.grid_group.addToGroup(line)
        
        self.canvas.addItem(self.grid_group)

    def showGridLines(self):
        if self.grid_group:
            self.grid_group.setVisible(True)

    def hideGridLines(self):
        if self.grid_group:
            self.grid_group.setVisible(False)

    def placeTile(self, event) -> None:
        pos = event.pos()
        pos = self.mapToScene(pos)
        pos = self.snapToGrid((pos.x(), pos.y()))

        if self.holding_shift:
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

        if self.blocks[grid_x][grid_y] is not None:
            # Remove the existing block
            self.canvas.removeItem(self.blocks[grid_x][grid_y])

        pixmap = self.loadBlockImage(self.selected_block)

        # Create pixmap item
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setScale(self.zoom_factor * self.default_zoom_scale)
        pixmap_item.setPos(scene_x, scene_y)
        self.canvas.addItem(pixmap_item)
        
        # Force picture to render even if top-left is outside screen
        rect = pixmap_item.boundingRect()
        rect.adjusted(0, 0, self.grid_spacing, self.grid_spacing)

        # Track the new block
        self.blocks[grid_x][grid_y] = pixmap_item

        self.last_placed_tile_pos = [grid_x, grid_y]


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
        if event.button() == Qt.MouseButton.LeftButton:
            self.holding_lmb = True

            self.placeTile(event)

        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.holding_lmb = False

        elif event.button() == Qt.MouseButton.RightButton:
            self.holding_rmb = False

    def mouseMoveEvent(self, event):
        self.current_cursor_pos = event.pos()
        if self.holding_lmb:
            self.placeTile(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Shift: # locking cursor pos when holding shift
            self.holding_shift = True

            self.locked_pos = self.current_cursor_pos
            self.locked_direction = None

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            self.holding_shift = False

            self.locked_direction = None

    def updateGrid(self):
        self.updateSpacing()
        for x in range(self.size[0]):
            line = self.grid_group.childItems()[x]
            line.setLine(x * self.grid_spacing, 0, x * self.grid_spacing, self.size[1] * self.grid_spacing)
    
        for y in range(self.size[1]):
            line = self.grid_group.childItems()[self.size[0] + y]
            line.setLine(0, y * self.grid_spacing, self.size[0] * self.grid_spacing, y * self.grid_spacing)

    def updateTiles(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                if self.blocks[x][y] is not None:
                    block = self.blocks[x][y]
                    scene_x = x * self.grid_spacing
                    scene_y = y * self.grid_spacing
                    block.setPos(scene_x, scene_y)
                    block.setScale(self.zoom_factor * self.default_zoom_scale)

    def wheelEvent(self, event):
        # todo: make this scroll exactly one tile ( help :( )
        scroll_distance = self.zoom_factor * self.default_zoom_scale / self.tile_size

        # Zoom if CTRL is held todo: update whole canvas to new scale
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                # zoom in
                self.zoom_factor += 0.1
            else:
                # zoom out
                self.zoom_factor -= 0.1
        else: # Scroll
            if event.modifiers() & Qt.KeyboardModifier.AltModifier: # left-right
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + round(-event.angleDelta().y() * scroll_distance))
            else: # up-down
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() + round(-event.angleDelta().y() * scroll_distance))

        self.updateGrid()
        self.updateTiles()
        self.update()

    def updateSpacing(self):
        self.grid_spacing = math.floor(self.zoom_factor * self.default_zoom_scale * self.tile_size)

    def isOutOfBounds(self, pos: tuple) -> bool:
        x, y = pos
        return x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]
