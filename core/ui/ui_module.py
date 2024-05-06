# Collection of custom classes for different solutions

from utils.vec import vec
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMenu, QWidget

class ui_module(QWidget):
    def __init__(self):
        super().__init__()
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
        self.menu_visible = False
        self.menu = None

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
        self.menu_visible = self.clicked_state and self.menu is not None

        if self.menu is not None:
            self.menu.setVisible(self.menu_visible)

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

    def addMenu(self, menu):
        if self.menu is None:
            self.menu = menu

class ui_menu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.children = []
        self.parent = parent
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        self.update()

    def update(self):
        geometry = self.parent.geometry()
        self.setGeometry(geometry.x(), geometry.y() + geometry.height(), geometry.width(), min(len(self.children), 75))
        