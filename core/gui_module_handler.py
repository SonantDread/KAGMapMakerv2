from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from core.modules.picker import Picker
from core.modules.teams import Teams
from utils.file_handler import FileHandler

class GUIModuleHandler:
    def __init__(self, window: QWidget):
        self.fh = FileHandler()
        self.app_window = window
        self.modules = []

        self.central_widget = QWidget(self.app_window)

        self.container = QVBoxLayout(self.central_widget)
        self.container.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.central_widget.setFixedSize(400, 280)

        self.setup_modules()

    def setup_modules(self):
        picker = Picker(self.app_window)
        teams = Teams(self.app_window, picker)
        # add to layout
        self.container.addWidget(picker)
        self.container.addWidget(teams)

        self.modules.extend([picker, teams])
