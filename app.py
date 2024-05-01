# COMPILATION SCRIPT
# python app.py   --- run app in terminal

# core
import sys

# libs
from PyQt6.QtWidgets import QApplication, QMainWindow

# sources
from utils.window import Window
from utils.config import Config

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.SetupWindow()

    def SetupWindow(self):
        window_config = self.config.data['Window']
        window_width = int(window_config['size']['width'])
        window_height = int(window_config['size']['height'])

        self.setWindowTitle('KAG Map Maker')
        self.setGeometry(0, 0, window_width, window_height) # offsets x,y & width,height

    def closeEvent(self, event):
        # self.config.resize_to_window()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())