"""
Used to compile all scripts into a functional app.
Run the map maker in terminal by using 'python app.py'.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
from PyQt6.QtCore import QEvent

from utils.windowsettings import Window
from utils.mainconfig import Config
from core.scripts.ui_layout import ui
from core.scripts.communicator import Communicator
from core.scripts.toolbar import Toolbar
from canvas import Canvas

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
        self.installEventFilter(self)

        self.toolbar = Toolbar()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        print("Setting up main window")
        cfg = self.config = Config()
        cfg.build.connect(self.quit)

        print("Loading UI")
        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)

        # create layout for main widget
        self.layout = QHBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.layout)

        self.ui_layout = ui(self.main_widget)
        self.ui_layout.load()

        window = cfg.window = Window()
        window.ui_window = self
        window.SetupWindow()

        # load canvas
        print("Loading Canvas")
        self.canvas = Canvas((200, 130))

        # add canvas to layout
        self.layout.addWidget(self.canvas)

        self.communicator = Communicator()
        self._announce("RUNNING APP")

    def closeEvent(self, event) -> None:
        """
        Handles the close event of the application.

        Saves the current configuration when the application is closed.

        Parameters:
            event (QEvent): The close event.
        """
        self.config.build_from_active_window(event)

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
