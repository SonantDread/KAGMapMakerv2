# Collection of custom classes for different solutions

from utils.vec import vec
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMenu, QWidget
from PyQt6.QtGui import QHideEvent
from PyQt6.QtCore import QTimer

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
        self.parent = parent
        self.menu = None
        self.active = True

    def reset(self, code):
        if code == 0:
            pass # default reset
        
        if code == 1:
            self.setTimeout(50)
            self.switchState(force_disable=True)

    def setHoverStyles(self, stylesheets):
        self.stylesheets = stylesheets
        
    def enterEvent(self, event):
        if self.parent.property("focus"):
            self.clicked_state = True
        else:
            self.hover_state = True
        self.updateStyle()

    def leaveEvent(self, event):
        self.hover_state = False
        self.updateStyle()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if not self.active:
                return

            self.switchState()
            self.parent.focus = self.clicked_state # set focus to buttons list when menu opens

            if self.menu is not None:
                if self.clicked_state:
                    pos = self.mapToGlobal(QtCore.QPoint(0, self.height()))
                    self.menu.move(pos.x(), pos.y())
                    self.menu.show()

            self.updateStyle()
            super().mousePressEvent(event)
    
    def setTimeout(self, time):
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self.resetTimeout)
        self.timeout_timer.start(time)

        self.active = False

    def switchState(self, force_disable=False):
        self.clicked_state = False if force_disable else not self.clicked_state
        self.updateStyle()

    def resetTimeout(self):
        self.active = True

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
    def __init__(self, parent=None, label=None):
        super().__init__(parent)
        self.children = []
        self.parent = parent
        self.label = label
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        self.update()

    def update(self):
        geometry = self.parent.geometry()
        self.setGeometry(geometry.x(), geometry.y() + geometry.height(), geometry.width(), min(len(self.children), 75))

    def hideEvent(self, event: QHideEvent):
        link = self.label if self.label is not None else self.parent
        if isinstance(link, ui_button):
            link.reset(1)