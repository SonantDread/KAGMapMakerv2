# handles the GUI of picking items
import sys
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QPushButton, QScrollArea, QSpacerItem
from PyQt6.QtGui import QIcon, QPixmap
from core.scripts.ui_module import ui_module
from base.CTileList import CTileList
from base.CBlobList import CBlobList
from core.scripts.Communicator import Communicator

SCROLLBAR_SIZE_WIDTH = 15
BUTTON_WIDTH, BUTTON_HEIGHT = 40, 40

class SelectionButton(QPushButton):
    def __init__(self, item_name: str, communicator: Communicator, parent = None):
        super().__init__(parent)
        self.name = item_name
        self.communicator = communicator

    def setSelectedItem(self, item_name: str, lmb: int):
        self.communicator.selectItem(item_name, lmb)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setSelectedItem(self.name, 1)
        elif event.button() == Qt.MouseButton.RightButton:
            self.setSelectedItem(self.name, 0)

class module(ui_module):
    def __init__(self, parent = None):
        super().__init__(self)
        self.setParent(parent)
        self.parent_widget = parent
        self.dragging = False
        self.offset = QPoint()

        self.communicator = Communicator()

    def setupUi(self):
        SIZE = self._getTabSize(32, 7, SCROLLBAR_SIZE_WIDTH)
        # Create a widget to hold the tab widget
        self.gridLayoutWidget = QtWidgets.QWidget(parent = self.parent_widget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 25, SIZE, SIZE))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")

        # Create a grid layout to contain the tab widget
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        # Create the tab widget
        self.tabWidget = QtWidgets.QTabWidget(parent = self.gridLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setGeometry(QtCore.QRect(0, 25, SIZE, SIZE))

        # Create the scroll areas for each tab
        self.tiles = QtWidgets.QScrollArea()
        self.tiles.setObjectName("tiles")
        self.tiles.setGeometry(QtCore.QRect(0, 25, SIZE, SIZE))
        self.tiles.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tiles.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabWidget.addTab(self.tiles, "")
        # Add the blocks to the tiles tab
        self.setupBlocks(self.tiles)

        self.entities = QtWidgets.QScrollArea() # TODO: sort the blobs into categories under the Entities tab
        self.entities.setObjectName("entities")
        self.entities.setGeometry(QtCore.QRect(0, 25, SIZE, SIZE))
        self.entities.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.entities.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabWidget.addTab(self.entities, "")
        # Add the blobs to the entities tab
        self.setupBlobs(self.entities)

        # TODO: have tab called "Other" for things that don't fit into Tiles or Blobs
        self.modded = QtWidgets.QScrollArea() # TODO: add JSON templates for modded tiles & blobs
        self.modded.setObjectName("modded")
        self.modded.setGeometry(QtCore.QRect(0, 25, SIZE, SIZE))
        self.modded.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.modded.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabWidget.addTab(self.modded, "")

        # Add the tab widget to the grid layout
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        # Translate the UI
        self.retranslateUi()
        # Set the current index of the tab widget to 0
        self.tabWidget.setCurrentIndex(0)
        # Connect the slots to the signals
        QtCore.QMetaObject.connectSlotsByName(self.parent_widget)

        # Set the mouse press/release/move events of the parent widget to the
        # module's events
        self.parent_widget.mousePressEvent = self.mousePressEvent
        self.parent_widget.mouseMoveEvent = self.mouseMoveEvent
        self.parent_widget.mouseReleaseEvent = self.mouseReleaseEvent

        # Add default selection to brush
        tiles = CTileList().vanilla_tiles_collection
        self.communicator.selectItem(tiles[0], 0)
        self.communicator.selectItem(tiles[1], 1)

    def setupBlocks(self, tab: QScrollArea) -> None:
        blocks = CTileList().vanilla_tiles_collection
        x, y = 0, 0

        scroll_widget = QtWidgets.QWidget(tab)
        scroll_layout = QtWidgets.QGridLayout(scroll_widget)

        scroll_layout.setSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        for block in blocks:
            if block.name == "" or block.name is None or block.img is None or block.name == "tile_empty":
                continue

            self._makeButton(scroll_layout, x, y, block.name, block.img)

            x += 1
            if x * BUTTON_WIDTH >= tab.width() - 64:
                x = 0
                y += 1

        scroll_widget.setLayout(scroll_layout)
        tab.setWidget(scroll_widget)
        tab.setWidgetResizable(True)

    def setupBlobs(self, tab: QScrollArea) -> None:
        blobs = CBlobList().vanilla_maploader_blobs
        x, y = 0, 0

        scroll_widget = QtWidgets.QWidget(tab)
        scroll_layout = QtWidgets.QGridLayout(scroll_widget)

        scroll_layout.setSpacing(0)
        scroll_layout.setVerticalSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        for blob in blobs:
            if blob.name == "" or blob.name is None or blob.img is None:
                continue

            self._makeButton(scroll_layout, x, y, blob.name, blob.img)

            x += 1
            if x * BUTTON_WIDTH >= tab.width() - 64:
                x = 0
                y += 1

        scroll_widget.setLayout(scroll_layout)
        tab.setWidget(scroll_widget)
        tab.setWidgetResizable(True)

    def _makeButton(self, layout: QtWidgets.QGridLayout, x: int, y: int, name: str, img: QPixmap) -> None:
        button = SelectionButton(name, self.communicator, layout.parentWidget())
        button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        button.setIcon(self._scaleImage(img))
        button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))

        button.setContentsMargins(0, 0, 0, 0)
        button.setMaximumSize(BUTTON_WIDTH, BUTTON_HEIGHT)

        if x != 0 or y != 0: # not in first row, add a spacer to prevent it being weird
            layout.addItem(QSpacerItem(self._getTabSize(32, 7, SCROLLBAR_SIZE_WIDTH), 2, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

        layout.addWidget(button, y, x)

    def _scaleImage(self, img: QPixmap) -> QIcon: # TODO: make this work better than it currently does
        """
        Scales the given QPixmap to a specified target size while maintaining its aspect ratio,
        and returns the scaled image as a QIcon.

        Args:
            img (QPixmap): The QPixmap to be scaled.

        Returns:
            QIcon: The scaled QPixmap as a QIcon.
        """
        target_size = QSize(64, 64)

        scaled_img = img.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)

        final_pixmap = QPixmap(target_size)
        final_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(final_pixmap)
        x_offset = (target_size.width() - scaled_img.width()) // 2
        y_offset = (target_size.height() - scaled_img.height()) // 2

        painter.drawPixmap(x_offset, y_offset, scaled_img)
        painter.end()

        return QIcon(final_pixmap)

    def _getTabSize(self, button_size: int, amount_of_buttons: int, scrollbar_width: int) -> int:
        return int((button_size * amount_of_buttons) + scrollbar_width)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tiles), _translate("menu", "Tiles"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.entities), _translate("menu", "Entities"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.modded), _translate("menu", "Modded"))