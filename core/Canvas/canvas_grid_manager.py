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
Manages the grid setting for the canvas.
"""
from PyQt6.QtWidgets import QGraphicsItemGroup
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt

class GridManager:
    """
    Sets up and handles the visibility of the grid.
    """
    def __init__(self, canvas) -> None:
        self.canvas = canvas

        self.grid_group = QGraphicsItemGroup()
        self.canvas.canvas.addItem(self.grid_group)

        is_visible = self.canvas.communicator.settings.get("tile grid visible", False)
        self.grid_group.setVisible(is_visible)

    def build_grid(self) -> None:
        """
        Builds or rebuilds the tile grid on the canvas by creating grid lines.
        Clears any existing grid lines before drawing new ones.
        """
        canvas = self.canvas
        self.grid_group = QGraphicsItemGroup()
        canvas.canvas.addItem(self.grid_group)
        is_visible = canvas.communicator.settings.get("tile grid visible", False)
        self.grid_group.setVisible(is_visible)

        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        # prevent grid lines being different sizes
        pen.setCosmetic(True)

        width, height = canvas.map_size * canvas.grid_spacing

        # vertical lines
        for x in range(0, width + 1, canvas.grid_spacing):
            line = canvas.canvas.addLine(x, 0, x, height, pen)
            self.grid_group.addToGroup(line)

        # create horizontal grid lines
        for y in range(0, height + 1, canvas.grid_spacing):
            line = canvas.canvas.addLine(0, y, width, y, pen)
            self.grid_group.addToGroup(line)

    def set_grid_visible(self, show: bool = None) -> None:
        """
        Toggles the visibility of the grid on the canvas.
        """
        is_visible: bool = self.grid_group.isVisible()

        if show is None:
            show = not is_visible

        self.grid_group.setVisible(show)
        self.canvas.communicator.settings['tile grid visible'] = show
