from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget, QHBoxLayout, QListWidgetItem, QListWidget 
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSignal

from Image import Image
import tempfile

import os
class BlockSelector(QWidget):  # Inherit from QWidget instead of QGraphicsProxyWidget
    blockSelected = pyqtSignal(str)  # Signal emitting the block name as a string
    def __init__(self, blocks, selected_block,parent=None):
        #super(BlockSelector, self).__init__("Block Selector", parent)
        self.imageProcessor = Image()
        super(BlockSelector, self).__init__(parent)  # Call superclass constructor with parent
        self.setWindowTitle("Block Selector")

        self.blocks = blocks
        self.selected_block = selected_block
        self.listWidget = QListWidget(self)
        self.layout = QVBoxLayout(self)  # Set the main layout of the widget
        self.layout.addWidget(self.listWidget)  # Add the listWidget to the layout
        self.populateBlocks()
        self.createMenu()
        self.listWidget.itemClicked.connect(self.onBlockSelected)

    def onBlockSelected(self, item):
        self.selected_block = item.text()
        print("Selected Block:", self.selected_block)
        self.blockSelected.emit(self.selected_block)


    def populateBlocks(self):
        # Example block items, replace with your actual block data
        blockNames = ["tile_ground", "tile_grassy_ground", "tile_grass"]

        for blockName in blockNames:
            blockIndex = self.imageProcessor.getTileIndexByName(blockName)
            blockImage = self.imageProcessor.getBlockPNGByIndex(blockIndex)
            iconPath = self.saveBlockImage(blockImage, blockName)  # Save the PIL image to a temporary file and return the path
            item = QListWidgetItem(QIcon(iconPath), blockName)
            self.listWidget.addItem(item)

    def selectedBlock(self):
        return self.listWidget.currentItem().text() if self.listWidget.currentItem() else None

    def saveBlockImage(self, blockImage, blockName):
        # Save the PIL Image to a temporary file
        tempImagePath = os.path.join(tempfile.gettempdir(), f"{blockName}.png")
        blockImage.save(tempImagePath)
        return tempImagePath
    def saveBlockImage(self, blockImage, blockName):
        # Save the PIL Image to a temporary file
        tempImagePath = os.path.join(tempfile.gettempdir(), f"{blockName}.png")
        blockImage.save(tempImagePath)
        return tempImagePath

    def getSelectedBlock(self):
        return self.selected_block
    
    def createMenu(self):
        layout = QVBoxLayout()

        # Create a tab widget
        tab_widget = QTabWidget(self)

        # Create tabs
        tiles_tab = QWidget()
        entities_tab = QWidget()

        # Add content to tabs
        self.createTabContent(tiles_tab, "Tiles")
        self.createTabContent(entities_tab, "Entities")

        # Add tabs to the tab widget
        tab_widget.addTab(tiles_tab, "Tiles")
        tab_widget.addTab(entities_tab, "Entities")

        # Add the tab widget to the layout
        layout.addWidget(tab_widget)
        
        # Set a fixed size for the BlockSelector widget
        self.setFixedSize(200, 300)  # Adjust the size as needed

    def createTabContent(self, tab, tab_name):
        # Create a layout for the tab
        tab_layout = QVBoxLayout(tab)

        # Create buttons with images
        button_layout = QHBoxLayout()

        button1 = self.createButtonWithImage("dirt.png", "Button 1")
        button2 = self.createButtonWithImage("dirt.png", "Button 2")

        # Connect buttons to the handleButtonClick method
        button1.clicked.connect(self.handleButtonClick)
        button2.clicked.connect(self.handleButtonClick)

        # Add buttons to the layout
        button_layout.addWidget(button1)
        button_layout.addWidget(button2)

        # Add the button layout to the tab layout
        tab_layout.addLayout(button_layout)

        # Add any additional content to the tab as needed
        label = QLabel("Selected Block: {}".format(self.selected_block), tab)
        tab_layout.addWidget(label)

    def createButtonWithImage(self, image_path, text):
        button = QPushButton(self)
        button.setIcon(QIcon(image_path))
        button.setIconSize(QSize(50, 50))
        button.setText(text)
        return button

    def handleButtonClick(self):
        sender_button = self.sender()
        if sender_button:
            self.selected_block = sender_button.text()
            print("Selected Block:", self.selected_block)
