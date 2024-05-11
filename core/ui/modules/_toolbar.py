# toolbar.py

from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction

class Toolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        action1 = QAction("Action 1", self)
        action1.triggered.connect(self.action1_triggered)
        self.addAction(action1)
        
        action2 = QAction("Action 2", self)
        action2.triggered.connect(self.action2_triggered)
        self.addAction(action2)

    def action1_triggered(self):
        print("Action 1 triggered")
        
    def action2_triggered(self):
        print("Action 2 triggered")
