from PyQt6.QtWidgets import QDockWidget
from PyQt6.QtCore import Qt

class MapMakerUI(QDockWidget):
    def __init__(self, MainWindow):
        super().__init__()
        self.setupUi(MainWindow)

    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        tools_blocks_dock = QDockWidget(parent = MainWindow)
        tools_blocks_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        tools_blocks_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.tools_block_dock = tools_blocks_dock

        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.tools_block_dock)