from PIL import Image
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget

from base.image_handler import ImageHandler
from core.communicator import Communicator

BUTTON_WIDTH, BUTTON_HEIGHT = 48, 48
# ARGB colors for teams
# subtract key by 1 to get team
TEAMS = {
    0: (255, 136, 136, 136),
    1: (255, 44, 175, 222),
    2: (255, 213, 84, 63),
    3: (255, 157, 202, 34),
    4: (255, 211, 121, 224),
    5: (255, 254, 165, 61),
    6: (255, 46, 229, 162),
    7: (255, 95, 132, 236)
}

communicator = Communicator()

class SelectionButton(QPushButton):
    def __init__(self, team: int, parent) -> None:
        super().__init__(parent)
        self.team = team
        self.setToolTip(str(f'Team {team}'))
        self.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)

    def mousePressEvent(self, event) -> None:
        qt_b = Qt.MouseButton
        if event.button() == qt_b.LeftButton or event.button() == qt_b.RightButton:
            communicator.team = self.team

class Teams(QWidget):
    def __init__(self, parent, picker) -> None:
        super().__init__(parent)
        self.setParent(parent)
        self.parent_widget = parent

        self.communicator = Communicator()
        self.images = ImageHandler()

        self.widget = QWidget(self.parent_widget)
        self.widget.setFixedSize(QSize(self._get_tab_size(), BUTTON_HEIGHT * 2))
        self.widget.move(0, picker.tab_holder.height())

        self.teams_tab = None
        self.setup_ui()

    def setup_ui(self) -> None:
        teams_tab = QGridLayout(parent=self.widget)
        teams_tab.setSpacing(0)
        teams_tab.setContentsMargins(0, 0, 0, 0)

        x, y = 0, 0
        for key, value in TEAMS.items():
            button = SelectionButton(key-1, self)
            button.setIcon(self._scale_image(self.__get_color_image(value)))
            button.setIconSize(QSize(BUTTON_WIDTH, BUTTON_HEIGHT))

            teams_tab.addWidget(button, y, x)
            x += 1
            if x >= 4: # max buttons
                x = 0
                y += 1

        self.teams_tab = teams_tab

    def __get_color_image(self, color: tuple) -> QPixmap:
        return Image.new("RGBA", (8, 8), (color[1], color[2], color[3], color[0])).toqpixmap()

    def _get_tab_size(self) -> None:
        return int(BUTTON_WIDTH * 4 + 40)

    def _scale_image(self, image: QPixmap) -> QIcon:
        scaled_pixmap = image.scaled(
            BUTTON_WIDTH - 10,
            BUTTON_HEIGHT - 10,
            Qt.AspectRatioMode.KeepAspectRatio
        )
        return QIcon(scaled_pixmap)
