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
        width = self.frameGeometry().width()
        height = self.frameGeometry().height()
        self.setGeometry(vec.x, vec.y, width, height)

class ui_button(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stylesheets = {}
        self.clicked_state = False
        self.hover_state = False

    def setHoverStyles(self, stylesheets):
        self.stylesheets = stylesheets
        
    def enterEvent(self, event):
        self.hover_state = True
        self.updateStyle()

    def leaveEvent(self, event):
        self.hover_state = False
        self.updateStyle()

    def mousePressEvent(self, event):
        self.clicked_state = not self.clicked_state
        self.updateStyle()
        super().mousePressEvent(event)

    def updateStyle(self):
        if self.clicked_state:
            self.addStyleSheet(self.stylesheets.get('clicked', ''))
        elif self.hover_state:
            self.addStyleSheet(self.stylesheets.get('enter', ''))
        else:
            self.addStyleSheet(self.stylesheets.get('leave', ''))

    def addStyleSheet(self, stylesheet):
        self.setStyleSheet(self.styleSheet() + stylesheet)