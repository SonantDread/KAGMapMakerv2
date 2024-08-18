# COMPILATION SCRIPT
# python app.py   --- run app in terminal

# core
import sys, os

# libs
from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
from PyQt6.QtCore import QEvent

# sources
from utils.windowsettings import Window
from utils.mainconfig import Config
from utils.input import input
from core.scripts.ui_layout import ui
from core.scripts.Communicator import Communicator
from core.scripts.modules._toolbar import module as Toolbar

from canvas import Canvas

class App(QMainWindow):
    def __init__(self):
        self.announce("STARTING APP")
        super().__init__()
        self.input = input(self)
        self.installEventFilter(self)

        self.toolbar = Toolbar()
        self.toolbar.setupUi()
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        print("Setting up main window")
        cfg = self.config = Config()
        cfg.build.connect(self.Quit)

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
        self.announce("RUNNING APP")

    def eventFilter(self, obj, event):
        self.input.eventFilter(obj, event)
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.config.build_from_active_window(event)

    def Quit(self, event: QEvent):
        self.announce("QUITTING APP")
        event.accept()

    def announce(self, message):
        print("============")
        print(message)
        print("============")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())