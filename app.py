"""
Used to compile all scripts into a functional app.
Run the map maker in terminal by using 'python app.py'.
"""

import atexit
import sys
import os

from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from core.canvas import Canvas
from core.communicator import Communicator
from core.toolbar import Toolbar
from core.gui_module_handler import GUIModuleHandler
from core.window_config_handler import WindowConfigHandler
from utils.vec2f import Vec2f

class App(QMainWindow):
    """
    The main application class for the map maker.

    This class sets up the main window and initializes all the necessary components
    for the application to run.
    """
    def __init__(self):
        """
        Initializes the App class and sets up the main window.
        """
        self._announce("STARTING APP")
        super().__init__()

        print("Setting up main window")
        self.window_config = WindowConfigHandler(self)
        self.window_config.load_window_config()

        print("Loading UI")
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)

        # create layout for main widget
        self.main_layout: QHBoxLayout = QHBoxLayout(self.main_widget)
        self.setLayout(self.main_layout)
        self.main_widget.setLayout(self.main_layout)

        # todo: this should all just be a large widget for the menus, and canvas should be a seperate thing
        # picker menus
        self.ui_layout = GUIModuleHandler(self.main_widget)

        self.toolbar = Toolbar(self)
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        # load canvas
        print("Loading Canvas")
        self.canvas = Canvas(Vec2f(200, 80))

        # add canvas to layout
        self.main_layout.addWidget(self.canvas)

        self.communicator = Communicator()
        self.communicator.set_canvas(self.canvas)
        self.communicator.set_exec_path(os.path.dirname(os.path.abspath(__file__)))
        self._announce("RUNNING APP")
        atexit.register(self.save_on_exit)

    def save_on_exit(self) -> None:
        """
        Saves the current application configuration on exit.
        """

        self.window_config.save_window_config()

    def _announce(self, message) -> None:
        """
        Prints a message to indicate an event in the application.

        Parameters:
            message (str): The message to be printed.
        """
        print("============")
        print(message)
        print("============")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    application = App()
    application.show()
    sys.exit(app.exec())
