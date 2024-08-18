from PyQt6.QtCore import QEvent, QPoint

class input:
    def __init__(self, parent):
        self.parent = parent

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            mouse_event = event