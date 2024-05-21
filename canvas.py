# from utils.vec import vec
# from core.ui.ui_module import ui_module
# from base.TileList import TileList

# class canvas(ui_module):
#     def __init__(self):
#         super().__init__()
#         self.geometry = vec(500,500)                    # module area
#         self.zoom_factor = 0                            # zoom
#         self.zoom_minmax = [-1.0,2.0]                   # min-max for zoom, 1.0 is 100% of scale
#         self.grid_size = vec(50,20)                     # map size
#         self.grid = []                                  # map

#         # tile list goes here
        
#         self.buildGrid()                                # builds empty grid
#         self.updateSelf()                               # resets properties according to new grid
#         self.resetZoom()                                # zoom, scales grid by geometry diagonal factor (wip, currently works using width factor)
#         self.setupUi()                                  # loads into main window

#     def updateSelf(self):
#         self.camera_pos = self.geometry/2               # center of camera
#         self.tile_size = 1.0 * self.zoom_factor         # grid tile scale

#     def buildGrid(self):
#         dim = self.grid_size
#         tile = 0
#         for row in range(dim.y):                        # rows
#             self.grid.append([])
#             for col in range(dim.x):                    # tiles in row (cols)
#                 slot = canvas_tile(vec(col, row))
#                 self.grid[row].append(slot)

#     def resetZoom(self):
#         self.setZoom(0)

#     def setZoom(self, zoom):
#         self.zoom_factor = max(min(zoom, self.zoom_minmax[1]), self.zoom_minmax[0])

# class canvas_tile:
#     def __init__(self, offset):
#         self.offset = offset    # tile offset on grid
#         self.children = []      # array of tiles or blobs

# """
#         def __init__(self):
#         super(canvas, self).__init__()
#         self.setMouseTracking(True)
#         self._panning = False
#         self._last_pan_point = QPoint()
#         # note: you multiply things by 8 to get a kag's block size
#         self.canvas_scale = 6
#         self.grid_size = 8 * self.canvas_scale
#         self.imageProcessor = Image()
#         self.selected_block = "tile_ground"
#         self.block_selector = BlockSelector()  # Initialize with your blocks and a default selected block

#         # Calculate the desired canvas size
#         self.width = 200 # TODO: this should be a parameter passed from kagmapmaker.py, specified by the user
#         self.height = 112

#         # Create the QGraphicsScene
#         self.canvas = QGraphicsScene(self)
#         self.setScene(self.canvas)
#         #self.setCentralWidget(self.canvas)

#         # Set the scene rect based on the grid and scale
#         self.canvas.setSceneRect(0, 0, self.scaleTocanvas(self.width), self.scaleTocanvas(self.height))

#         # grid settings
#         self.grid_color = QColor(255, 255, 255, 255)

#         # Set the background color or image
#         self.setBackgroundBrush(QColor(165, 189, 200, 255))  # You can customize the color or set an image

#         # Set the render hints
#         self.setRenderHint(QPainter.Antialiasing, True)
#         self.setRenderHint(QPainter.SmoothPixmapTransform, True)
#         self.setRenderHint(QPainter.HighQualityAntialiasing, True)

#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # no scroll bars
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

#         # add a pixmap item for testing
#         pixmap = QPixmap(self.selected_block + ".png")
#         pixmap_item = QGraphicsPixmapItem(pixmap)
#         pixmap_item.setScale(self.canvas_scale)
#         self.canvas.addItem(pixmap_item)

#         self.current_item = pixmap_item

#         self.settings = canvasSettings(self)  # Initialize settings

#         # Adjust the position of the proxy_widget as needed
#         self.canvas.installEventFilter(self)
#         self.block_selector.blockSelected.connect(self.onBlockSelected)
#         self.left_mouse_button_down = False
#         self.right_mouse_button_down = False
#         self.blocks = {}

#         self.blockimages = {}
#         self.usedblocks = []
# """

############################
# old canvas above here ^

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QBrush, QImage
from PyQt6.QtCore import Qt, QRectF
from base.KagImage import KagImage
from base.Tile import Tile
from utils.vec import vec
import io, os

class Canvas(QGraphicsView):
    def __init__(self, size: tuple):
        super().__init__()
        self.canvas = QGraphicsScene()
        self.setScene(self.canvas)
        self.geometry = vec(500, 500)
        self.size = size
        self.tile_images = KagImage()

        self.zoom_factor = 1
        self.zoom_minmax = [0.1, 5]

        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setBackgroundBrush(QColor(165, 189, 200, 255))  # background color
        self.setMinimumSize(200, 200)  # cannot be smaller than this
        self.setMaximumSize(1000, 1000)

        self.lmb = False # is key pressed
        self.scw = False # scroll wheel
        self.rmb = False # right mouse button

        self.blocks = [[None for _ in range(self.size[0])] for _ in range(self.size[1])] # should have the tile class of every placed tile in here
        self.usedblocks = []
        self.blockimages = {}

        self.grid_spacing = 50 # spacing for lines
        # ! above variable ideally should be 1

        self.selected_block = "tile_ground"

        self.buildGrid()

    def buildGrid(self):
        # Clear the scene to rebuild the grid
        self.canvas.clear()

        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)

        # Create vertical grid lines
        for x in range(0, self.size[0] * 25 + 1, self.grid_spacing):
            self.canvas.addLine(x, 0, x, self.size[1] * 25, pen)

        # Create horizontal grid lines
        for y in range(0, self.size[1] * 25 + 1, self.grid_spacing):
            self.canvas.addLine(0, y, self.size[0] * 25, y, pen)

    def placeOrReplaceTile(self, pos: tuple) -> None:
        grid_x, grid_y = pos
        scene_x = grid_x * self.grid_spacing
        scene_y = grid_y * self.grid_spacing

        if self.blocks[grid_x][grid_y] is not None:
            # Remove the existing block
            self.canvas.removeItem(self.blocks[grid_x][grid_y])

        pixmap = self.loadBlockImage(self.selected_block)

        # Create pixmap item
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setScale(6 + .25)
        pixmap_item.setPos(scene_x, scene_y)
        self.canvas.addItem(pixmap_item)

        # Track the new block
        self.blocks[grid_x][grid_y] = pixmap_item

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

    #################################
    # all custom functions above here

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lmb = True

            pos = event.pos()

            pos = self.mapToScene(pos)

            self.placeOrReplaceTile(self.snapToGrid((pos.x(), pos.y())))

        elif event.button() == Qt.MouseButton.RightButton:
            self.rmb = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lmb = False

        elif event.button() == Qt.MouseButton.RightButton:
            self.rmb = False

    def mouseMoveEvent(self, event):
        pass # todo