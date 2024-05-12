# # toolbar.py

# from PyQt6.QtWidgets import QToolBar, QMenu
# from PyQt6.QtGui import QAction
# from PyQt6 import QtCore

# class Toolbar(QToolBar):
#     def __init__(self, parent = None):
#         super().__init__(parent)
#         self.initUI()

#     def initUI(self):
#         # Create a dropdown menu
#         menu = QMenu(self)
        
#         # Add actions to the dropdown menu
#         action1 = QAction("Action 1", self)
#         action1.triggered.connect(self.action1_triggered)
#         menu.addAction(action1)
        
#         action2 = QAction("Action 2", self)
#         action2.triggered.connect(self.action2_triggered)
#         menu.addAction(action2)

#         # Add a button to the toolbar that opens the dropdown menu
#         menu_button = QAction("File", self)
#         menu_button.triggered.connect(lambda: self._PopUp(menu, menu_button)) # open menu 
#         self.addAction(menu_button)
#         # menu.popup(self.mapToGlobal(self.actionGeometry(menu_button).bottomLeft()))

#     def _PopUp(self, tabtoopen, trigger):
#         return tabtoopen.popup(self.mapToGlobal(self.actionGeometry(trigger).bottomLeft()))

#     def action1_triggered(self):
#         print("Action 1 triggered")
        
#     def action2_triggered(self):
#         print("Action 2 triggered")

from PyQt6.QtWidgets import QToolBar, QMenu, QCheckBox, QComboBox, QWidgetAction
from PyQt6.QtGui import QAction
from PyQt6 import QtCore

class Toolbar(QToolBar):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # File menu
        file_menu = QMenu("File", self)
        new_action = QAction("New", self)
        save_action = QAction("Save", self)
        save_as_action = QAction("Save As", self)
        load_action = QAction("Load", self)
        render_action = QAction("Render", self)
        file_menu.addAction(new_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(load_action)
        file_menu.addAction(render_action)

        # Settings menu
        settings_menu = QMenu("Settings", self)
        example_checkbox = QCheckBox("Example Checkbox", self)
        settings_widget_action = QWidgetAction(self)
        settings_widget_action.setDefaultWidget(example_checkbox)
        settings_menu.addAction(settings_widget_action)

        # View menu
        view_menu = QMenu("View", self)
        
        # Create a submenu for buttons
        buttons_submenu = QMenu("Buttons", self)
        button1_action = QAction("Button 1", self)
        button2_action = QAction("Button 2", self)
        button3_action = QAction("Button 3", self)
        buttons_submenu.addAction(button1_action)
        buttons_submenu.addAction(button2_action)
        buttons_submenu.addAction(button3_action)
        
        # Add the submenu to the "View" menu
        view_menu.addMenu(buttons_submenu)

        # Add menus to the toolbar
        self.addAction(file_menu.menuAction())
        self.addAction(settings_menu.menuAction())
        self.addAction(view_menu.menuAction())

        # Connect actions
        new_action.triggered.connect(self.new_triggered)
        save_action.triggered.connect(self.save_triggered)
        save_as_action.triggered.connect(self.save_as_triggered)
        load_action.triggered.connect(self.load_triggered)
        render_action.triggered.connect(self.render_triggered)
        example_checkbox.toggled.connect(self.example_checkbox_toggled)
        button1_action.triggered.connect(self.button1_triggered)
        button2_action.triggered.connect(self.button2_triggered)
        button3_action.triggered.connect(self.button3_triggered)

    def new_triggered(self):
        print("New triggered")
        
    def save_triggered(self):
        print("Save triggered")

    def save_as_triggered(self):
        print("Save As triggered")

    def load_triggered(self):
        print("Load triggered")

    def render_triggered(self):
        print("Render triggered")

    def example_checkbox_toggled(self, checked):
        print(f"Example Checkbox toggled: {checked}")

    def button1_triggered(self):
        print("Button 1 clicked")

    def button2_triggered(self):
        print("Button 2 clicked")

    def button3_triggered(self):
        print("Button 3 clicked")