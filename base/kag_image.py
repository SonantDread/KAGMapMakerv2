"""
Used to handle creating, saving, loading, rendering and testing maps in KAG.
"""

import inspect
import os
import re
from tkinter import filedialog
from typing import Union

from PIL import Image

from PyQt6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QDialog

from base.cblob import CBlob
from base.ctile import CTile
from base.ctile_list import CTileList
from base.image_handler import ImageHandler
from base.kag_color import KagColor
from core.communicator import Communicator
from utils.vec2f import Vec2f
from utils.file_handler import FileHandler
from utils.config_handler import ConfigHandler

class KagImage:
    """
    Handles saving, loading, rendering and testing maps in KAG.
    """
    def __init__(self):
        self.colors = KagColor()
        self.communicator = Communicator()
        self.last_saved_location = None
        self.tilelist = CTileList()
        self.images = ImageHandler()
        self.file_handler = FileHandler()

    def new_map(self) -> None:
        """
        Used to create a new KAG map.
        
        Args:
            None

        Returns:
            None
        """
        dialog = TwoInputDialog()
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            width, height = dialog.get_inputs()
            try:
                width = int(width)
                height = int(height)
                self._create_new_map(width, height)

            except ValueError:
                print("Invalid input. Width and height must be integers.")
        else:
            print("New map creation cancelled.")

    def _create_new_map(self, width: int, height: int) -> None:
        canvas = self._get_canvas()
        new_tilemap = [[None for _ in range(height)] for _ in range(width)]
        self._resize_canvas(Vec2f(width, height), canvas, new_tilemap)
        print(f"New map created with dimensions: {width}x{height}")

    def save_map(self, filepath: str = None, force_ask: bool = False) -> None:
        """
        Saves a KAG map to a file.

        Args:
            filepath (str): The path where the map will be saved, asks the user if not specified.
            force_ask (bool): If True, the function will always ask for a save location.

        Returns:
            None
        """
        if filepath is None or filepath == "" or force_ask:
            filepath = self._ask_save_location()

        canvas = self._get_canvas()
        tilemap = canvas.get_tilemap()
        tilemap = self.__get_translated_tilemap(tilemap)

        sky = self.argb_to_rgba(self.colors.get_color_by_name("sky"))
        image = Image.new("RGBA", size = (canvas.get_size().x, canvas.get_size().y), color = sky)

        for x, row in enumerate(tilemap):
            for y, tile in enumerate(row):
                if tile is None:
                    continue
                # TODO: should take into account for teams when they are added
                name = tile.name
                argb = self.colors.get_color_by_name(name)

                if argb is None:
                    linenum = inspect.currentframe().f_lineno
                    path = os.path.basename(__file__)
                    print(f"Item not found: '{name}' | Unable to load in line {linenum} of {path}")
                    continue

                image.putpixel((x, y), self.argb_to_rgba(argb))

        try:
            image.save(filepath)
            print(f"Map saved to: {filepath}")
            self.last_saved_location = filepath

        except FileNotFoundError as e:
            print(f"Failed to save image: {e}")

    def save_map_as(self) -> None:
        """
        Saves a KAG map to a file, always asking for a save location.

        Args:
            None

        Returns:
            None
        """
        self.save_map(force_ask = True)

    def load_map(self) -> None:
        """
        Loads a KAG map from a file.

        Args:
            None

        Returns:
            None
        """
        filepath = self._ask_location("Load Map", self.file_handler.get_maps_path(), False)
        if filepath is None or filepath == "":
            print("Map to load not selected. Operation cancelled.")
            return

        if isinstance(filepath, tuple):
            filepath = filepath[0]

        if not self.file_handler.does_path_exist(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        canvas = self._get_canvas()
        tilemap = Image.open(filepath).convert("RGBA")

        width, height = tilemap.size

        new_tilemap = [[None for _ in range(height)] for _ in range(width)]
        for x in range(width):
            for y in range(height):
                pixel = self.rgba_to_argb(tilemap.getpixel((x, y)))
                name = self.colors.get_name_by_color(pixel) # TODO: for map saving and loading, implement rotation

                if name == "sky" or name is None:
                    continue # cant do anything so ignore

                pos = (x, y)

                item = self.__make_class(name, pos)
                print(f"Original name: {name} | Name: {item.name}")
                new_tilemap[x][y] = item

        new_tilemap = self.__get_translated_tilemap(new_tilemap)

        self._resize_canvas(Vec2f(width, height), canvas, new_tilemap)

    def _resize_canvas(self, size: Vec2f, canvas, new_tilemap) -> None:
        width, height = size.x, size.y

        canvas.size = Vec2f(width, height)
        canvas.tilemap = new_tilemap
        canvas.force_rerender()

    def __make_class(self, name: str, pos: tuple) -> Union[CTile, CBlob]:
        raw_name = self._get_raw_name(name)
        img = self.images.get_image(raw_name)
        team = self._get_team(name)
        rotation = self._get_canvas().rotation

        if self.tilelist.does_tile_exist(name):
            return CTile(img, raw_name, Vec2f(pos[0], pos[1]), 0)
        return CBlob(img, raw_name, Vec2f(pos[0], pos[1]), 0, team, r = rotation)

    def argb_to_rgba(self, argb: tuple) -> tuple:
        """
        Converts an ARGB color tuple to an RGBA color tuple.

        Parameters:
            argb (tuple): The ARGB color tuple to be converted.

        Returns:
            tuple: The RGBA color tuple.
        """
        a, r, g, b = argb
        return (r, g, b, a)

    def rgba_to_argb(self, rgba: tuple) -> tuple:
        """
        Converts an RGBA color tuple to an ARGB color tuple.

        Parameters:
            rgba (tuple): The RGBA color tuple to be converted.

        Returns:
            tuple: The ARGB color tuple.
        """
        r, g, b, a = rgba
        return (a, r, g, b)

    def _get_raw_name(self, name: str) -> str:
        if not name:
            return None

        # handle rotation
        for suffix in ["_r0", "_r90", "_r180", "_r270"]:
            if name.endswith(suffix):
                name = name[:-len(suffix)]

        pattern = r"_\-?([0-7]|-1)$"
        return re.sub(pattern, "", name)

    def _get_team(self, name: str) -> int:
        pattern = r"_\-?([0-7]|-1)$"
        matched = re.match(pattern, name)

        if matched is None:
            return None

        return int(matched.group(1))

    def _get_canvas(self):
        return self.communicator.get_canvas()

    def _ask_location(self, text: str, initialdir: str, saving_map: bool) -> str:
        if saving_map:
            file_path = filedialog.asksaveasfilename(
                title = text,
                defaultextension = ".png",
                filetypes = [("PNG files", "*.png")],
                initialdir = initialdir
            )
        else:
            file_path = filedialog.askopenfilename(
                title = text,
                defaultextension = ".png",
                filetypes = [("PNG files", "*.png")],
                initialdir = initialdir
            )

        if file_path is None or file_path == "":
            return None

        return file_path

    def _get_kag_path(self) -> str:
        path = ConfigHandler().get_config_item("kag_path")

        return str(path)

    def _ask_save_location(self) -> str:
        if self.last_saved_location is None:
            filepath = self._ask_location("Save Map As", self.file_handler.get_maps_path(), True)
            if filepath is None or filepath == "":
                print("Save location not selected. Operation cancelled.")
                return
        else:
            filepath = self.last_saved_location

        if isinstance(filepath, tuple):
            filepath = filepath[0]

        return str(filepath)

    # required because trees can be multiple blocks tall
    def __get_translated_tilemap(self, tilemap: list) -> list:
        if tilemap is None:
            print(f"Failed to get tilemap in kag_image.py: {inspect.currentframe().f_lineno}")
            return None

        newmap = []
        for column in tilemap:
            new_column = []
            tree_group = []

            for pixel in column:
                if pixel is not None and pixel.name == "tree":
                    tree_group.append(pixel)
                else:
                    if tree_group:
                        new_column.extend([None] * (len(tree_group) - 1))
                        new_column.append(tree_group[-1])
                        tree_group = []
                    new_column.append(pixel)

            if tree_group:
                new_column.extend([None] * (len(tree_group) - 1))
                new_column.append(tree_group[-1])

            newmap.append(new_column)

        return newmap

class TwoInputDialog(QDialog):
    """
    Used as the input box for the new map size.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("New Map")
        self.setFixedSize(300, 150)

        # create widgets
        width_label = QLabel("Width:")
        height_label = QLabel("Height:")
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        ok_button = QPushButton("Continue")
        cancel_button = QPushButton("Cancel")

        # connect buttons to signals
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        # create layout
        width_layout = QHBoxLayout()
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_input)

        height_layout = QHBoxLayout()
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(width_layout)
        main_layout.addLayout(height_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_inputs(self):
        """
        Retrieves the text input from the width and height input fields
        and returns them as a tuple of strings.

        Returns:
            tuple: A tuple containing the text from the width input field
            and the text from the height input field.
        """
        return (self.width_input.text(), self.height_input.text())
