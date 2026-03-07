# KAGMapMakerV2 - An unofficial map maker for King Arthur's Gold.
# Copyright (C) 2026 SonantDread
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
Handles the selecting of blocks, blobs, colors and other items.
"""

from PIL import Image
from PyQt6 import QtCore
from PyQt6.QtCore import QPoint, Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QGridLayout, QPushButton, QScrollArea, QTabWidget, QWidget, QLineEdit, QVBoxLayout

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

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            communicator.select_item(self.data, 1)

        elif event.button() == Qt.MouseButton.RightButton:
            communicator.select_item(self.data, 0)

class Picker(QWidget):
    """
    Manages the buttons for picking items on the left sidebar.
    """
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setParent(parent)
        self.parent_widget = parent
        self.offset = QPoint()

        self.tab_holder = self.vanilla_tab = self.modded_tab = None
        self.search_box = None

        self.vanilla_items = {"tiles": [], "blobs": [], "colors": [], "others": []}
        self.modded_items = {"tiles": [], "blobs": [], "colors": [], "others": []}
        self.vanilla_tab_widgets = {}
        self.modded_tab_widgets = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        """
        Sets up the main UI for the picking items menu.
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        size = self._get_tab_size()
        tab_height = size - 48

        self.tab_holder = QTabWidget(parent=self.parent_widget)
        self.tab_holder.setFixedSize(QtCore.QSize(size, tab_height))

        self.vanilla_tab = QTabWidget(parent=self.tab_holder)
        self.vanilla_tab.setFixedSize(QtCore.QSize(size, tab_height))
        self.tab_holder.addTab(self.vanilla_tab, "Vanilla")

        self.modded_tab = QTabWidget(parent=self.tab_holder)
        self.modded_tab.setFixedSize(QtCore.QSize(size, tab_height))
        self.tab_holder.addTab(self.modded_tab, "Modded")

        self._setup_tabs(self.vanilla_tab, True)
        self._setup_tabs(self.modded_tab, False)

        main_layout.addWidget(self.tab_holder)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search items...")
        self.search_box.setFixedWidth(size)
        self.search_box.textChanged.connect(self._on_search_text_changed)
        main_layout.addWidget(self.search_box)

        self.setLayout(main_layout)

    def _setup_tabs(self, tab: QTabWidget, is_vanilla: bool) -> None:
        tiles_tab  = self._make_scroll_area("Tiles", tab)
        blobs_tab  = self._make_scroll_area("Blobs", tab)
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
            others = itemlist.vanilla_others
            items_dict = self.vanilla_items
            tab_widgets = self.vanilla_tab_widgets

        else:
            tiles, blobs = itemlist.modded_tiles, itemlist.modded_blobs
            others = itemlist.modded_others
            items_dict = self.modded_items
            tab_widgets = self.modded_tab_widgets

        tiles = [item for item in tiles if item.is_in_picker_menu()]
        blobs = [blob for blob in blobs if blob.is_in_picker_menu()]
        others = [other for other in others if other.is_in_picker_menu()]

        items_dict["tiles"] = tiles
        items_dict["blobs"] = blobs
        items_dict["others"] = others

        tab_widgets["tiles"] = tiles_tab
        tab_widgets["blobs"] = blobs_tab
        tab_widgets["colors"] = colors_tab
        tab_widgets["others"] = others_tab
        tab_widgets["tab"] = tab

        self._setup_items(tiles_tab, tiles)
        self._setup_items(blobs_tab, blobs)

        all_colors = tiles + blobs + others

        colors = []
        for item in all_colors:
            if not item.is_in_picker_menu():
                continue

            item = item.copy()
            item.sprite.offset = Vec2f(0, 0)
            item.sprite.image = self.__get_color_image(item.get_color())

            colors.append(item)

        items_dict["colors"] = colors
        self._setup_items(colors_tab, colors)
        self._setup_items(others_tab, others)

    def _setup_items(self, tab: QScrollArea, items: list[CItem]) -> None:
        x, y = 0, 0
        max_buttons = 5
        spacing = 5
        # basically use a qwidget to hold the grid so we can actually place it in the scroll area
        content_widget = QWidget()
        grid = QGridLayout(content_widget)

        grid.setSpacing(5)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        for item in items:
            if self._bad_item(item):
                continue

            button = SelectionButton(item, content_widget)
            button.setIcon(self._scale_image(item.sprite.image))
            button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))

            grid.addWidget(button, y, x)
            x += 1
            if x >= max_buttons:
                x = 0
                y += 1

        rows_needed = y + (1 if x > 0 else 0)
        min_height = (rows_needed * (BUTTON_HEIGHT + spacing)) + (BUTTON_HEIGHT // 2)
        content_widget.setMinimumHeight(min_height)

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
        return name == "" or name is None

    def _on_search_text_changed(self, text: str) -> None:
        """
        Handles search text changes and filters items in real-time.
        """
        search_text = text.strip().lower()

        if not search_text:
            # clear search
            current_tab_index = self.tab_holder.currentIndex()
            is_vanilla = current_tab_index == 0

            if is_vanilla:
                self._repopulate_tabs(self.vanilla_items, self.vanilla_tab_widgets)

            else:
                self._repopulate_tabs(self.modded_items, self.modded_tab_widgets)

        else:
            # search
            current_tab_index = self.tab_holder.currentIndex()
            is_vanilla = current_tab_index == 0

            if is_vanilla:
                items_dict = self.vanilla_items
                tab_widgets = self.vanilla_tab_widgets

            else:
                items_dict = self.modded_items
                tab_widgets = self.modded_tab_widgets

            best_match_tab = self._apply_search_filter(search_text, items_dict, tab_widgets)

            if best_match_tab is not None:
                current_subtab = tab_widgets["tab"]
                current_subtab.setCurrentIndex(best_match_tab)

    def _apply_search_filter(self, search_text: str, items_dict: dict, tab_widgets: dict) -> int:
        """
        Filters items based on search text and updates tabs.
        Returns the index of the best matching tab (excluding colors tab).
        """
        search_text = search_text.lower()
        best_match_tab = None

        for tab_name in ["tiles", "blobs", "colors", "others"]:
            if tab_name not in items_dict:
                continue

            original_items = items_dict[tab_name]
            filtered_items = []

            for item in original_items:
                if search_text in item.name_data.display_name.lower():
                    filtered_items.append(item)
                    # exact match
                    if tab_name != "colors" and (best_match_tab is None or item.name_data.display_name.lower().startswith(search_text)):
                        best_match_tab = self._get_tab_index(tab_name)

                    continue

                if search_text in item.name_data.name.lower():
                    filtered_items.append(item)
                    if tab_name != "colors" and best_match_tab is None:
                        best_match_tab = self._get_tab_index(tab_name)

                    continue

                for keyword in item.search_keywords:
                    if search_text in keyword.lower():
                        filtered_items.append(item)
                        if tab_name != "colors" and best_match_tab is None:
                            best_match_tab = self._get_tab_index(tab_name)

                        break

            if tab_name in tab_widgets:
                self._setup_items(tab_widgets[tab_name], filtered_items)

        return best_match_tab

    def _repopulate_tabs(self, items_dict: dict, tab_widgets: dict) -> None:
        """
        Repopulates all tabs with their full item lists (clears search filter).
        """
        for tab_name in ["tiles", "blobs", "colors", "others"]:
            if tab_name in items_dict and tab_name in tab_widgets:
                self._setup_items(tab_widgets[tab_name], items_dict[tab_name])

    def _get_tab_index(self, tab_name: str) -> int:
        """
        Returns the tab index for a given tab name.
        """
        tab_map = {"tiles": 0, "blobs": 1, "colors": 2, "others": 3}
        return tab_map.get(tab_name, 0)

    def _get_tab_size(self) -> int:
        return int(BUTTON_WIDTH * 5 + 48) # button size, button amount and scrollbar width
