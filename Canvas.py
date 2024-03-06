import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem, QMenu, QAction, QMainWindow, QVBoxLayout, QWidget, QGraphicsProxyWidget
from PyQt5.QtGui import QMouseEvent, QPixmap, QPainter, QColor, QPolygonF, QImage, QTransform
from PyQt5.QtCore import Qt, QLineF, QPointF, QEvent, QPoint, QRectF
from PyQt5 import *
import Image
from BlockSelector import BlockSelector
from CanvasSettings import CanvasSettings
import io
# TODO: undo / redo
class Canvas(QGraphicsView):
    def __init__(self):
        super(Canvas, self).__init__()
        self._panning = False
        self._last_pan_point = QPoint()
        # note: you multiply things by 8 to get a kag's block size
        self.canvas_scale = 6
        self.grid_size = 8 * self.canvas_scale
        self.imageProcessor = Image.Image()
        self.selected_block = "tile_ground"
        self.block_selector = BlockSelector([], "")  # Initialize with your blocks and a default selected block

        # Calculate the desired canvas size
        self.width = 200 # TODO: this should be a parameter passed from kagmapmaker.py, specified by the user
        self.height = 200

        # Create the QGraphicsScene
        self.Canvas = QGraphicsScene(self)
        self.setScene(self.Canvas)
        #self.setCentralWidget(self.Canvas)

        # Set the scene rect based on the grid and scale
        self.Canvas.setSceneRect(0, 0, self.width * self.canvas_scale * 8, self.height * self.canvas_scale * 8)

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

    def eventFilter(self, watched, event):
        # Check if the event is a mouse press and if it occurred within the blockSelector bounds
        if event.type() == QEvent.MouseButtonPress:
            if self.blockSelector.geometry().contains(event.pos()):
                # Optionally, handle the event here (e.g., ignore block placement)
                return True  # True indicates the event has been handled
            
        # For all other conditions, let the event proceed as normal
        return super().eventFilter(watched, event) #super(MainWindow, self).eventFilter(object, event)
    
    def setSelectedBlock(self, blockName):
        self.selected_block = blockName

    def onBlockSelected(self, blockName):
        print(f"Block selected in main window: {blockName}")
        self.selected_block = blockName
        #self.selected_block = item.text()
        print("Selected Block:", self.selected_block)  # For debugging
        self.blockSelected.emit(self.selected_block)

    def wheelEvent(self, event):
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

            for x in range(int(start_x), int(end_x) + 1, self.grid_size):
                lines.append(QLineF(x, start_y, x, end_y))
            for y in range(int(start_y), int(end_y) + 1, self.grid_size):
                lines.append(QLineF(start_x, y, end_x, y))

            painter.setPen(self.grid_color)
            painter.drawLines(lines)
        else:
            painter.fillRect(rect, self.backgroundBrush())


    def snapToGrid(self, value):
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

    def blockUpdates(self):
        self.blockSignals(True)

    def unblockUpdates(self):
        self.blockSignals(False)

    def mousePressEvent(self, event):
        super(Canvas, self).mousePressEvent(event)
        self.block_selector.mousePressEvent(event)

        # Get the mouse position in scene coordinates
        pos = self.mapToScene(event.pos())

        x, y = self.snapToGrid(pos.x()), self.snapToGrid(pos.y())
        x = min(max(x, 0), self.width * self.canvas_scale * 8)
        y = min(max(y, 0), self.height * self.canvas_scale * 8)
        
        # todo: make this more smooth
        if event.button() == Qt.LeftButton:
            self.left_mouse_button_down = True
            self.placeOrReplaceBlock(x, y)
        elif event.button() == Qt.RightButton:
            self.right_mouse_button_down = True
            self.deleteBlock(x, y)
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
            self.placeOrReplaceBlock(x, y)
        elif self.right_mouse_button_down:
            self.deleteBlock(x, y)
        if self._panning:
            # Calculate how much the mouse has moved
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()
            
            # Scroll the view accordingly
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        else:
            super().mousePressEvent(event)

    def placeOrReplaceBlock(self, x, y):
        # Check if a block already exists at (x, y), if so, remove it
        if (x, y) in self.blocks:
            self.Canvas.removeItem(self.blocks[(x, y)][0])
        # Place a new block
        block_pixmap = self.loadBlockImage(self.selected_block)
        pixmap_item = QGraphicsPixmapItem(block_pixmap)
        pixmap_item.setScale(self.canvas_scale)
        pixmap_item.setPos(x, y)
        self.Canvas.addItem(pixmap_item)
        self.blocks[(x, y)] = (pixmap_item, self.selected_block)

    def deleteBlock(self, x, y):
        # Delete a block at (x, y) if it exists
        if (x, y) in self.blocks:
            self.Canvas.removeItem(self.blocks[(x, y)][0])
            print(self.blocks[(x,y)])
            del self.blocks[(x, y)]

    def loadBlockImage(self, blockName):
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
        x = min(max(x, 0), self.width * self.canvas_scale * 8)
        y = min(max(y, 0), self.height * self.canvas_scale * 8)

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

    # def toggleBlockSelector(self):
    #     # Toggle the visibility of the block selector
    #     block_selector_visible = not self.block_selector.isVisible()
    #     self.block_selector.setVisible(block_selector_visible)

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