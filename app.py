# COMPILATION SCRIPT
# python app.py   --- run app in terminal

# core
import sys, os

# libs
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QEvent
from PyQt6.uic import loadUiType, loadUi

# sources
from utils.windowsettings import Window
from utils.mainconfig import Config
from core.ui.ui_grid import ui

#test
from core.ui.modules.canvas import Canvas
class App(QMainWindow):
    def __init__(self):
        self.announce("STARTING APP")
        super().__init__()

        print("Setting up main window")
        cfg = self.config = Config()
        cfg.build.connect(self.Quit)

        window = cfg.window = Window()
        window.ui_window = self
        window.SetupWindow()

        print("Loading UI")
        ui_grid = self.ui_grid = ui()
        #for module in ui_grid.modules:
        #    module.setupUi(self)

        #testarea
        #main_canvas = self.canvas = Canvas()
        #testareaend

        #* load the file ui file
        self.loadGUIFromFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "core", "ui", "modules", "mapmakergui.ui"))

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

    # expects a direct path to file, ie 'core\ui\modules\mapmaker.ui'
    # parent class is the class that it will be the subclass to
    def loadGUIFromFile(self, directpathtofile: str, parent_class=None) -> None:
        # Determine whether the file is a .ui or .py file
        is_py = directpathtofile.endswith('.py')

        # Load from .ui file
        if not is_py:
            try:
                loadUiType(directpathtofile)
                self.mapmaker_ui = loadUi(directpathtofile, self)
            except FileNotFoundError:
                raise FileNotFoundError(f"Could not find file path: '{directpathtofile}'")
            except Exception as e:
                raise RuntimeError(f"Error loading UI from file: {e}")

        # Load from .py file
        else:
            try:
                # Import the class from the Python file
                from core.ui.modules.mapmakergui import Ui_MainWindow
                self.mapmaker_ui = Ui_MainWindow()
                self.mapmaker_ui.setupUi(parent_class if parent_class is not None else self)
            except Exception as e:
                raise RuntimeError(f"Error loading UI from Python file: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())