"""
Handles the GUI of selecting blocks, blobs and everything else.
"""
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QPushButton, QScrollArea, QSpacerItem, QGridLayout,
                            QWidget, QTabWidget, QSizePolicy)

from base.cblob_list import CBlobList
from base.ctile_list import CTileList
from core.communicator import Communicator

SCROLLBAR_SIZE_WIDTH = 15
BUTTON_WIDTH, BUTTON_HEIGHT = 40, 40

class SelectionButton(QPushButton):
    """
    Used for the block & blob selection buttons because
    there isn't a good built in right click handler.
    """
    def __init__(self, item_name: str, communicator: Communicator, parent = None):
        super().__init__(parent)
        self.name = item_name
        self.communicator = communicator

    def set_selected_item(self, item_name: str, lmb: int):
        """
        Sets the currently selected item in the application.

        Args:
            item_name (str): The name of the item to select.
            lmb (int): The mouse button that triggered the selection (1 for left, 0 for right).

        Returns:
            None
        """
        self.communicator.select_item(item_name, lmb)

    def mousePressEvent(self, event):
        """
        Handles mouse press events to select an item.

        Parameters:
            event: A QMouseEvent object containing information about the mouse press event.

        Returns:
            None
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_selected_item(self.name, 1)
        elif event.button() == Qt.MouseButton.RightButton:
            self.set_selected_item(self.name, 0)

class Module(QWidget):
    """
    The picker menu for blocks, blobs and whatever else.
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setParent(parent)
        self.parent_widget = parent
        self.offset = QPoint()

        self.communicator = Communicator()

        self.grid_layout_widget = self.grid_layout = self.tab_widget = None
        self.tiles = self.modded = self.entities = None

    def setup_ui(self):
        """
        Sets up the user interface for the module, including the grid layout, tab widget, 
        scroll areas, and other UI elements. It also connects the slots to the signals and 
        sets up the mouse press/release/move events.

        Parameters:
            None

        Returns:
            None
        """
        size = self._get_tab_size(32, 7, SCROLLBAR_SIZE_WIDTH)
        # Create a widget to hold the tab widget
        self.grid_layout_widget = QWidget(parent = self.parent_widget)
        self.grid_layout_widget.setGeometry(QtCore.QRect(0, 25, size, size))
        self.grid_layout_widget.setObjectName("grid_layout_widget")

        # Create a grid layout to contain the tab widget
        self.grid_layout = QGridLayout(self.grid_layout_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setObjectName("gridLayout")

        # Create the tab widget
        self.tab_widget = QTabWidget(parent = self.grid_layout_widget)
        self.tab_widget.setObjectName("tabWidget")
        self.tab_widget.setGeometry(QtCore.QRect(0, 25, size, size))

        # Create the scroll areas for each tab
        self.tiles = QScrollArea()
        self.tiles.setObjectName("tiles")
        self.tiles.setGeometry(QtCore.QRect(0, 25, size, size))
        self.tiles.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.tiles.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tab_widget.addTab(self.tiles, "")
        # Add the blocks to the tiles tab
        self.setup_blocks(self.tiles)

        # TODO: sort the blobs into categories under the Entities tab
        self.entities = QScrollArea()
        self.entities.setObjectName("entities")
        self.entities.setGeometry(QtCore.QRect(0, 25, size, size))
        self.entities.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.entities.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tab_widget.addTab(self.entities, "")
        # Add the blobs to the entities tab
        self.setup_blobs(self.entities)

        # TODO: have tab called "Other" for things that don't fit into Tiles or Blobs
        self.modded = QScrollArea() # TODO: add JSON templates for modded tiles & blobs
        self.modded.setObjectName("modded")
        self.modded.setGeometry(QtCore.QRect(0, 25, size, size))
        self.modded.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.modded.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tab_widget.addTab(self.modded, "")

        # Add the tab widget to the grid layout
        self.grid_layout.addWidget(self.tab_widget, 0, 0, 1, 1)
        # Translate the UI
        self.retranslateUi()
        # Set the current index of the tab widget to 0
        self.tab_widget.setCurrentIndex(0)
        # Connect the slots to the signals
        QtCore.QMetaObject.connectSlotsByName(self.parent_widget)

        # Set the mouse press/release/move events of the parent widget to the
        # module's events
        self.parent_widget.mousePressEvent = self.mousePressEvent
        self.parent_widget.mouseMoveEvent = self.mouseMoveEvent
        self.parent_widget.mouseReleaseEvent = self.mouseReleaseEvent

        # Add default selection to brush
        tiles = CTileList().vanilla_tiles_collection
        self.communicator.select_item(tiles[0], 0)
        self.communicator.select_item(tiles[1], 1)

    def setup_blocks(self, tab: QScrollArea) -> None:
        """
        Sets up the blocks in the given tab by creating a scroll widget and layout, 
        then populating it with buttons representing the blocks in the vanilla tiles collection.
        
        Args:
            tab (QScrollArea): The tab to set up the blocks in.
        
        Returns:
            None
        """
        blocks = CTileList().vanilla_tiles_collection
        x, y = 0, 0

        scroll_widget = QWidget(tab)
        scroll_layout = QGridLayout(scroll_widget)

        scroll_layout.setSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        for block in blocks:
            n = block.name
            if n == "" or n is None or n == "tile_empty" or block.img is None:
                continue

            self._make_button(scroll_layout, x, y, block.name, block.img)

            x += 1
            if x * BUTTON_WIDTH >= tab.width() - 64:
                x = 0
                y += 1

        scroll_widget.setLayout(scroll_layout)
        tab.setWidget(scroll_widget)
        tab.setWidgetResizable(True)

    def setup_blobs(self, tab: QScrollArea) -> None:
        """
        Sets up the blobs in the given tab by creating a scroll widget and layout, 
        then populating it with buttons representing the blobs in the vanilla maploader collection.
        
        Args:
            tab (QScrollArea): The tab to set up the blobs in.
        
        Returns:
            None
        """
        blobs = CBlobList().vanilla_maploader_blobs
        x, y = 0, 0

        scroll_widget = QWidget(tab)
        scroll_layout = QGridLayout(scroll_widget)

        scroll_layout.setSpacing(0)
        scroll_layout.setVerticalSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        for blob in blobs:
            if blob.name == "" or blob.name is None or blob.img is None:
                continue

            self._make_button(scroll_layout, x, y, blob.name, blob.img)

            x += 1
            if x * BUTTON_WIDTH >= tab.width() - 64:
                x = 0
                y += 1

        scroll_widget.setLayout(scroll_layout)
        tab.setWidget(scroll_widget)
        tab.setWidgetResizable(True)

    def _make_button(self, layout: QGridLayout, x: int, y: int, name: str, img: QPixmap) -> None:
        button = SelectionButton(name, self.communicator, layout.parentWidget())
        button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        button.setIcon(self._scale_image(img))
        button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))

        button.setContentsMargins(0, 0, 0, 0)
        button.setMaximumSize(BUTTON_WIDTH, BUTTON_HEIGHT)

        if x != 0 or y != 0: # not in first row, add a spacer to prevent it being weird
            ex = QSizePolicy.Policy.Expanding
            layout.addItem(QSpacerItem(self._get_tab_size(32, 7, SCROLLBAR_SIZE_WIDTH), 2, ex, ex))

        layout.addWidget(button, y, x)

    # TODO: make this work better than it currently does
    def _scale_image(self, img: QPixmap) -> QIcon:
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

    def _get_tab_size(self, button_size: int, amount_of_buttons: int, scrollbar_width: int) -> int:
        return int((button_size * amount_of_buttons) + scrollbar_width)

    def retranslateUi(self):
        """
        Retranslates the UI elements of the current object.
        
        This method is used to update the text of the UI elements to match the current language.
        
        Parameters:
            None
        
        Returns:
            None
        """
        _translate = QtCore.QCoreApplication.translate
        tw = self.tab_widget
        tw.setTabText(tw.indexOf(self.tiles), _translate("menu", "Tiles"))
        tw.setTabText(tw.indexOf(self.entities), _translate("menu", "Entities"))
        tw.setTabText(tw.indexOf(self.modded), _translate("menu", "Modded"))
