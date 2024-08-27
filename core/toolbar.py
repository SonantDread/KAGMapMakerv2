"""
The toolbar for the file, settings, view, etc.
"""

from PyQt6.QtWidgets import QToolBar, QMenu, QCheckBox, QWidgetAction
from PyQt6.QtGui import QAction

from base.kag_image import KagImage

class Toolbar(QToolBar):
    """
    The toolbar for the program.
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setParent(parent)
        self.kagimage = KagImage()
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the UI for the toolbar, including the file, settings, and view menus.
        This function creates the menu actions, adds them to their respective menus,
        and connects the actions to their corresponding functions.

        Parameters:
            None

        Returns:
            None
        """
        # file menu
        file_menu = QMenu("File", self)
        new_action = QAction("New", self)
        save_action = QAction("Save", self)
        save_as_action = QAction("Save As", self)
        load_action = QAction("Load", self)
        render_action = QAction("Render", self)
        test_in_kag = QAction("Test in KAG", self)
        file_menu.addAction(new_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(load_action)
        file_menu.addAction(render_action)
        file_menu.addAction(test_in_kag)

        # settings menu
        settings_menu = QMenu("Settings", self)
        example_checkbox = QCheckBox("Example Checkbox", self)
        settings_widget_action = QWidgetAction(self)
        settings_widget_action.setDefaultWidget(example_checkbox)
        settings_menu.addAction(settings_widget_action)

        # view menu
        view_menu = QMenu("View", self)

        # create a submenu for buttons
        buttons_submenu = QMenu("Buttons", self)
        button1_action = QAction("Button 1", self)
        button2_action = QAction("Button 2", self)
        button3_action = QAction("Button 3", self)
        buttons_submenu.addAction(button1_action)
        buttons_submenu.addAction(button2_action)
        buttons_submenu.addAction(button3_action)

        # add the submenu to the 'View' menu
        view_menu.addMenu(buttons_submenu)

        # connect actions to functions
        new_action.triggered.connect(self.new_triggered)
        save_action.triggered.connect(self.save_triggered)
        save_as_action.triggered.connect(self.save_as_triggered)
        load_action.triggered.connect(self.load_triggered)
        render_action.triggered.connect(self.render_triggered)
        example_checkbox.toggled.connect(self.example_checkbox_toggled)
        button1_action.triggered.connect(self.button1_triggered)
        button2_action.triggered.connect(self.button2_triggered)
        button3_action.triggered.connect(self.button3_triggered)
        test_in_kag.triggered.connect(self.test_in_kag_triggered)

        # add File menu to toolbar
        self.file_menu = QAction("File", self)
        self.file_menu.triggered.connect(lambda: self._pop_up(file_menu, self.file_menu))
        self.addAction(self.file_menu)

        # add Settings menu to toolbar
        self.settings_menu = QAction("Settings", self)
        self.settings_menu.triggered.connect(lambda: self._pop_up(settings_menu, self.settings_menu))
        self.addAction(self.settings_menu)

        # add View menu to toolbar
        self.view_menu = QAction("View", self)
        self.view_menu.triggered.connect(lambda: self._pop_up(view_menu, self.view_menu))
        self.addAction(self.view_menu)

    def _pop_up(self, tabtoopen, trigger):
        return tabtoopen.popup(self.mapToGlobal(self.actionGeometry(trigger).bottomLeft()))

    def new_triggered(self):
        print("New triggered")

    def save_triggered(self):
        print("Save triggered")
        self.kagimage.save_map()

    def save_as_triggered(self):
        print("Save As triggered")
        self.kagimage.save_map_as()

    def load_triggered(self):
        self.kagimage.load_map()

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

    def test_in_kag_triggered(self):
        print("Test in kag clicked")
