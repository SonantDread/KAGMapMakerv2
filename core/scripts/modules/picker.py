import sys
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from core.scripts.ui_module import ui_module
from base.TileList import TileList
from core.scripts.cursor import Cursor

class module(ui_module):
    def __init__(self, parent=None):
        super().__init__(self)
        self.setParent(parent)
        self.parent_widget = parent
        self.dragging = False
        self.offset = QPoint()
        self.button_pos = {}

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.handleRightClick(event)

    def setupUi(self):   
        self.gridLayoutWidget = QtWidgets.QWidget(parent=self.parent_widget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 25, 230, 230))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        
        self.tabWidget = QtWidgets.QTabWidget(parent=self.gridLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setGeometry(QtCore.QRect(0, 25, 230, 230))

        self.tiles = QtWidgets.QWidget()
        self.tiles.setObjectName("tiles")
        self.tiles.setGeometry(QtCore.QRect(0, 25, 230, 230))
        self.tabWidget.addTab(self.tiles, "")
        self.setupBlocks(self.tiles)

        self.entities = QtWidgets.QWidget()
        self.entities.setObjectName("entities")
        self.entities.setGeometry(QtCore.QRect(0, 25, 230, 230))
        self.tabWidget.addTab(self.entities, "")

        self.colors = QtWidgets.QWidget()
        self.colors.setObjectName("colors")
        self.colors.setGeometry(QtCore.QRect(0, 25, 230, 230))
        self.tabWidget.addTab(self.colors, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self.parent_widget)

        self.parent_widget.mousePressEvent = self.mousePressEvent
        self.parent_widget.mouseMoveEvent = self.mouseMoveEvent
        self.parent_widget.mouseReleaseEvent = self.mouseReleaseEvent

        # add default selection to brush
        tiles = TileList().vanilla_tiles_collection
        self.cursorcomm = Cursor()
        self.cursorcomm.selectTile(tiles[0], 0)
        self.cursorcomm.selectTile(tiles[1], 1)

    def setupBlocks(self, tab):
        blocks = TileList().vanilla_tiles_collection
        buttons = []
        x, y = 0, 0
        button_width, button_height = 32, 32

        for block in blocks:
            if(block.tile_name == "tile_empty"):
                continue

            button = QPushButton(tab)
            button.setGeometry(x, y, button_width, button_height)

            button.setIcon(QIcon(block.img.scaled(32, 32)))
            button.setIconSize(QSize(button_width, button_height))

            button.clicked.connect(lambda _, block = block: self.setSelectedBlock(block.tile_name, 1))
            self.button_pos[(x, y)] = block.tile_name 

            buttons.append(button)

            x += button_width
            
            if x + button_width > tab.width():
                x = 0
                y += button_height

        self.blocksbuttons = buttons

    def setSelectedBlock(self, block: str, lmb: int):
        self.selectedBlock = block
        self.cursorcomm.selectTile(block, lmb)

    def handleRightClick(self, event):
        x, y = event.pos().x(), event.pos().y() - 50  # Adjusted position
        print(f'x: {x}, y: {y}')

        col = x // 32
        row = y // 32

        key = (col * 32, row * 32)

        if key not in self.button_pos:
            return  # key not found, possibly out of bounds

        block = self.button_pos[key]
        if block is None:
            return

        self.cursorcomm.selectTile(block, 0)


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tiles), _translate("menu", "Tiles"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entities), _translate("menu", "Entities"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.colors), _translate("menu", "Colors"))