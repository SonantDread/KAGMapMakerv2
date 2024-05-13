import sys
from PyQt6.QtCore import Qt, QPoint
from PyQt6 import QtCore, QtGui, QtWidgets
from core.ui.ui_module import ui_module

class module(ui_module):
    def __init__(self, parent=None):
        super().__init__(self)
        self.parent = parent
        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToParent(event.pos() - self.offset)) # self.move moves CONTENTS of the widget!!!!!! solve later

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def setupUi(self):
        self.parent.setObjectName("menu")
        
        self.gridLayoutWidget = QtWidgets.QWidget(parent=self.parent)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 25, 250, 250))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        
        self.tabWidget = QtWidgets.QTabWidget(parent=self.gridLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tiles")
        self.tabWidget.addTab(self.tab, "")

        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("entities")
        self.tabWidget.addTab(self.tab_1, "")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("colors")
        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self.parent)

        self.parent.mousePressEvent = self.mousePressEvent
        self.parent.mouseMoveEvent = self.mouseMoveEvent
        self.parent.mouseReleaseEvent = self.mouseReleaseEvent

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("menu", "Tiles"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("menu", "Entities"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("menu", "Colors"))