"""
The toolbar for the file, settings and view.
"""

import os
import shutil
import subprocess

from tkinter import filedialog

from PyQt6.QtWidgets import QToolBar, QMenu, QCheckBox, QWidgetAction
from PyQt6.QtGui import QAction

from base.kag_image import KagImage
from core.communicator import Communicator
from utils.config_handler import ConfigHandler
from utils.file_handler import FileHandler

class Toolbar(QToolBar):
    """
    The toolbar for the program.
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setParent(parent)
        self.kagimage = KagImage()
        self.communicator = Communicator()
        self.setup_ui()

    def setup_ui(self) -> None:
        """
        Sets up the UI for the toolbar, including the file, settings, and view menus.
        This function creates the menu actions, adds them to their respective menus,
        and connects the actions to their corresponding functions.
        """
        file_menu = QMenu("File", self)
        new_action = QAction("New", self)
        save_action = QAction("Save", self)
        save_as_action = QAction("Save As", self)
        load_action = QAction("Load", self)
        test_in_kag = QAction("Test in KAG", self)

        new_action.triggered.connect(self.kagimage.new_map)
        save_action.triggered.connect(self.kagimage.save_map)
        save_as_action.triggered.connect(lambda: self.kagimage.save_map(force_ask=True))
        load_action.triggered.connect(lambda: self.kagimage.load_map())
        test_in_kag.triggered.connect(self.test_in_kag_triggered)

        file_menu.addAction(new_action)
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        file_menu.addAction(test_in_kag)

        settings_menu = QMenu("Settings", self)
        self.mirror_x = self._add_checkbox(settings_menu, "Mirror Over X-Axis", self.toggle_mirrored_x)

        view_menu = QMenu("View", self)
        self.tilegrid_visible = self._add_checkbox(view_menu, "Show Grid", self.toggle_grid)
        self.redbarrier_visible = self._add_checkbox(view_menu, "Show Red Barrier", self.toggle_redbarrier)
        self.redbarrier_visible = self._add_checkbox(view_menu, "Show Non-Mineable Edge Blocks", self.toggle_edge_blocks)
        # view_menu.addSeparator()

        # buttons_submenu = QMenu("Buttons", self)
        # button1_action = QAction("Button 1", self)
        # button2_action = QAction("Button 2", self)
        # button3_action = QAction("Button 3", self)

        # button1_action.triggered.connect(self.button1_triggered)
        # button2_action.triggered.connect(self.button2_triggered)
        # button3_action.triggered.connect(self.button3_triggered)

        # buttons_submenu.addAction(button1_action)
        # buttons_submenu.addAction(button2_action)
        # buttons_submenu.addAction(button3_action)

        # view_menu.addMenu(buttons_submenu)

        self.file_menu = QAction("File", self)
        self.file_menu.triggered.connect(lambda: self._pop_up(file_menu, self.file_menu))
        self.addAction(self.file_menu)

        self.settings_menu = QAction("Settings", self)
        self.settings_menu.triggered.connect(lambda: self._pop_up(settings_menu, self.settings_menu))
        self.addAction(self.settings_menu)

        self.view_menu = QAction("View", self)
        self.view_menu.triggered.connect(lambda: self._pop_up(view_menu, self.view_menu))
        self.addAction(self.view_menu)

    def _pop_up(self, tabtoopen, trigger):
        return tabtoopen.popup(self.mapToGlobal(self.actionGeometry(trigger).bottomLeft()))

    def _add_checkbox(self, menu: QMenu, text: str, action) -> QCheckBox:
        box = QCheckBox(text, self)
        action_widget = QWidgetAction(self)
        action_widget.setDefaultWidget(box)
        menu.addAction(action_widget)
        box.toggled.connect(action)

        return box

    def toggle_mirrored_x(self, checked: bool) -> None:
        """
        Toggles the mirrored over x setting based on checkbox state.
        """
        self.communicator.settings['mirrored over x'] = checked

    def toggle_grid(self, checked: bool) -> None:
        """
        Toggle's the canvas's grid visibility.
        """
        self.communicator.get_canvas().set_grid_visible(checked)

    def toggle_redbarrier(self, checked: bool) -> None:
        """
        Toggle's the canvas's red barrier visibility.
        """
        self.communicator.view["redbarrier"] = checked

        overlays = self.communicator.get_canvas().renderer.render_overlays
        overlays.render_extra_overlay() # force update

    def toggle_edge_blocks(self, checked: bool) -> None:
        """
        Toggle's the visibility of the canvas's nobuild area on the edges of the map.
        """
        self.communicator.view["nobuild_edges"] = checked

        overlays = self.communicator.get_canvas().renderer.render_overlays
        overlays.render_extra_overlay() # force update

    def test_in_kag_triggered(self):
        """
        Opens KAG to test the current map on the canvas.
        """
        fh = FileHandler()
        config_handler = ConfigHandler()
        config_handler.load_config_file(config_handler.config_path, "config.json")
        kag_base_path = config_handler.get_config_item("config.json", "kag_path")

        if kag_base_path is None or kag_base_path == "":
            config_handler.load_config_file(config_handler.readonly_config_path, "config.json")
            kag_base_path = config_handler.get_config_item("readonly_config.json", "kag_path")

        if kag_base_path is None or kag_base_path == "":
            kag_base_path = self.ask_kag_path()
            kag_base_path = os.path.dirname(kag_base_path) if kag_base_path is not None else None

        if kag_base_path is None or kag_base_path == "":
            return

        kag_script_path = fh.get_kag_autostart_path(kag_base_path)
        kag_map_path = fh.get_kag_maps_path(kag_base_path)
        autostart_script = fh.paths.get("autostart_script_path")

        if fh.does_path_exist(autostart_script) and not fh.does_path_exist(kag_script_path):
            shutil.copy(autostart_script, kag_script_path)

        if fh.does_path_exist(kag_base_path):
            self.kagimage.save_map(kag_map_path)

        try:
            kag_executable = os.path.join(kag_base_path, "KAG")
            # windows
            if os.name == "nt":
                kag_executable += ".exe"

            command = [
                kag_executable,
                "autostart",
                "Scripts/MapMaker_Autostart.as",
                "noautoupdate",
                "nolauncher"
            ]
            subprocess.Popen(command, cwd = kag_base_path)

        except subprocess.CalledProcessError as e:
            print(f"Error executing KAG command: {e}")

    def ask_kag_path(self) -> str | None:
        """
        Asks the user to provide the path to their KAG installation.

        Returns:
            str | None: The path to the KAG installation, or None if the user cancels.
        """
        filepath = filedialog.askopenfilename(
            title = "Please open your KAG executable.",
            defaultextension = ".exe",
            filetypes = [("Executeable Files", "*.exe")]
        )

        return filepath

    # def example_checkbox_toggled(self, checked):
    #     print(f"Example Checkbox toggled: {checked}")

    # def button1_triggered(self):
    #     print("Button 1 clicked")

    # def button2_triggered(self):
    #     print("Button 2 clicked")

    # def button3_triggered(self):
    #     print("Button 3 clicked")
