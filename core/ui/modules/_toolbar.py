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
        # file menu
        _file_menu = QMenu("File", self)
        _new_action = QAction("New", self)
        _save_action = QAction("Save", self)
        _save_as_action = QAction("Save As", self)
        _load_action = QAction("Load", self)
        _render_action = QAction("Render", self)
        _file_menu.addAction(_new_action)
        _file_menu.addAction(_save_action)
        _file_menu.addAction(_save_as_action)
        _file_menu.addAction(_load_action)
        _file_menu.addAction(_render_action)

        # settings menu
        _settings_menu = QMenu("Settings", self)
        _example_checkbox = QCheckBox("Example Checkbox", self)
        _settings_widget_action = QWidgetAction(self)
        _settings_widget_action.setDefaultWidget(_example_checkbox)
        _settings_menu.addAction(_settings_widget_action)

        # view menu
        _view_menu = QMenu("View", self)
        
        # create a submenu for buttons
        _buttons_submenu = QMenu("Buttons", self)
        _button1_action = QAction("Button 1", self)
        _button2_action = QAction("Button 2", self)
        _button3_action = QAction("Button 3", self)
        _buttons_submenu.addAction(_button1_action)
        _buttons_submenu.addAction(_button2_action)
        _buttons_submenu.addAction(_button3_action)
        
        # add the submenu to the 'View' menu
        _view_menu.addMenu(_buttons_submenu)

        # connect actions to functions
        _new_action.triggered.connect(self.new_triggered)
        _save_action.triggered.connect(self.save_triggered)
        _save_as_action.triggered.connect(self.save_as_triggered)
        _load_action.triggered.connect(self.load_triggered)
        _render_action.triggered.connect(self.render_triggered)
        _example_checkbox.toggled.connect(self.example_checkbox_toggled)
        _button1_action.triggered.connect(self.button1_triggered)
        _button2_action.triggered.connect(self.button2_triggered)
        _button3_action.triggered.connect(self.button3_triggered)

        # add File menu to toolbar
        self.file_menu = QAction("File", self)
        self.file_menu.triggered.connect(lambda: self._PopUp(_file_menu, self.file_menu))
        self.addAction(self.file_menu)

        # add Settings menu to toolbar
        self.settings_menu = QAction("Settings", self)
        self.settings_menu.triggered.connect(lambda: self._PopUp(_settings_menu, self.settings_menu))
        self.addAction(self.settings_menu)

        # add View menu to toolbar
        self.view_menu = QAction("View", self)
        self.view_menu.triggered.connect(lambda: self._PopUp(_view_menu, self.view_menu))
        self.addAction(self.view_menu)

    def _PopUp(self, tabtoopen, trigger):
        return tabtoopen.popup(self.mapToGlobal(self.actionGeometry(trigger).bottomLeft()))

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