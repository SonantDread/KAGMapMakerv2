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
Used to compile all scripts into a functional app.
Run the map maker in terminal by using 'python app.py'.
"""

import atexit
import os
import sys

from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from base.kag_image import KagImage
from core.Canvas.canvas import Canvas
from core.communicator import Communicator
from core.gui_module_handler import GUIModuleHandler
from core.toolbar import Toolbar
from core.window_config_handler import WindowConfigHandler
from utils.vec2f import Vec2f

class App(QMainWindow):
    """
    The main application class for the map maker.

    This class sets up the main window and initializes all the necessary components
    for the application to run.
    """
    def __init__(self):
        super().__init__()

        self.window_config = WindowConfigHandler(self)
        self.window_config.load_window_config()

        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)

        self.main_layout: QHBoxLayout = QHBoxLayout(self.main_widget)
        self.setLayout(self.main_layout)
        self.main_widget.setLayout(self.main_layout)

        # left sidebar
        self.ui_layout = GUIModuleHandler(self.main_widget)

        self.toolbar = Toolbar(self)
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.canvas = Canvas(Vec2f(200, 80))
        self.main_layout.addWidget(self.canvas)

        self.communicator = Communicator()
        self.communicator.set_canvas(self.canvas)
        self.communicator.set_exec_path(os.path.dirname(os.path.abspath(__file__)))

        last_map_path = self.communicator.last_saved_map_path
        if last_map_path:
            KagImage().load_map(last_map_path)

        atexit.register(self.save_on_exit)

    def save_on_exit(self) -> None:
        """
        Saves the current application configuration on exit.
        """
        self.window_config.save_window_config()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    application = App()
    application.show()
    sys.exit(app.exec())
