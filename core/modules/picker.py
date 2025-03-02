"""
Handles the GUI of selecting blocks, blobs and everything else.
"""

from PIL import Image
from PyQt6 import QtCore
from PyQt6.QtCore import QPoint, Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QGridLayout, QPushButton, QScrollArea, QTabWidget, QWidget

from base.citem import CItem
from base.citemlist import CItemList
from core.communicator import Communicator
from utils.vec2f import Vec2f

BUTTON_WIDTH, BUTTON_HEIGHT = 48, 48
communicator = Communicator()

class SelectionButton(QPushButton):
    def __init__(self, data: CItem, parent) -> None:
        super().__init__(parent)
        self.data: CItem = data
        self.setToolTip(str(self.data.name_data.display_name))
        self.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)

        # todo: https://chatgpt.com/c/678aa424-ca4c-800f-972d-c43efdd5b203

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            communicator.select_item(self.data, 1)
        elif event.button() == Qt.MouseButton.RightButton:
            communicator.select_item(self.data, 0)

class Picker(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setParent(parent)
        self.parent_widget = parent
        self.offset = QPoint()

        self.tab_holder = self.vanilla_tab = self.modded_tab = None
        self.setup_ui()

    def setup_ui(self) -> None:
        size = self._get_tab_size()
        # TODO: https://chatgpt.com/c/678ae16c-1bf4-800f-9bfc-53302564e25b
        # holds "Vanilla" and "Modded" tabs
        self.tab_holder = QTabWidget(parent=self.parent_widget)
        self.tab_holder.setFixedSize(QtCore.QSize(size,size))

        # the actual vanilla and modded tabs
        self.vanilla_tab = QTabWidget(parent=self.tab_holder)
        self.vanilla_tab.setFixedSize(QtCore.QSize(size,size))
        self.tab_holder.addTab(self.vanilla_tab, "Vanilla")

        self.modded_tab = QTabWidget(parent=self.tab_holder)
        self.modded_tab.setFixedSize(QtCore.QSize(size,size))
        self.tab_holder.addTab(self.modded_tab, "Modded")

        self.setup_tabs(self.vanilla_tab, True)
        self.setup_tabs(self.modded_tab, False)

    def setup_tabs(self, tab: QTabWidget, is_vanilla: bool) -> None:
        tiles_tab =  self._make_scroll_area("Tiles", tab)
        blobs_tab = self._make_scroll_area("Blobs", tab)
        colors_tab = self._make_scroll_area("Colors", tab)
        others_tab = self._make_scroll_area("Other", tab)

        tab.addTab(tiles_tab,  "Tiles")
        tab.addTab(blobs_tab,  "Blobs")
        tab.addTab(colors_tab, "Colors")
        tab.addTab(others_tab, "Other")

        # tiles and blobs
        itemlist = CItemList()
        if is_vanilla:
            tiles, blobs = itemlist.vanilla_tiles, itemlist.vanilla_blobs
            # others = itemlist.vanilla_others # todo
        else:
            tiles, blobs = itemlist.modded_tiles, itemlist.modded_blobs
            # others = itemlist.modded_others # todo

        self._setup_items(tiles_tab, tiles)
        self._setup_items(blobs_tab, blobs)
        # need a new item list to prevent overwriting the other one
        itemlist = CItemList()
        colors = itemlist.vanilla_tiles + itemlist.vanilla_blobs #+ others # todo
        for item in colors:
            item.sprite.offset = Vec2f(0, 0)
            item.sprite.image = self.__get_color_image(item.get_color())

        self._setup_items(colors_tab, colors)
        # self._setup_items(others_tab, others)

    def _setup_items(self, tab: QScrollArea, items: list[CItem]) -> None:
        x, y = 0, 0
        # basically use a qwidget to hold the grid so we can actually place it in the scroll area
        content_widget = QWidget()
        grid = QGridLayout(content_widget)

        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)

        for item in items:
            if self._bad_item(item):
                continue

            button = SelectionButton(item, content_widget)
            button.setIcon(self._scale_image(item.sprite.image))
            button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))

            grid.addWidget(button, y, x)
            x += 1
            if x >= 5: # max buttons
                x = 0
                y += 1

        content_widget.setLayout(grid)

        tab.setWidget(content_widget)
        tab.setWidgetResizable(True)

    def _make_scroll_area(self, name: str, parent: QTabWidget) -> QScrollArea:
        scroll_area = QScrollArea(parent=parent)
        scroll_area.setObjectName(name)
        scroll_area.setGeometry(QtCore.QRect(0, 0, self._get_tab_size(), self._get_tab_size()))
        scroll_area.setWidgetResizable(False)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        return scroll_area

    def _scale_image(self, image: QPixmap) -> QIcon:
        scaled_pixmap = image.scaled(
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            Qt.AspectRatioMode.KeepAspectRatio
        )
        return QIcon(scaled_pixmap)

    def __get_color_image(self, color: tuple) -> QPixmap:
        return Image.new("RGBA", (8, 8), (color[1], color[2], color[3], color[0])).toqpixmap()

    def _bad_item(self, item: CItem) -> bool:
        name = item.name_data.name
        return name == "" or name is None or name is None

    def _get_tab_size(self) -> None:
        return int(BUTTON_WIDTH * 5 + 40) # button size, button amount and scrollbar width
