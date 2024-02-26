from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class BlockSelector(QWidget):  # Inherit from QWidget instead of QGraphicsProxyWidget
    def __init__(self, blocks, selected_block):
        super().__init__()

        self.blocks = blocks
        self.selected_block = selected_block

        self.createMenu()

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

        # Add the layout to the widget
        self.setLayout(layout)

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
