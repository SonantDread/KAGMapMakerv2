import sys
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon, QPixmap
from core.ui.ui_module import ui_module
from base.TileList import TileList

class module(ui_module):
    def __init__(self, parent=None):
        super().__init__(self)
        self.parent_widget = parent
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

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

            button.clicked.connect(lambda _, block = block: self.setSelectedBlock(block.tile_name))

            buttons.append(button)

            x += button_width
            
            if x + button_width > tab.width():
                x = 0
                y += button_height

        self.blocksbuttons = buttons

    def setSelectedBlock(self, block):
        self.selectedBlock = block

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tiles), _translate("menu", "Tiles"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entities), _translate("menu", "Entities"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.colors), _translate("menu", "Colors"))