from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QStackedWidget, QDockWidget, QCheckBox, QStatusBar, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from Canvas import Canvas
from BlockSelector import BlockSelector
from EscapeMenu import EscapeMenu
import sys

class TransparentOverlay(QWidget):
    def __init__(self, parent=None):
        super(TransparentOverlay, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Make it ignore mouse events

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))  # 128 is the alpha value for transparency

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize the canvas
        self.canvas = Canvas()

        # Set up the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add a 'toggle grid' checkbox to the status bar
        self.toggle_grid_checkbox = QCheckBox("Show Grid")
        self.toggle_grid_checkbox.setChecked(self.canvas.settings.show_grid)
        self.status_bar.addWidget(self.toggle_grid_checkbox)
        self.toggle_grid_checkbox.toggled.connect(self.canvas.settings.toggle_grid)

        # Initialize the block selector
        self.blockSelector = BlockSelector()

        # Wrap blockSelector in a QDockWidget
        self.blockSelectorDock = QDockWidget("Block Selector", self)
        self.blockSelectorDock.setWidget(self.blockSelector)
        self.blockSelectorDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.blockSelectorDock)

        # Create an instance of EscapeMenu
        self.escape_menu = EscapeMenu(self.canvas, self)

        # Set up a stacked widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.canvas)
        self.stacked_widget.addWidget(self.escape_menu)

        # Create and add the transparent overlay
        self.overlay = TransparentOverlay(self)
        self.overlay.hide()

        # Set the central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(self.stacked_widget)
        central_layout.addWidget(self.overlay)  # Add the overlay as a sibling to the stacked widget
        central_layout.setStretch(0, 1)  # Stretch the stacked widget to take most of the space
        central_layout.setStretch(1, 0)  # Shrink the overlay to take less space

        self.setCentralWidget(central_widget)

        # Connect the blockSelector's signal to the canvas's slot
        self.blockSelector.blockSelected.connect(self.canvas.setSelectedBlock)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.toggleEscMenu()

    def toggleEscMenu(self):
        # Toggle between the canvas and escape menu in the QStackedWidget
        index = self.stacked_widget.currentIndex()
        if(index == 0):
            index += 1
        elif(index == 1):
            index -= 1

        self.stacked_widget.setCurrentIndex(index)

        # Show/hide the transparent overlay
        self.overlay.setVisible(index == 1)

        # Toggle the visibility of the BlockSelector dock
        if(not self.blockSelectorDock.isFloating()):
            self.blockSelectorDock.setVisible(index == 0)

        # Make sure the overlay covers the entire window
        if index == 1:
            self.overlay.raise_()  # Raise the overlay to be on top
        else:
            self.overlay.lower()  # Lower the overlay to be behind

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    sys.exit(app.exec_())


# todo: make it overlay blockselector IF its docked
# todo: make it not completely overlap canvas
# todo: make the buttons appear on the left, and have the menu opened to the right, with the button currently opened having a bluish tint