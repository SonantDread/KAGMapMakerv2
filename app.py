# COMPILATION SCRIPT
# python app.py   --- run app in terminal

# core
import sys

# libs
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QObject, pyqtSignal, QEvent

# sources
from utils.window import Window
from utils.config import Config

class App(QMainWindow):
    def __init__(self):
        self.announce("STARTING APP")
        super().__init__()

        self.config = Config()
        self.config.resize.connect(self.Quit)

        self.SetupWindow()

    def SetupWindow(self):
        window_config = self.config.data['Window']
        window_width = int(window_config['size']['width'])
        window_height = int(window_config['size']['height'])

        self.setWindowTitle('KAG Map Maker')
        self.setGeometry(0, 0, window_width, window_height) # offsets x,y & width,height

    def closeEvent(self, event):
        self.config.resize_to_window(event)
    
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