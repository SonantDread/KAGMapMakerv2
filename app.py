# COMPILATION SCRIPT
# python app.py   --- run app in terminal

# core
import sys, os

# libs
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QEvent

# sources
from utils.windowsettings import Window
from utils.mainconfig import Config
from core.ui.ui_grid import ui

#test
from canvas import canvas

class App(QMainWindow):
    def __init__(self):
        self.announce("STARTING APP")
        super().__init__()

        print("Setting up main window")
        cfg = self.config = Config()
        cfg.build.connect(self.Quit)

        print("Loading UI")
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.ui_grid = ui(self.main_widget)
        self.ui_grid.load()
        
        window = cfg.window = Window()
        window.ui_window = self
        window.SetupWindow()

        self.announce("RUNNING APP")

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