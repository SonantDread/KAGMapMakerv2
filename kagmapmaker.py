# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'kagmapmaker.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1728, 972)
        self.title_ButtonHolder = QtWidgets.QWidget(MainWindow)
        self.title_ButtonHolder.setEnabled(True)
        self.title_ButtonHolder.setObjectName("title_ButtonHolder")
        self.Pages = QtWidgets.QStackedWidget(self.title_ButtonHolder)
        self.Pages.setGeometry(QtCore.QRect(0, 0, 1728, 972))
        self.Pages.setObjectName("Pages")
        self.titleScreen = QtWidgets.QWidget()
        self.titleScreen.setObjectName("titleScreen")
        self.title_Create = QtWidgets.QPushButton(self.titleScreen)
        self.title_Create.setEnabled(True)
        self.title_Create.setGeometry(QtCore.QRect(576, 100, 432, 162))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        font.setStrikeOut(False)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.title_Create.setFont(font)
        self.title_Create.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.title_Create.setAcceptDrops(False)
        self.title_Create.setToolTip("")
        self.title_Create.setToolTipDuration(-1)
        self.title_Create.setStatusTip("")
        self.title_Create.setAutoFillBackground(False)
        self.title_Create.setCheckable(False)
        self.title_Create.setObjectName("title_Create")
        self.title_Settings = QtWidgets.QPushButton(self.titleScreen)
        self.title_Settings.setEnabled(True)
        self.title_Settings.setGeometry(QtCore.QRect(576, 362, 432, 162))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        self.title_Settings.setFont(font)
        self.title_Settings.setObjectName("title_Settings")
        self.title_Quit = QtWidgets.QPushButton(self.titleScreen)
        self.title_Quit.setGeometry(QtCore.QRect(576, 624, 432, 162))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        self.title_Quit.setFont(font)
        self.title_Quit.setObjectName("title_Quit")
        self.title_BackgroundImage = QtWidgets.QLabel(self.titleScreen)
        self.title_BackgroundImage.setGeometry(QtCore.QRect(0, 0, 1728, 972))
        self.title_BackgroundImage.setText("")
        self.title_BackgroundImage.setPixmap(QtGui.QPixmap("Sprites/Back/BackgroundCastle.png")) # todo: right path
        self.title_BackgroundImage.setScaledContents(True)
        self.title_BackgroundImage.setObjectName("title_BackgroundImage")
        self.title_BackgroundImage.raise_()
        self.title_Create.raise_()
        self.title_Settings.raise_()
        self.title_Quit.raise_()
        self.Pages.addWidget(self.titleScreen)
        self.setupCreate = QtWidgets.QWidget()
        self.setupCreate.setObjectName("setupCreate")
        self.setupCreate_BackgroundImage = QtWidgets.QLabel(self.setupCreate)
        self.setupCreate_BackgroundImage.setGeometry(QtCore.QRect(0, 0, 1728, 972))
        self.setupCreate_BackgroundImage.setText("")
        self.setupCreate_BackgroundImage.setPixmap(QtGui.QPixmap("Sprites/Back/BackgroundTrees.png")) # todo: right path
        self.setupCreate_BackgroundImage.setScaledContents(True)
        self.setupCreate_BackgroundImage.setObjectName("setupCreate_BackgroundImage")
        self.setupCreate_CreateMap = QtWidgets.QPushButton(self.setupCreate)
        self.setupCreate_CreateMap.setEnabled(True)
        self.setupCreate_CreateMap.setGeometry(QtCore.QRect(576, 50, 432, 162))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        font.setStrikeOut(False)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.setupCreate_CreateMap.setFont(font)
        self.setupCreate_CreateMap.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.setupCreate_CreateMap.setAcceptDrops(False)
        self.setupCreate_CreateMap.setToolTip("")
        self.setupCreate_CreateMap.setToolTipDuration(-1)
        self.setupCreate_CreateMap.setStatusTip("")
        self.setupCreate_CreateMap.setAutoFillBackground(False)
        self.setupCreate_CreateMap.setCheckable(False)
        self.setupCreate_CreateMap.setObjectName("setupCreate_CreateMap")
        self.setupCreate_LoadMap = QtWidgets.QPushButton(self.setupCreate)
        self.setupCreate_LoadMap.setEnabled(True)
        self.setupCreate_LoadMap.setGeometry(QtCore.QRect(576, 262, 432, 162))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        font.setStrikeOut(False)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.setupCreate_LoadMap.setFont(font)
        self.setupCreate_LoadMap.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.setupCreate_LoadMap.setAcceptDrops(False)
        self.setupCreate_LoadMap.setToolTip("")
        self.setupCreate_LoadMap.setToolTipDuration(-1)
        self.setupCreate_LoadMap.setStatusTip("")
        self.setupCreate_LoadMap.setAutoFillBackground(False)
        self.setupCreate_LoadMap.setCheckable(False)
        self.setupCreate_LoadMap.setObjectName("setupCreate_LoadMap")
        self.setupCreate_RenderMap = QtWidgets.QPushButton(self.setupCreate)
        self.setupCreate_RenderMap.setEnabled(True)
        self.setupCreate_RenderMap.setGeometry(QtCore.QRect(576, 462, 432, 162))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        font.setStrikeOut(False)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.setupCreate_RenderMap.setFont(font)
        self.setupCreate_RenderMap.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.setupCreate_RenderMap.setAcceptDrops(False)
        self.setupCreate_RenderMap.setToolTip("")
        self.setupCreate_RenderMap.setToolTipDuration(-1)
        self.setupCreate_RenderMap.setStatusTip("")
        self.setupCreate_RenderMap.setAutoFillBackground(False)
        self.setupCreate_RenderMap.setCheckable(False)
        self.setupCreate_RenderMap.setObjectName("setupCreate_RenderMap")
        self.setupCreate_Back = QtWidgets.QPushButton(self.setupCreate)
        self.setupCreate_Back.setEnabled(True)
        self.setupCreate_Back.setGeometry(QtCore.QRect(576, 662, 432, 162))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(48)
        font.setStrikeOut(False)
        font.setKerning(True)
        font.setStyleStrategy(QtGui.QFont.PreferDefault)
        self.setupCreate_Back.setFont(font)
        self.setupCreate_Back.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.setupCreate_Back.setAcceptDrops(False)
        self.setupCreate_Back.setToolTip("")
        self.setupCreate_Back.setToolTipDuration(-1)
        self.setupCreate_Back.setStatusTip("")
        self.setupCreate_Back.setAutoFillBackground(False)
        self.setupCreate_Back.setCheckable(False)
        self.setupCreate_Back.setObjectName("setupCreate_Back")
        self.Pages.addWidget(self.setupCreate)
        self.createCanvas = QtWidgets.QWidget()
        self.createCanvas.setObjectName("createCanvas")
        self.Pages.addWidget(self.createCanvas)
        MainWindow.setCentralWidget(self.title_ButtonHolder)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_2 = QtWidgets.QAction(MainWindow)
        self.actionSave_2.setObjectName("actionSave_2")

        self.retranslateUi(MainWindow)
        self.Pages.setCurrentIndex(0) # starting page
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # buttons
        self.title_Create.clicked.connect(lambda: self.setPageIndex(1))
        self.title_Quit.clicked.connect(lambda: app.quit())

        # self.setupCreate_CreateMap.clicked.connect(lambda: )
        # self.setupCreate_LoadMap.clicked.connect(lambda: )
        # self.setupCreate_RenderMap.clicked.connect(lambda: )
        self.setupCreate_Back.clicked.connect(lambda: self.setPageIndex(0))

    def setPageIndex(self, pageIndex: int):
        self.Pages.setCurrentIndex(pageIndex)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title_Create.setText(_translate("MainWindow", "Create"))
        self.title_Settings.setText(_translate("MainWindow", "Settings"))
        self.title_Quit.setText(_translate("MainWindow", "Quit"))
        self.setupCreate_CreateMap.setText(_translate("MainWindow", "Create Map"))
        self.setupCreate_LoadMap.setText(_translate("MainWindow", "Load Map"))
        self.setupCreate_RenderMap.setText(_translate("MainWindow", "Render Map"))
        self.setupCreate_Back.setText(_translate("MainWindow", "Back"))
        self.actionSave.setText(_translate("MainWindow", "New"))
        self.actionSave_2.setText(_translate("MainWindow", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
    # todo: hook this file up to mainwindow.py