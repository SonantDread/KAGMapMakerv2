from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from core.ui.ui_module import hoverbutton

class Ui_MainWindow():
    def setupUi(self, MainWindow):
        MainWindow.setMouseTracking(True)
        self.file_settings_view_dropdowns = QtWidgets.QWidget(parent=MainWindow)
        self.file_settings_view_dropdowns.setObjectName("file_settings_view_dropdowns")
        self.groupBox = QtWidgets.QGroupBox(parent=self.file_settings_view_dropdowns)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 251, 25))
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        
        button_names = ["File", "Edit", "View", "Help"]
        self.buttons = []

        for index, name in enumerate(button_names):
            button = button(parent=self.groupBox)
            button.setGeometry(QtCore.QRect(61 * index, 0, 61, 25))
            button.setObjectName(f"pushButton_{index}")
            button.setText(name)

            button.setStyleSheet("border: 0px solid transparent; background-color: transparent; color: black; padding: 5px;")
            button.setHoverStyles({
                "enter":"border: 1px solid black; background-color: lightgray; color: black; padding: 4px;",
                "leave":"border: 0px solid transparent; background-color: transparent; color: black; padding: 5px;"
                })
            button.setMouseTracking(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            
            self.buttons.append(button)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))