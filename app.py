"""
Used to compile all scripts into a functional app.
Run the map maker in terminal by using 'python app.py'.
"""

import atexit
import sys

from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QWidget

from canvas import Canvas
from core.communicator import Communicator
from core.toolbar import Toolbar
from core.gui_module_handler import GUIModuleHandler
from utils.config_handler import ConfigHandler
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
        self.config_handler = ConfigHandler()
        self.config_handler.load_config(self)

        print("Loading UI")
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)

        # create layout for main widget
        self.layout = QHBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)

        self.ui_layout = GUIModuleHandler(self)
        self.ui_layout.setup_modules()

        self.toolbar = Toolbar(self)
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        # load canvas
        print("Loading Canvas")
        self.canvas = Canvas(Vec2f(200, 130))

        # add canvas to layout
        self.layout.addWidget(self.canvas)

        self.communicator = Communicator()
        self._announce("RUNNING APP")
        atexit.register(self.save_on_exit)

    def save_on_exit(self) -> None:
        """
        Saves the current application configuration on exit.

        Args:
            None

        Returns:
            None
        """
        self.config_handler.save_config(self)

    def quit(self, event: QEvent) -> None:
        """
        Handles the quit event of the application.

        Prints a message to indicate that the application is quitting.

        Parameters:
            event (QEvent): The quit event.
        """
        self._announce("QUITTING APP")
        event.accept()

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
