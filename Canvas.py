import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsItem, QMenu, QAction, QMainWindow, QVBoxLayout, QWidget, QGraphicsProxyWidget
from PyQt5.QtGui import QMouseEvent, QPixmap, QPainter, QColor, QPolygonF
from PyQt5.QtCore import Qt, QLineF, QPointF
from PyQt5 import *
import Image
from BlockSelector import BlockSelector

class Canvas(QGraphicsView):
    def __init__(self):
        super(Canvas, self).__init__()

        # note: you multiply things by 8 to get a kag's block size
        self.canvas_scale = 6
        self.grid_size = 8 * self.canvas_scale

        self.selected_block = "dirt"
        self.block_selector = BlockSelector([], "")  # Initialize with your blocks and a default selected block

        # Calculate the desired canvas size
        self.width = 20
        self.height = 20

        # Create the QGraphicsScene
        self.Canvas = QGraphicsScene(self)
        self.setScene(self.Canvas)

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

        proxy_widget = QGraphicsProxyWidget()
        proxy_widget.setWidget(self.block_selector)

        # Add the proxy_widget to the scene
        self.Canvas.addItem(proxy_widget)

        # Adjust the position of the proxy_widget as needed
        proxy_widget.setPos(0, 0)

    def loadImage(image):
        return QGraphicsPixmapItem(QPixmap(image))
    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor

            # Set Anchors
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

            # Scale the view / do the zoom
            if event.angleDelta().y() > 0:
                scaleFactor = zoomInFactor
            else:
                scaleFactor = zoomOutFactor

            # Limit zoom range
            currentScale = self.transform().m11()  # m11() element of the transformation matrix represents the horizontal scaling
            if (currentScale < 0.2 and scaleFactor < 1) or (currentScale > 10 and scaleFactor > 1):
                return  # Prevent zooming out too much or zooming in too much

            self.scale(scaleFactor, scaleFactor)

    def drawBackground(self, painter, rect):
        # TODO: render an image throughout the background
        super(Canvas, self).drawBackground(painter, rect)

        # draw grid
        left = 0
        right = self.width * self.canvas_scale * 8
        top = 0
        bottom = self.height * self.canvas_scale * 8

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        lines = []

        for x in range(first_left, right + 1, self.grid_size):
            lines.append(QPointF(x, top))
            lines.append(QPointF(x, bottom))

        for y in range(first_top, bottom + 1, self.grid_size):
            lines.append(QPointF(left, y))
            lines.append(QPointF(right, y))

        painter.setPen(self.grid_color)
        painter.drawLines(QPolygonF(lines))

    def snapToGrid(self, value):
        return (value // self.grid_size) * self.grid_size
    
    def mouseReleaseEvent(self, event):
        pass # todo: implement this to enable drawing with current block as you move the mouse

    def mousePressEvent(self, event):
        super(Canvas, self).mousePressEvent(event)
        self.block_selector.mousePressEvent(event)

        # todo: check if this is lmb / rmb = eraser
        # Get the mouse position in scene coordinates
        pos = self.mapToScene(event.pos())

        x, y = self.snapToGrid(pos.x()), self.snapToGrid(pos.y())
        if(x > (self.width * self.canvas_scale) * 8):
            x = (self.width * self.canvas_scale) * 8
        
        if(y > (self.height * self.canvas_scale) * 8):
            y = (self.height * self.canvas_scale) * 8

        if(x < 0):
            x = 0
        
        if(y < 0):
            y = 0

        snapped_pos = QPointF(x, y)

        # Create a pixmap item at the snapped mouse position
        pixmap_item = QGraphicsPixmapItem(QPixmap(self.selected_block + ".png"))
        pixmap_item.setScale(self.canvas_scale)
        pixmap_item.setPos(snapped_pos.x(), snapped_pos.y())
        self.Canvas.addItem(pixmap_item)

        # store as var to allow rendering (see mouseMoveEvent function)
        self.current_item = pixmap_item

    def mouseMoveEvent(self, event):
        super(Canvas, self).mouseMoveEvent(event)
        self.block_selector.mouseMoveEvent(event)

        if self.current_item:
            # Update the position of the pixmap item as the mouse moves
            pos = self.mapToScene(event.pos())
            snapped_pos = QPointF(self.snapToGrid(pos.x()), self.snapToGrid(pos.y()))
            self.current_item.setPos(snapped_pos.x(), snapped_pos.y())

    def keyPressEvent(self, event):
        # Handle key press events here
        if event.key() == Qt.Key_Escape:
            pass # todo: gui menu for settings etc

        if event.key() == Qt.Key_F:
            self.toggleBlockSelector()

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

    def toggleBlockSelector(self):
        # Toggle the visibility of the block selector
        block_selector_visible = not self.block_selector.isVisible()
        self.block_selector.setVisible(block_selector_visible)

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