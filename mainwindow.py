from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QDockWidget, QAction, QCheckBox, QStatusBar
from PyQt5.QtCore import Qt
from CanvasSettings import CanvasSettings
from Canvas import Canvas  # Import your Canvas class
from BlockSelector import BlockSelector  # Import your BlockSelector class
import sys
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
        #self.toggle_grid_checkbox.stateChanged.connect(self.canvas.settings.toggle_grid)
        self.status_bar.addWidget(self.toggle_grid_checkbox)
        self.toggle_grid_checkbox.toggled.connect(self.canvas.settings.toggle_grid)
        # Initialize the block selector
        self.blockSelector = BlockSelector([], "")

        # Wrap blockSelector in a QDockWidget
        self.blockSelectorDock = QDockWidget("Block Selector", self)
        self.blockSelectorDock.setWidget(self.blockSelector)
        # prevent closing the dock
        # ? todo: maybe closable, but can reopen with f?
        self.blockSelectorDock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        # Add the dock widget to the main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.blockSelectorDock)

        # Set the canvas as the central widget
        self.setCentralWidget(self.canvas)

        # Connect the blockSelector's signal to the canvas's slot
        self.blockSelector.blockSelected.connect(self.canvas.setSelectedBlock)
    def onBlockSelected(self, blockName):
        print(f"Block selected: {blockName}")
        # Here, implement the logic to change the current block in the canvas
        # For example, you might have a method in your canvas to set the current block
        self.canvas.setSelectedBlock(blockName)

# Make sure to adjust your canvas class to include a method like `setSelectedBlock`
# that changes the current block based on the selection from the block selector.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()

    mainWindow.show()
    sys.exit(app.exec_())
