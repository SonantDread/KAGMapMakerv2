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
    def __init__(self) -> None:
        self.communicator = Communicator()
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
                width = re.sub(r"[^0-9]+", "", width)
                height = re.sub(r"[^0-9]+", "", height)

                width = abs(int(width))
                height = abs(int(height))
                canvas = self.communicator.get_canvas()
                canvas.resize_canvas(Vec2f(width, height))
                canvas.recenter_canvas()

            except ValueError:
                print("Invalid input. Width and height must be integers.")

        else:
            print("New map creation cancelled.")

    def save_map(self, fp: str = None, force_ask: bool = False) -> None:
        if self.communicator.last_saved_map_path is not None and not force_ask and fp is None:
            fp = self.communicator.last_saved_map_path

        if fp is None or fp == "" or force_ask:
            self.communicator.last_saved_map_path = None
            fp = self._ask_save_location()

        if fp is None or fp == "":
            return

        fp = fp.strip()

        canvas = self.communicator.get_canvas()
        tilemap = self._get_translated_tilemap(canvas.tilemap)
        sky = self.argb_to_rgba(self.item_list.get_item_by_name("sky").get_color())
        image = Image.new("RGBA", size=(canvas.size.x, canvas.size.y), color=sky)

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

                    print(f"Item not found: '{item.name_data.name}' | Unable to load in line {linenum} of {path} from mod: {item.mod_info.folder_name}")
                    continue

            offset_x, offset_y = item.pixel_data.offset
            width, height = canvas.size

            # clamp coords to map size
            final_x = min(max(pos.x + offset_x, 0), width - 1)
            final_y = min(max(pos.y + offset_y, 0), height - 1)

            image.putpixel((final_x, final_y), self.argb_to_rgba(color))

        try:
            image.save(fp)
            print(f"Map saved to: {fp}")
            self.communicator.last_saved_map_path = fp

        except FileNotFoundError as e:
            print(f"Failed to save image: {e}")

    def load_map(self, fp: str = "") -> None:
        if fp is None or fp == "":
            fp = self._ask_location("Load Map", self.file_handler.get_maps_path(), False)
            if fp is None or fp == "":
                print("Map to load not selected. Operation cancelled.")
                return

            # prevent crash
            if isinstance(fp, tuple) and len(fp) == 0:
                return None

            if isinstance(fp, tuple):
                fp = fp[0]

        if not self.file_handler.does_path_exist(fp):
            raise FileNotFoundError(f"File not found: {fp}")

        canvas = self.communicator.get_canvas()
        tilemap = Image.open(fp).convert("RGBA")

        width, height = tilemap.size

        new_tilemap = {}
        for x in range(width):
            for y in range(height):
                pixel = self.rgba_to_argb(tilemap.getpixel((x, y)))
                try: # todo: try to get rid of this try except block
                    item = self.item_list.get_item_by_color(pixel).copy()

                except:
                    continue

                name = item.name_data.name if item is not None else None

                # skip empty pixels
                if name == "sky" or name is None:
                    continue

                item.sprite.position = Vec2f(x, y)

                alpha = pixel[0]
                # team from alpha channel
                if item.pixel_data.team_from_alpha:
                    team = item.get_team_from_alpha(alpha)
                    item.swap_team(team)

                # angle from alpha channel
                if item.pixel_data.angle_from_alpha and item.sprite.properties.is_rotatable:
                    rotation = item.get_angle_from_alpha(alpha)
                    item.sprite.rotation = rotation

                # account for the saving offsets
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
        a, r, g, b = argb
        return (r, g, b, a)

    def rgba_to_argb(self, rgba: tuple) -> tuple:
        r, g, b, a = rgba
        return (a, r, g, b)

    def _ask_save_location(self) -> str:
        if self.communicator.last_saved_map_path is None:
            filepath = self._ask_location("Save Map As", self.file_handler.get_maps_path(), True)
            if filepath is None or filepath == "":
                print("Save location not selected. Operation cancelled.")
                return

            else:
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
                # add non-tree items directly to the new tilemap
                if item.name_data.name != "tree":
                    new_tilemap[pos] = item
                else:
                    # handle trees specially
                    x, y = pos

                    # find the lowest pixel of the tree (to place it properly)
                    while tilemap.get(Vec2f(x, y + 1)) is not None and tilemap.get(Vec2f(x, y + 1)).name_data.name == "tree":
                        y += 1

                    # add the bottom-most tree pixel
                    new_tilemap[Vec2f(x, y)] = tilemap[Vec2f(x, y)]

        return new_tilemap

class TwoInputDialog(QDialog): # todo: maybe this should be in a different file?
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
