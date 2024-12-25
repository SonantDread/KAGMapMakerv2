"""
Handles the GUI of selecting blocks, blobs and everything else.
"""
import os

from PIL import Image
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QGridLayout, QPushButton, QScrollArea,
                            QSizePolicy, QSpacerItem, QTabWidget, QWidget)

from base.cblob_list import CBlobList
from base.ctile_list import CTileList
from base.custom_items import CustomItem
from base.kag_color import KagColor
from core.communicator import Communicator
from utils.file_handler import FileHandler
from utils.vec2f import Vec2f

SCROLLBAR_SIZE_WIDTH = 15
BUTTON_WIDTH, BUTTON_HEIGHT = 40, 40

class SelectionButton(QPushButton):
    """
    Used for the block & blob selection buttons because
    there isn't a good built in right click handler.
    """
    def __init__(self, item_name: str, display_name: str, section_name: str, image: QPixmap,
                z_index: int = None, rotatable: bool = False, team_swappable: bool = False,
                team: int = 0, offset: Vec2f = None, search_keywords: list = None,
                communicator: Communicator = None, parent = None):
        super().__init__(parent)
        # names
        self.name = item_name
        self.display_name = display_name
        self.section_name = section_name
        # sprite
        self.image = image
        self.z_index = z_index
        self.rotatable = rotatable
        self.team_swappable = team_swappable
        self.team = team
        self.offset = offset
        #* searchable keywords (for future)
        self.search_keywords = search_keywords

        self.communicator = communicator
        self.display_name = str(self.display_name)
        self.setToolTip(self.display_name.strip())

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
        self.tiles = self.modded = self.entities = self.colors = None

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

        # create the tab widget
        self.tab_widget = QTabWidget(parent = self.grid_layout_widget)
        self.tab_widget.setObjectName("tabWidget")
        self.tab_widget.setGeometry(QtCore.QRect(0, 25, size, size))

        # create the tabs
        self.tiles = self._make_tab("tiles", size, self.tab_widget)
        self.setup_blocks(self.tiles)

        # TODO: sort the blobs into categories under the Entities tab
        self.entities = self._make_tab("entities", size, self.tab_widget)
        self.setup_blobs(self.entities)

        self.colors = self._make_tab("colors", size, self.tab_widget)
        self.setup_colors(self.colors)

        # TODO: have tab called "Other" for things that don't fit into Tiles or Blobs
        self.modded = self._make_tab("modded", size, self.tab_widget)
        self.setup_modded_items(self.modded)

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

    def _make_tab(self, name: str, size: int, tab_widget) -> QScrollArea:
        new_tab = QScrollArea()
        new_tab.setObjectName(name)
        new_tab.setGeometry(QtCore.QRect(0, 25, size, size))
        new_tab.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        new_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tab_widget.addTab(new_tab, "")
        return new_tab

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

    def setup_colors(self, tab: QScrollArea) -> None:
        """
        Sets up the colors in the given tab by creating a scroll widget and layout,
        then populating it with buttons representing the colors in the vanilla colors collection.

        Args:
            tab (QScrollArea): The tab to set up the blobs in.

        Returns:
            None
        """
        colors = KagColor().vanilla_colors
        x, y = 0, 0

        scroll_widget = QWidget(tab)
        scroll_layout = QGridLayout(scroll_widget)

        scroll_layout.setSpacing(0)
        scroll_layout.setVerticalSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        tiles, blobs = CTileList(), CBlobList()

        for item in colors:
            name = item.name
            color = item.color
            if name is None or name == "":
                continue

            # invalid item
            if not tiles.get_tile_by_name(name) and not blobs.does_blob_exist(name):
                continue

            self._make_button(scroll_layout, x, y, name, self.__get_color_image(color))

            x += 1
            if x * BUTTON_WIDTH >= tab.width() - 64:
                x = 0
                y += 1

        scroll_widget.setLayout(scroll_layout)
        tab.setWidget(scroll_widget)
        tab.setWidgetResizable(True)

    def setup_modded_items(self, tab: QScrollArea) -> None:
        # todo: section_name is WIP (should split items into horizontal sections for easier finding)
        # todo: each mod should be split into a section
        # todo: searchbar should allow searching by loaded mods

        modded_path = FileHandler().modded_items_path

        files = []
        # put json files into files list with full path
        for root, _, fn in os.walk(modded_path):
            files.extend([os.path.join(root, f.strip()) for f in fn if f.strip().endswith(".json")
                        and root.split("\\")[-1] != "_ExampleMod"])

        # make tabs with relative data
        scroll_widget = QWidget(tab)
        scroll_layout = QGridLayout(scroll_widget)

        scroll_layout.setSpacing(0)
        scroll_layout.setVerticalSpacing(0)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        x, y = 0, 0

        for file in files:
            button: SelectionButton = self._get_modded_button(file)
            self._make_modded_button(button, scroll_layout, x, y)

            x += 1
            if x * BUTTON_WIDTH >= tab.width() - 64:
                x = 0
                y += 1

        scroll_widget.setLayout(scroll_layout)
        tab.setWidget(scroll_widget)
        tab.setWidgetResizable(True)

    def _get_modded_button(self, file: str) -> SelectionButton:
        data = CustomItem(file)

        return SelectionButton(*data.get_data(), self.communicator, None)

    def __get_color_image(self, color: tuple) -> QPixmap:
        return Image.new("RGBA", (1, 1), (color[1], color[2], color[3], color[0])).toqpixmap()

    def _make_button(self, layout: QGridLayout, x: int, y: int, name: str, img: QPixmap) -> None:
        # todo: vanilla items should have their own config file for easier handling
        button = SelectionButton(name, name.replace("_", " "), "", img, communicator = self.communicator, parent = layout.parentWidget())
        button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        button.setIcon(self._scale_image(img))
        button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))

        button.setContentsMargins(0, 0, 0, 0)
        button.setMaximumSize(BUTTON_WIDTH, BUTTON_HEIGHT)

        if x != 0 or y != 0: # item not in first row, add a spacer to prevent it being weird
            ex = QSizePolicy.Policy.Expanding
            layout.addItem(QSpacerItem(self._get_tab_size(32, 7, SCROLLBAR_SIZE_WIDTH), 2, ex, ex))

        layout.addWidget(button, y, x)

    def _make_modded_button(self, button: SelectionButton, layout: QGridLayout,
                            x: int, y: int) -> None:

        button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        button.setIcon(self._scale_image(button.image))
        button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))

        button.setContentsMargins(0, 0, 0, 0)
        button.setMaximumSize(BUTTON_WIDTH, BUTTON_HEIGHT)

        if x != 0 or y != 0: # item not in first row, add a spacer to prevent it being weird
            ex = QSizePolicy.Policy.Expanding
            layout.addItem(QSpacerItem(self._get_tab_size(32, 7, SCROLLBAR_SIZE_WIDTH), 2, ex, ex))

        layout.addWidget(button, y, x)

    # it is what it is
    def _scale_image(self, img) -> QIcon:
        """
        Scales the given image to a specified target size while maintaining its aspect ratio,
        and returns the scaled image as a QIcon.

        Args:
            img: The image to be scaled (can be QPixmap, PIL Image, or path string)

        Returns:
            QIcon: The scaled image as a QIcon.
        """
        target_size = QSize(32, 32)

        # convert input to QPixmap if needed
        if isinstance(img, str):
            # if img is a file path
            pixmap = QPixmap(img)
        elif isinstance(img, Image.Image):
            # if img is a PIL Image
            pixmap = QPixmap.fromImage(img.toqimage())
        elif isinstance(img, QPixmap):
            # if img is already a QPixmap
            pixmap = img
        else:
            print(f"Unsupported image type: {type(img)}")
            # return an empty icon if conversion fails
            return QIcon()

        # check if the pixmap is valid
        if pixmap.isNull():
            print("Failed to create valid pixmap")
            return QIcon()

        scaled_img = pixmap.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)

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
        tw.setTabText(tw.indexOf(self.colors), _translate("menu", "Colors"))
        tw.setTabText(tw.indexOf(self.modded), _translate("menu", "Modded"))
