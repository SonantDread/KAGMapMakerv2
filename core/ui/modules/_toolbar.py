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

from PyQt6.QtWidgets import QToolBar, QMenu, QCheckBox, QComboBox
from PyQt6.QtGui import QAction
from PyQt6 import QtCore

class Toolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # File tab
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

        # Settings tab
        settings_menu = QMenu("Settings", self)
        example_checkbox = QCheckBox("Example Checkbox", self)
        settings_menu.addAction(example_checkbox)

        # View tab
        view_menu = QMenu("View", self)
        example_dropdown = QComboBox(self)
        example_dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        view_menu_action = view_menu.menuAction()
        self.addAction(view_menu_action)

        # Add tabs to the toolbar
        self.addMenu(file_menu)
        self.addMenu(settings_menu)

        # Connect actions
        new_action.triggered.connect(self.new_triggered)
        save_action.triggered.connect(self.save_triggered)
        save_as_action.triggered.connect(self.save_as_triggered)
        load_action.triggered.connect(self.load_triggered)
        render_action.triggered.connect(self.render_triggered)
        example_checkbox.toggled.connect(self.example_checkbox_toggled)
        example_dropdown.currentIndexChanged.connect(self.example_dropdown_changed)

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

    def example_dropdown_changed(self, index):
        print(f"Example Dropdown changed to index {index}")