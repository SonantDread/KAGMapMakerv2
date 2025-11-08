"""
Handles the conversion of formats between the map maker and KAG.
"""
import inspect
import os
from tkinter import filedialog
import re

from PIL import Image

from PyQt6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QDialog

from base.citemlist import CItemList
from core.communicator import Communicator
from utils.vec2f import Vec2f
from utils.file_handler import FileHandler

class KagImage:
    """
    Handles saving and loading maps.
    """
    def __init__(self) -> None:
        self.communicator = Communicator()
        self.item_list = CItemList()
        self.file_handler = FileHandler()

    def new_map(self) -> None:
        """
        Used to create a new map.
        """
        dialog = TwoInputDialog()
        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            print("New map creation cancelled.")

        width, height = dialog.get_inputs()
        try:
            width = re.sub(r"[^0-9]+", "", width)
            height = re.sub(r"[^0-9]+", "", height)

            width = abs(int(width))
            height = abs(int(height))
            canvas = self.communicator.get_canvas()
            canvas.resize_canvas(Vec2f(width, height))
            canvas.recenter_canvas()

        except ValueError:
            print("Invalid input. Width and height must be integers.")

    def save_map(self, fp: str = None, force_ask: bool = False) -> None:
        """
        Saves the map back to a PNG file.
        """
        if self.communicator.last_saved_map_path is not None and not force_ask and fp is None:
            fp = self.communicator.last_saved_map_path

        if fp is None or fp == "" or force_ask or isinstance(fp, bool):
            self.communicator.last_saved_map_path = None
            fp = self._ask_save_location()

        if fp is None or fp == "":
            return

        fp = fp.strip()

        canvas = self.communicator.get_canvas()
        tilemap = self._get_translated_tilemap(canvas.tilemap)
        sky = self.argb_to_rgba(self.item_list.get_item_by_name("sky").get_color())
        image = Image.new("RGBA", size=(canvas.map_size.x, canvas.map_size.y), color=sky)

        redbarrier_min_x, redbarrier_max_x = None, None

        for pos, item in tilemap.items():
            if item is None or pos is None:
                continue

            rotation = item.sprite.rotation
            team = item.sprite.team
            color = item.get_color(rotation, team)

            if color is None:
                color = item.get_color(rotation, team, True)
                if color is None:
                    linenum = inspect.currentframe().f_lineno
                    path = os.path.basename(__file__)

                    print(f"Item not found: '{item.name_data.name}' | Unable to load in line {linenum} of {path} (from mod: {item.mod_info.folder_name})")
                    continue

            offset_x, offset_y = item.pixel_data.offset
            width, height = canvas.map_size

            # clamp coords to map size
            final_x = min(max(pos.x + offset_x, 0), width - 1)
            final_y = min(max(pos.y + offset_y, 0), height - 1)

            color = self.argb_to_rgba(color)

            if item.name_data.name == "redbarrier":
                if redbarrier_min_x is None or final_x < redbarrier_min_x[0]:
                    redbarrier_min_x = (final_x, final_y)

                if redbarrier_max_x is None or final_x > redbarrier_max_x[0]:
                    redbarrier_max_x = (final_x, final_y)

                continue

            # save trees multiple blocks tall
            if item.name_data.name == "tree":
                for i in range(5):
                    pos = (final_x, final_y - i)
                    if self._is_out_of_bounds(pos):
                        break

                    if i != 0 and image.getpixel(pos) != sky:
                        break

                    image.putpixel(pos, color)

            else:
                image.putpixel((final_x, final_y), color)

        try:
            if redbarrier_min_x is not None and redbarrier_max_x is not None:
                barrier_color = self.argb_to_rgba(self.item_list.get_item_by_name("redbarrier").get_color())
                image.putpixel(redbarrier_min_x, barrier_color)
                image.putpixel(redbarrier_max_x, barrier_color)

            image.save(fp)
            print(f"Map saved to: {fp}")
            self.communicator.last_saved_map_path = fp

        except FileNotFoundError as e:
            print(f"Failed to save image: {e}")

    def load_map(self, fp: str = "") -> None:
        """
        Loads a map from a PNG file.
        """
        if fp is None or fp == "":
            fp = self._ask_location("Load Map", self.file_handler.get_maps_path(), False)
            if fp is None or fp == "":
                print("Map to load not selected. Operation cancelled.")
                return

        # prevent crash
        if isinstance(fp, tuple) and len(fp) == 0:
            return

        if isinstance(fp, tuple):
            fp = fp[0]

        if not self.file_handler.does_path_exist(fp):
            print(f"File not found: {fp}")
            return

        canvas = self.communicator.get_canvas()
        tilemap = Image.open(fp).convert("RGBA")

        width, height = tilemap.size

        new_tilemap = {}
        for x in range(width):
            for y in range(height):
                pixel = self.rgba_to_argb(tilemap.getpixel((x, y)))
                item = self.item_list.get_item_by_color(pixel)
                if item:
                    item = item.copy()

                else:
                    print(f"Invalid pixel: {pixel}")
                    continue

                name = item.name_data.name if item is not None else None

                if name == "sky" or name is None:
                    continue

                item.sprite.position = Vec2f(x, y)

                alpha = pixel[0]
                if item.pixel_data.team_from_alpha:
                    team = item.get_team_from_alpha(alpha)
                    item.swap_team(team)

                if item.pixel_data.angle_from_alpha and item.sprite.properties.is_rotatable:
                    rotation = item.get_angle_from_alpha(alpha)
                    item.sprite.rotation = rotation

                offset_x, offset_y = -item.pixel_data.offset

                # clamp coords to map size
                final_x = min(max(x + offset_x, 0), width - 1)
                final_y = min(max(y + offset_y, 0), height - 1)

                new_tilemap[Vec2f(final_x, final_y)] = item

        self.communicator.last_saved_map_path = fp

        new_tilemap = self._get_translated_tilemap(new_tilemap)
        canvas.resize_canvas(Vec2f(width, height), new_tilemap)
        canvas.recenter_canvas()

    def argb_to_rgba(self, argb: tuple) -> tuple:
        """
        Converts an ARGB tuple to an RGBA tuple.
        """
        a, r, g, b = argb
        return (r, g, b, a)

    def rgba_to_argb(self, rgba: tuple) -> tuple:
        """
        Converts an RGBA tuple to an ARGB tuple.
        """
        r, g, b, a = rgba
        return (a, r, g, b)

    def _ask_save_location(self) -> str:
        if self.communicator.last_saved_map_path is None:
            filepath = self._ask_location("Save Map As", self.file_handler.get_maps_path(), True)
            if filepath is None or filepath == "":
                print("Save location not selected. Operation cancelled.")
                return

            self.communicator.last_saved_map_path = filepath

        else:
            filepath = self.communicator.last_saved_map_path

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
    def _get_translated_tilemap(self, tilemap: dict) -> dict:
        if tilemap is None:
            print(f"Failed to get tilemap in kag_image.py: {inspect.currentframe().f_lineno}")
            return None

        new_tilemap = {}
        for pos, item in tilemap.items():
            if item is not None and pos is not None:
                if item.name_data.name != "tree":
                    new_tilemap[pos] = item

                else:
                    x, y = pos

                    # find the lowest pixel of the tree
                    tile = Vec2f(x, y + 1)
                    while tilemap.get(tile) is not None and tilemap.get(tile).name_data.name == "tree":
                        y += 1
                        tile.y += 1

                    pos = Vec2f(x, y)
                    new_tilemap[pos] = tilemap[pos]

        return new_tilemap

    def _is_out_of_bounds(self, pos: tuple) -> bool:
        x, y = pos
        size: Vec2f = self.communicator.get_canvas().map_size
        return x < 0 or y < 0 or x >= size.x or y >= size.y

class TwoInputDialog(QDialog):
    """
    Used as the input box for the new map size.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("New Map")
        self.setFixedSize(300, 150)

        width_label = QLabel("Width:")
        height_label = QLabel("Height:")
        self.width_input = QLineEdit()
        self.height_input = QLineEdit()
        ok_button = QPushButton("Continue")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

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
        """
        return (self.width_input.text(), self.height_input.text())
