from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QDockWidget
from PyQt5.QtCore import Qt

from Canvas import Canvas  # Import your Canvas class
from BlockSelector import BlockSelector  # Import your BlockSelector class
import sys
class MainWindow(QMainWindow):
    def __init__(self):
        # super(MainWindow, self).__init__()

        # # Initialize the canvas and block selector
        # self.canvas = Canvas()
        # self.blockSelector = BlockSelector([], "")  # Adjust parameters as needed
        # # Dock the block selector to the side of the main window
        # self.addDockWidget(Qt.LeftDockWidgetArea, self.blockSelector)
        # self.setCentralWidget(self.canvas)
        # # Connect the blockSelector's signal to a method that handles block changes
        # #self.blockSelector.blockSelected.connect(self.onBlockSelected)
        # self.blockSelector.blockSelected.connect(self.canvas.setSelectedBlock)

        # # Setup the layout and add widgets
        # self.mainWidget = QWidget()  # Central widget for the QMainWindow
        # self.setCentralWidget(self.mainWidget)
        # layout = QVBoxLayout(self.mainWidget)
        
        # # Assuming you want both the canvas and block selector visible in the main window
        # layout.addWidget(self.canvas)
        # layout.addWidget(self.blockSelector)
        super(MainWindow, self).__init__()

        # Initialize the canvas
        self.canvas = Canvas()

        # Initialize the block selector
        self.blockSelector = BlockSelector([], "")

        # Wrap blockSelector in a QDockWidget
        self.blockSelectorDock = QDockWidget("Block Selector", self)
        self.blockSelectorDock.setWidget(self.blockSelector)

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
