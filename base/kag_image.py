import inspect
import os
from tkinter import filedialog

from PIL import Image

from PyQt6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QDialog

from base.citemlist import CItemList
from core.communicator import Communicator
from utils.vec2f import Vec2f
from utils.file_handler import FileHandler

class KagImage:
    def __init__(self) -> None:
        self.communicator = Communicator()
        self.last_saved_location = None
        self.item_list = CItemList()
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
                width = abs(int(width.strip()))
                height = abs(int(height.strip()))
                canvas = self.communicator.get_canvas()
                canvas.resize(Vec2f(width, height))

            except ValueError:
                print("Invalid input. Width and height must be integers.")
        else:
            print("New map creation cancelled.")

    def save_map(self, fp: str = None, force_ask: bool = False) -> None:
        if fp is None or fp == "" or force_ask:
            self.last_saved_location = None
            fp = self._ask_save_location()

        if fp is None or fp == "":
            print("Save location not selected. Operation cancelled.")
            return

        fp = fp.strip()

        canvas = self.communicator.get_canvas()
        tilemap = self._get_translated_tilemap(canvas.tilemap)
        sky = self.argb_to_rgba(self.item_list.get_item_by_name("sky").get_color())
        image = Image.new("RGBA", size=(canvas.size.x, canvas.size.y), color=sky)

        for x, row in enumerate(tilemap):
            for y, item in enumerate(row):
                if item is None:
                    continue

                rotation = item.sprite.rotation
                team = item.sprite.team

                color = item.get_color(rotation, team)
                if color is None:
                    color = item.get_color(rotation, team, True)
                    if color is None:
                        linenum = inspect.currentframe().f_lineno
                        path = os.path.basename(__file__)
                        # todo: should be 'raise' but we dont have all the sprites yet
                        print(f"Item not found: '{item.name_data.name}' | Unable to load in line {linenum} of {path} from mod: {item.mod_info.folder_name}")
                        continue

                offset_x, offset_y = item.pixel_data.offset
                width, height = canvas.size

                # clamp coords to map size
                final_x = min(max(x + offset_x, 0), width - 1)
                final_y = min(max(y + offset_y, 0), height - 1)

                image.putpixel((final_x, final_y), self.argb_to_rgba(color))

        try:
            image.save(fp)
            print(f"Map saved to: {fp}")
            self.last_saved_location = fp

        except FileNotFoundError as e:
            print(f"Failed to save image: {e}")

    def load_map(self) -> None:
        fp = self._ask_location("Load Map", self.file_handler.get_maps_path(), False)
        if fp is None or fp == "":
            print("Map to load not selected. Operation cancelled.")
            return

        if isinstance(fp, tuple):
            fp = fp[0]

        if not self.file_handler.does_path_exist(fp):
            raise FileNotFoundError(f"File not found: {fp}")

        canvas = self.communicator.get_canvas()
        tilemap = Image.open(fp).convert("RGBA")

        width, height = tilemap.size

        new_tilemap = [[None for _ in range(height)] for _ in range(width)]
        for x in range(width):
            for y in range(height):
                pixel = self.rgba_to_argb(tilemap.getpixel((x, y)))
                item = self.item_list.get_item_by_color(pixel)
                name = item.name_data.name if item is not None else None

                if name == "sky" or name is None:
                    continue # cant do anything so ignore

                item.sprite.position = Vec2f(x, y)

                # account for the saving offsets
                offset_x, offset_y = -item.pixel_data.offset

                # clamp coords to map size
                final_x = min(max(x + offset_x, 0), width - 1)
                final_y = min(max(y + offset_y, 0), height - 1)

                new_tilemap[final_x][final_y] = item

        new_tilemap = self._get_translated_tilemap(new_tilemap)

        self._resize_canvas(Vec2f(width, height), canvas, new_tilemap)

    def _resize_canvas(self, size: Vec2f, canvas, new_tilemap) -> None:
        width, height = size.x, size.y

        canvas.size = Vec2f(width, height)
        canvas.tilemap = new_tilemap
        canvas.force_rerender()

    def argb_to_rgba(self, argb: tuple) -> tuple:
        a, r, g, b = argb
        return (r, g, b, a)

    def rgba_to_argb(self, rgba: tuple) -> tuple:
        r, g, b, a = rgba
        return (a, r, g, b)

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

    # required because trees can be multiple blocks tall
    def _get_translated_tilemap(self, tilemap: list) -> list:
        if tilemap is None:
            print(f"Failed to get tilemap in kag_image.py: {inspect.currentframe().f_lineno}")
            return None

        newmap = []
        for column in tilemap:
            new_column = []
            tree_group = []

            for pixel in column:
                if pixel is not None and pixel.name_data.name == "tree":
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
