from PyQt6.QtWidgets import QGraphicsItemGroup
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt

class GridManager:
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
        self.grid_group = QGraphicsItemGroup()
        self.canvas.canvas.addItem(self.grid_group)
        is_visible = self.canvas.communicator.settings.get("tile grid visible", False)
        self.grid_group.setVisible(is_visible)

        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(1)
        # prevent grid lines being different sizes
        pen.setCosmetic(True)

        width = self.canvas.size.x * self.canvas.grid_spacing
        height = self.canvas.size.y * self.canvas.grid_spacing

        # vertical lines
        for x in range(0, width + 1, self.canvas.grid_spacing):
            line = self.canvas.canvas.addLine(x, 0, x, height, pen)
            self.grid_group.addToGroup(line)

        # create horizontal grid lines
        for y in range(0, height + 1, self.canvas.grid_spacing):
            line = self.canvas.canvas.addLine(0, y, width, y, pen)
            self.grid_group.addToGroup(line)

    def set_grid_visible(self, show: bool = None) -> None:
        """
        Toggles the visibility of the grid on the canvas.

        Args:
            show (bool): Whether to show or hide the grid, or toggle if not specified.

        Returns:
            None
        """
        is_visible: bool = self.grid_group.isVisible()

        if show is None:
            show = not is_visible

        self.grid_group.setVisible(show)
        self.canvas.communicator.settings['tile grid visible'] = show
