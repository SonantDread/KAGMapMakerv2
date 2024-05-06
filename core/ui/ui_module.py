# Collection of custom classes for different solutions

from utils.vec import vec
from PyQt6 import QtWidgets

class ui_module:
    def __init__(self):
        self.pos = vec(0,0)
        self.id = 0

    def set_id(self, id):
        self.id = id

    def set_pos(self, vec):
        self.pos = vec

class button(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheets = {}

    def setHoverStyles(self, stylesheets):
        self.stylesheets = stylesheets
        
    def enterEvent(self, event):
        self.setStyleSheet(self.stylesheets['enter'])

    def leaveEvent(self, event):
        self.setStyleSheet(self.stylesheets['leave'])