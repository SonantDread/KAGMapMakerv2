import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem, QMenu, QAction, QMainWindow, QVBoxLayout, QWidget, QGraphicsProxyWidget
from PyQt5.QtGui import QMouseEvent, QPixmap, QPainter, QColor, QPolygonF, QImage, QTransform
from PyQt5.QtCore import Qt, QLineF, QPointF, QEvent, QPoint, QRectF
from PyQt5 import *
from Image import Image
from BlockSelector import BlockSelector
from CanvasSettings import CanvasSettings
import io
from Tile import Tile
# TODO: undo / redo
# TODO: move to using tile.py
class Canvas(QGraphicsView):
    def __init__(self):
        super(Canvas, self).__init__()
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

    def scaleToCanvas(self, num: int, scaled: bool = False) -> int:
        """
            Scales an integer to fit the canvas scaling

            Args:
                num (int): the number you want to scale
                scaled (bool): if the coordinates of the input are scaled

            Returns:
                int: The scaled or unscaled coordinates of input
        """

        if(scaled): # if its scaled, scale it back down
            return int(num / self.canvas_scale / 8)

        return int(num * self.canvas_scale * 8)

    def isOutOfBounds(self, pos: tuple) -> bool:
        """
            Checks whether or not the provided (x, y) position is out of bounds on the canvas

            Args:
                pos (tuple): the (x, y) position you want to check

            Returns:
                bool: True if out of bounds, otherwise False
        """

        x, y = pos

        return x < 0 or y < 0 or x >= self.width * self.canvas_scale * 8 or y >= self.height * self.canvas_scale * 8

    def eventFilter(self, watched, event):
        # Check if the event is a mouse press and if it occurred within the blockSelector bounds
        if event.type() == QEvent.MouseButtonPress:
            if self.blockSelector.geometry().contains(event.pos()):
                # Optionally, handle the event here (e.g., ignore block placement)
                return True  # True indicates the event has been handled

        # For all other conditions, let the event proceed as normal
        return super().eventFilter(watched, event) #super(MainWindow, self).eventFilter(object, event)

    def setSelectedBlock(self, blockName: str) -> None:
        """
            Sets the selected block to the blockName provided

            Args:
                blockName (str): The new name of the selected block
        """

        self.selected_block = blockName

    def onBlockSelected(self, blockName):
        self.selected_block = blockName
        self.blockSelected.emit(self.selected_block)

    def wheelEvent(self, event): # todo: fix issue on 2k monitor where zooming out fully then fullscreening program causes you to see parts of the canvas you cant place on
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            zoomInFactor = 1.05
            zoomOutFactor = 1 / zoomInFactor

            # Get the position before scaling, in scene coords
            oldPos = self.mapToScene(event.pos())

            # Scaling
            scaleFactor = zoomInFactor if event.angleDelta().y() > 0 else zoomOutFactor
            # Calculate the new scale factor and clamp it
            newScale = self.transform().m11() * scaleFactor
            minScale = 0.2  # Minimum zoom level
            maxScale = 10   # Maximum zoom level

            if minScale <= newScale <= maxScale:
                self.scale(scaleFactor, scaleFactor)

                # Get the position after scaling, in scene coords
                newPos = self.mapToScene(event.pos())

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
            super().wheelEvent(event)

    # ? todo: this should draw a background from kag, or at least something nicer than this?
    def drawBackground(self, painter, rect):
        super(Canvas, self).drawBackground(painter, rect)
        # Only draw the grid if the setting is enabled
        if self.settings.show_grid:
            # Adjust grid drawing to fill the entire rect
            lines = []

            start_x = rect.left() - (rect.left() % self.grid_size)
            end_x = rect.right() + (self.grid_size - (rect.right() % self.grid_size))
            start_y = rect.top() - (rect.top() % self.grid_size)
            end_y = rect.bottom() + (self.grid_size - (rect.bottom() % self.grid_size))

            if(start_x < 0):
                start_x = 0

            if(start_y < 0):
                start_y = 0

            if(end_x > self.scaleToCanvas(self.width)):
                end_x = self.scaleToCanvas(self.width)

            if(end_y > self.scaleToCanvas(self.height)):
                end_y = self.scaleToCanvas(self.height)

            for x in range(int(start_x), int(end_x) + 1, self.grid_size):
                lines.append(QLineF(x, start_y, x, end_y))

            for y in range(int(start_y), int(end_y) + 1, self.grid_size):
                lines.append(QLineF(start_x, y, end_x, y))

            painter.setPen(self.grid_color)
            painter.drawLines(lines)

        else:
            painter.fillRect(rect, self.backgroundBrush())

    def snapToGrid(self, value: int) -> int:
        """
            Snaps the inputted value to the nearest grid point

            Args:
                value (int): the value to snap the grid

            Returns:
                int: The snapped to grid value
        """

        return (value // self.grid_size) * self.grid_size

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.left_mouse_button_down = False

        if event.button() == Qt.RightButton:
            self.right_mouse_button_down = False

        if event.button() == Qt.MiddleButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
            self.setDragMode(QGraphicsView.NoDrag)
            self.viewport().unsetCursor()

        else:
            super(Canvas, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        super(Canvas, self).mousePressEvent(event)
        self.block_selector.mousePressEvent(event)

        # Get the mouse position in scene coordinates
        pos = self.mapToScene(event.pos())

        x, y = self.snapToGrid(pos.x()), self.snapToGrid(pos.y())
        x = min(max(x, 0), self.scaleToCanvas(self.width))
        y = min(max(y, 0), self.scaleToCanvas(self.height))

        if event.button() == Qt.LeftButton:
            self.left_mouse_button_down = True
            self.placeOrReplaceBlock((x, y))

        elif event.button() == Qt.RightButton:
            self.right_mouse_button_down = True
            self.deleteBlock((x, y))

        if event.button() == Qt.MiddleButton:
            self.setCursor(Qt.ClosedHandCursor)
            self._pan_start_x, self._pan_start_y = event.x(), event.y()
            self._last_pan_point = event.pos()
            self._panning = True
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.viewport().setCursor(Qt.ClosedHandCursor)

        else:
            super().mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        super(Canvas, self).mouseMoveEvent(event)
        self.block_selector.mouseMoveEvent(event)
        scenePos = self.mapToScene(event.pos())

        if self.current_item:
            # Update the position of the pixmap item as the mouse moves
            pos = self.mapToScene(event.pos())
            snapped_pos = QPointF(self.snapToGrid(pos.x()), self.snapToGrid(pos.y()))
            self.current_item.setPos(snapped_pos.x(), snapped_pos.y())
        x, y = self.snapToGrid(scenePos.x()), self.snapToGrid(scenePos.y())

        if self.left_mouse_button_down:
            self.placeOrReplaceBlock((x, y))

        elif self.right_mouse_button_down:
            self.deleteBlock((x, y))
            
        if self._panning:
            # Calculate how much the mouse has moved
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()

            # Scroll the view accordingly
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        else:
            super().mousePressEvent(event)

    def placeOrReplaceBlock(self, pos):
        """
        Tries to place or replace a block at the provided position

        Args:
            pos (tuple): The (x, y) position to place the block on the canvas
        """

        # do nothing if out of bounds
        if self.isOutOfBounds(pos):
            return

        # Check if a block already exists at (x, y), if so, remove it
        if pos in self.blocks:
            self.Canvas.removeItem(self.blocks[pos].get_tile_image())

        block_pixmap = None

        # dont load an image if its already been loaded
        if(self.selected_block not in self.usedblocks):
            block_pixmap = self.loadBlockImage(self.selected_block)

            self.blockimages.update({self.selected_block: block_pixmap})
            self.usedblocks.append(self.selected_block)

        else:
            block_pixmap = self.blockimages[self.selected_block]

        pixmap_item = QGraphicsPixmapItem(block_pixmap)
        pixmap_item.setScale(self.canvas_scale)
        pixmap_item.setPos(pos[0], pos[1])
        self.Canvas.addItem(pixmap_item)

        tile = Tile(self.imageProcessor, self.selected_block, pixmap_item, pos, self.canvas_scale)

        self.blocks[pos] = tile

    def deleteBlock(self, pos):
        """
            Tries to delete a block at the provided position

            Args:
                pos (tuple): The (x, y) position you want to delete the block from
        """
        # Check if a block exists at (x, y)
        if pos in self.blocks:
            # Get the Tile instance at the specified position
            tile = self.blocks[pos]

            # Remove the Tile's image from the canvas
            self.Canvas.removeItem(tile.get_tile_image())

            # Remove the Tile instance from the blocks dictionary
            del self.blocks[pos]

    def loadBlockImage(self, blockName: str) -> QPixmap:
        """
            Loads a block's PNG from its name

            Args:
                blockName (str): the name of the block you want to load

            Returns:
                QPixmap: The block's image as a QPixmap
        """
        # Assuming block images are stored in a folder named 'blocks' in the same directory as this script
        # Use the Image class to get the block image as a PIL Image object
        blockIndex = self.imageProcessor.getTileIndexByName(blockName)
        blockPILImage = self.imageProcessor.getBlockPNGByIndex(blockIndex)

        # Convert the PIL Image to a format that PyQt can use (QPixmap)
        # First, save the PIL Image to a byte stream
        byte_array = io.BytesIO()
        blockPILImage.save(byte_array, format='PNG')

        # Then, create a QImage from the byte stream
        qimage = QImage()
        qimage.loadFromData(byte_array.getvalue())

        # Finally, convert the QImage to QPixmap and return
        return QPixmap.fromImage(qimage)

    def drawBlock(self, position):
        # Convert the mouse position to scene coordinates
        scene_position = self.mapToScene(position)
        x, y = self.snapToGrid(scene_position.x()), self.snapToGrid(scene_position.y())

        # Ensure the position is within the bounds of the canvas
        x = min(max(x, 0), self.scaleToCanvas(self.width))
        y = min(max(y, 0), self.scaleToCanvas(self.height))

        # Create a pixmap item with the selected block's image at the snapped position
        block_pixmap = self.loadBlockImage(self.selected_block)
        pixmap_item = QGraphicsPixmapItem(block_pixmap)
        pixmap_item.setScale(self.canvas_scale)
        pixmap_item.setPos(x, y)
        self.Canvas.addItem(pixmap_item)

    def keyPressEvent(self, event):
        # Pass key press event to the parent widget
        self.parent().keyPressEvent(event)
        super(Canvas, self).keyPressEvent(event)

        # TODO: make this more smooth when the user presses WASD
        if event.key() == Qt.Key_A:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - 10)
            self.block_selector.move(self.block_selector.pos().x() - 10, self.block_selector.pos().y())

        if event.key() == Qt.Key_D:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + 10)
            self.block_selector.move(self.block_selector.pos().x() + 10, self.block_selector.pos().y())

        if event.key() == Qt.Key_W:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 10)
            self.block_selector.move(self.block_selector.pos().x(), self.block_selector.pos().y() - 10)

        if event.key() == Qt.Key_S:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 10)
            self.block_selector.move(self.block_selector.pos().x(), self.block_selector.pos().y() + 10)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.canvas = Canvas()

        # Set the central widget to the Canvas
        self.setCentralWidget(self.canvas)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Canvas with Block Selector")

def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()