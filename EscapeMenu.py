from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from KagImage import KagImage

class EscapeMenu(QWidget):
    def __init__(self, canvas, mainwindow):
        super(EscapeMenu, self).__init__()

        self.canvas = canvas
        self.init_ui()
        self.mainwindow = mainwindow

    def init_ui(self):
        layout = QVBoxLayout()

        # Add buttons to the layout
        buttons_layout = QVBoxLayout()

        # Back to Canvas button
        back_button = QPushButton("Back to Canvas")
        back_button.clicked.connect(self.on_back_clicked)
        buttons_layout.addWidget(back_button)

        # # Help button # ? todo: display an image for keybinds
        # help_button = QPushButton("Help")
        # help_button.clicked.connect(self.on_help_clicked)
        # buttons_layout.addWidget(help_button)

        # Settings button
        settings_button = QPushButton("Settings (WIP)")
        settings_button.clicked.connect(self.on_settings_clicked)
        buttons_layout.addWidget(settings_button)

        # Save Map button
        save_button = QPushButton("Save Map")
        save_button.clicked.connect(self.on_save_clicked)
        buttons_layout.addWidget(save_button)

        # Load Map button
        load_button = QPushButton("Load Map")
        load_button.clicked.connect(self.on_load_clicked)
        buttons_layout.addWidget(load_button)

        # Load Map button
        rendermap_button = QPushButton("Render Map")
        rendermap_button.clicked.connect(self.on_render_clicked)
        buttons_layout.addWidget(rendermap_button)

        # leave a space so you can't accidentally click exit app
        blank_button = QPushButton("")
        blank_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        buttons_layout.addWidget(blank_button)

        # Exit app button
        exit_button = QPushButton("Exit App")
        exit_button.clicked.connect(self.on_exit_clicked)
        buttons_layout.addWidget(exit_button)

        # Add buttons layout to the main layout
        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.hide()

    def toggle_visibility(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def on_settings_clicked(self):
        # Implement the action for the Settings button
        print("Settings clicked")

    # def on_help_clicked(self):
    #     # Implement the action for the Help button
    #     print("Help clicked")

    def on_back_clicked(self):
        self.mainwindow.toggleEscMenu()

    def on_exit_clicked(self):
        # Implement the action for the Exit App button
        raise SystemExit

    # save and load map
    def on_save_clicked(self):
        # Implement the action for the Save Map button
        if(KagImage(self.canvas).saveMap()):
            self.mainwindow.toggleEscMenu()

    def on_load_clicked(self):
        if(KagImage(self.canvas).loadMap()):
            self.mainwindow.toggleEscMenu()

    def on_render_clicked(self):
        if(KagImage(self.canvas).renderMap()):
            self.mainwindow.toggleEscMenu()