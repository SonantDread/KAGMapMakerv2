from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from core.ui.ui_module import ui_module, ui_button
from core.ui.preset import default_preset

class module(ui_module):
    def setupUi(self, parentwidget):
        parentwidget.setMouseTracking(True)
        self.list_width = 250
        self.list_height = 25
        
        self.file_settings_view_dropdowns = QtWidgets.QWidget(parent=parentwidget)
        self.file_settings_view_dropdowns.setObjectName("file_settings_view_dropdowns")
        self.groupBox = QtWidgets.QGroupBox(parent=self.file_settings_view_dropdowns)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, self.list_width, self.list_height))
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        
        button_names = ["File", "Edit", "View", "Help"]
        self.buttons = []

        for index, name in enumerate(button_names):
            button_width = int(self.list_width/len(button_names))
            button = ui_button(parent=self.groupBox)
            button.setGeometry(QtCore.QRect(button_width * index, 0, button_width, self.list_height))
            button.setObjectName(f"pushButton_{index}")
            button.setText(name)

            preset = default_preset()
            button.setStyleSheet("border: 0px solid transparent; background-color: transparent; color: black; padding: 5px;")
            button.setHoverStyles({
                "enter":f"background-color: {preset.getHoverColor()};",
                "leave":f"background-color: {preset.getBackgroundColor()};",
                "clicked":f"background-color: {preset.getHoverColor()};"
                })
            
            button.setMouseTracking(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            self.buttons.append(button)

        self.retranslateUi(parentwidget)
        QtCore.QMetaObject.connectSlotsByName(parentwidget)

    def retranslateUi(self, Mparentwidget):
        _translate = QtCore.QCoreApplication.translate