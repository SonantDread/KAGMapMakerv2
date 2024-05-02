from PyQt6 import QtCore, QtGui, QtWidgets
from core.ui.ui_module import ui_module

class test(ui_module):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(141, 300)
        self.gridLayoutWidget = QtWidgets.QWidget(parent=Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 158, 301))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_2.setText(_translate("Form", "PushButton"))
        self.pushButton.setText(_translate("Form", "PushButton"))
