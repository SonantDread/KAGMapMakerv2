# COMPILATION SCRIPT
# python app.py   --- run app in terminal

# core
import sys

# libs
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QObject, pyqtSignal, QEvent

# sources
from utils.windowsettings import Window
from utils.mainconfig import Config

class App(QMainWindow):
    def __init__(self):
        self.announce("STARTING APP")
        super().__init__()

        cfg = self.config = Config()
        cfg.build.connect(self.Quit)

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