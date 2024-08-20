"""
Used to handle saving, loading, rendering and testing maps in KAG.
"""

import inspect
import json
import os
import re
from tkinter import filedialog
from typing import Union

from PIL import Image

from base.cblob import CBlob
from base.ctile import CTile
from base.ctile_list import CTileList
from base.image_handler import ImageHandler
from base.kag_color import KagColor
from core.scripts.communicator import Communicator
from utils.vec import vec

# TODO: update config handling instead of having this file handle some config
# TODO: have a better way of handling filepaths
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

    def save_map(self, filepath: str = None, force_ask: bool = False):
        """
        Saves a KAG map to a file.

        Args:
            filepath (str): The path where the map will be saved, asks the user if not specified.
            force_ask (bool): If True, the function will always ask for a save location.

        Returns:
            None
        """
        if filepath is None or filepath is "" or force_ask:
            filepath = self._ask_save_location()

        canvas = self._get_canvas()
        tilemap = canvas.get_tilemap()
        colors = self.colors.vanilla_colors

        sky = self.argb_to_rgba(colors.get("sky"))
        image = Image.new("RGBA", size = canvas.get_size(), color = sky)

        for x, row in enumerate(tilemap):
            for y, tile in enumerate(row):
                if tile is None:
                    continue
                # TODO: should take into account for teams when they are added
                name = tile.name
                argb = colors.get(name)

                if argb is None:
                    linenum = inspect.currentframe().f_lineno
                    path = os.path.basename(__file__)
                    print(f"Item not found: {name} | Unable to load in line {linenum} of {path}")
                    continue

                image.putpixel((x, y), self.argb_to_rgba(argb))

        try:
            image.save(filepath)
            print(f"Image saved to: {filepath}")
            self.last_saved_location = filepath

        except FileNotFoundError as e:
            print(f"Failed to save image: {e}")

    def save_map_as(self):
        """
        Saves a KAG map to a file, always asking for a save location.

        Args:
            None

        Returns:
            None
        """
        self.save_map(force_ask = True)

    def load_map(self):
        """
        Loads a KAG map from a file.

        Args:
            None

        Returns:
            None
        """
        # todo: 2nd arg should be to maps folder
        filepath = self._ask_location("Load Map", self._get_kag_path(), False)
        if filepath is None or filepath == "":
            print("Map to load not selected. Operation cancelled.")
            return

        if isinstance(filepath, tuple):
            filepath = filepath[0]

        canvas = self._get_canvas()
        tilemap = Image.open(filepath).convert("RGBA")
        rev_lookup = self.colors.vanilla_colors
        rev_lookup = {v: k for k, v in rev_lookup.items()}

        width, height = tilemap.size

        new_tilemap = [[None for _ in range(height)] for _ in range(width)]
        for x in range(width):
            for y in range(height):
                pixel = self.rgba_to_argb(tilemap.getpixel((x, y)))
                name = rev_lookup.get(pixel)

                if name == "sky" or name is None:
                    continue # cant do anything so ignore

                pos = (x, y)

                item = self.__make_class(name, pos)
                print(f"Original name: {name} | Name: {item.name}")
                new_tilemap[x][y] = item

        canvas.size = (width, height)
        canvas.tilemap = new_tilemap
        canvas.force_rerender()

    def __make_class(self, name: str, pos: tuple) -> Union[CTile, CBlob]:
        raw_name = self._get_raw_name(name)
        img = self.images.get_image(raw_name)
        team = self._get_team(name)

        # check if we should return CTile
        if self.tilelist.does_tile_exist(name):
            return CTile(img, raw_name, vec(pos[0], pos[1]), 0)
        return CBlob(img, raw_name, vec(pos[0], pos[1]), 0, team)

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
        path = 'settings/config.json'

        try:
            with open(path, 'r', encoding = 'utf-8') as json_file:
                data = json.load(json_file)

                kag_path = data['kag_path']
                return kag_path

        except FileNotFoundError:
            print(f"Could not find {path}")

        return None

    def _ask_save_location(self) -> str:
        if self.last_saved_location is None: # todo: 2nd arg should be to maps folder
            filepath = self._ask_location("Save Map As", self._get_kag_path(), True)
            if filepath is None or filepath == "":
                print("Save location not selected. Operation cancelled.")
                return
        else:
            filepath = self.last_saved_location

        if isinstance(filepath, tuple):
            filepath = filepath[0]

        return str(filepath)
