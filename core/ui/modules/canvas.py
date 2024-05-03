from utils.vec import vec
from core.ui.ui_module import ui_module

class Canvas(ui_module):
    def __init__(self):
        super().__init__()
        self.geometry = vec(500,500)                    # module area
        self.zoom_factor = 0                            # zoom
        self.zoom_minmax = [-1.0,2.0]                   # min-max for zoom, 1.0 is 100% of scale
        self.grid_size = vec(50,20)                     # map size
        self.grid = []                                  # map
        
        self.buildGrid()                                # builds empty grid
        self.updateSelf()                               # resets properties according to new grid
        self.resetZoom()                                # zoom, scales grid by geometry diagonal factor (wip, currently works using width factor)
        self.setupUi()                                  # loads into main window

    def updateSelf(self):
        self.camera_pos = self.geometry/2               # center of camera
        self.tile_size = 1.0 * self.zoom_factor         # grid tile scale

    def buildGrid(self):
        dim = self.grid_size
        tile = 0
        for row in range(dim.y):                        # rows
            self.grid.append([])
            for col in range(dim.x):                    # tiles in row (cols)
                slot = Canvas_Tile(vec(col, row))
                self.grid[row].append(slot)

    def resetZoom(self):
        self.setZoom(0)

    def setZoom(self, zoom):
        self.zoom_factor = max(min(zoom, self.zoom_minmax[1]), self.zoom_minmax[0])

    def setupUi(self):
        pass # designer info here

class Canvas_Tile:
    def __init__(self, offset):
        self.offset = offset    # tile offset on grid
        self.children = []      # array of tiles or blobs

"""
        def __init__(self):
        super(Canvas, self).__init__()
        self.setMouseTracking(True)
        self._panning = False
        self._last_pan_point = QPoint()
        # note: you multiply things by 8 to get a kag's block size
        self.canvas_scale = 6
        self.grid_size = 8 * self.canvas_scale
        self.imageProcessor = Image()
        self.selected_block = "tile_ground"
        self.block_selector = BlockSelector()  # Initialize with your blocks and a default selected block

        # Calculate the desired canvas size
        self.width = 200 # TODO: this should be a parameter passed from kagmapmaker.py, specified by the user
        self.height = 112

        # Create the QGraphicsScene
        self.Canvas = QGraphicsScene(self)
        self.setScene(self.Canvas)
        #self.setCentralWidget(self.Canvas)

        # Set the scene rect based on the grid and scale
        self.Canvas.setSceneRect(0, 0, self.scaleToCanvas(self.width), self.scaleToCanvas(self.height))

        # grid settings
        self.grid_color = QColor(255, 255, 255, 255)

        # Set the background color or image
        self.setBackgroundBrush(QColor(165, 189, 200, 255))  # You can customize the color or set an image

        # Set the render hints
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setRenderHint(QPainter.HighQualityAntialiasing, True)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # no scroll bars
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # add a pixmap item for testing
        pixmap = QPixmap(self.selected_block + ".png")
        pixmap_item = QGraphicsPixmapItem(pixmap)
        pixmap_item.setScale(self.canvas_scale)
        self.Canvas.addItem(pixmap_item)

        self.current_item = pixmap_item

        self.settings = CanvasSettings(self)  # Initialize settings

        # Adjust the position of the proxy_widget as needed
        self.Canvas.installEventFilter(self)
        self.block_selector.blockSelected.connect(self.onBlockSelected)
        self.left_mouse_button_down = False
        self.right_mouse_button_down = False
        self.blocks = {}

        self.blockimages = {}
        self.usedblocks = []
"""