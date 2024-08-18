# handles saving, loading, rendering and testing maps in kag
from base.KagColor import KagColor
from core.scripts.Communicator import Communicator
from PIL import Image
from tkinter import filedialog
from base.CBlob import CBlob
from base.CTile import CTile
from base.CTileList import CTileList
from base.ImageHandler import ImageHandler
from typing import Union
import json
import re
import inspect
import os
from utils.vec import vec
# TODO: update config handling instead of having this file handle some config
class KagImage:
    def __init__(self):
        self.colors = KagColor()
        self.communicator = Communicator()
        self.last_saved_location = None
        self.tilelist = CTileList()
        self.images = ImageHandler()

    def save_map(self, force_ask = False):
        if self.last_saved_location is None or force_ask:
            filepath = self._ask_location("Save Map As", self._get_kag_path(), True) # todo: 2nd arg should be to maps folder
            if filepath is None or filepath == "":
                print("Save location not selected. Operation cancelled.")
                return
        else:
            filepath = self.last_saved_location
            
        if isinstance(filepath, tuple):
            filepath = filepath[0]

        canvas = self._get_canvas()
        tilemap = canvas.get_tilemap()
        colors = self.colors.vanilla_colors

        image = Image.new("RGBA", size = canvas.get_size(), color = self.argb_to_rgba(colors.get("sky")))

        for x in range(len(tilemap)):
            for y in range(len(tilemap[x])):
                if tilemap[x][y] is None:
                    continue
                # TODO: should take into account for teams when they are added
                name = tilemap[x][y].name
                argb = colors.get(name)

                if argb is None:
                    print(f"Item not found: {name}. Unable to load in line {inspect.currentframe().f_lineno} of {os.path.basename(__file__)}")
                    continue

                image.putpixel((x, y), self.argb_to_rgba(argb))

        try:
            image.save(filepath)
            print(f"Image saved to: {filepath}")
            self.last_saved_location = filepath

        except Exception as e:
            print(f"Failed to save image: {e}")

    def save_map_as(self):
        self.save_map(True)
        
    def load_map(self):
        filepath = self._ask_location("Load Map", self._get_kag_path(), False) # todo: 2nd arg should be to maps folder
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
        img = self.images.getImage(raw_name)
        team = self._get_team(name)
        
        # check if we should return CTile
        if self.tilelist.does_tile_exist(name):
            return CTile(img, raw_name, vec(pos[0], pos[1]), 0)
        return CBlob(img, raw_name, vec(pos[0], pos[1]), 0, team)

    def argb_to_rgba(self, argb: tuple) -> tuple:
        a, r, g, b = argb
        return (r, g, b, a)

    def rgba_to_argb(self, rgba: tuple) -> tuple:
        r, g, b, a = rgba
        return (a, r, g, b)

    def _get_raw_name(self, name: str) -> str:
        if name is None: return None
        
        # handle rotation
        if name.endswith("_r0") or name.endswith("_r90") or name.endswith("_r180") or name.endswith("_r270"):
            name = name.rstrip("_r0").rstrip("_r90").rstrip("_r180").rstrip("_r270")
        
        pattern = r"_\-?([0-7]|-1)$" # chatgpt string idk
        name = re.sub(pattern, "", name)

        return name
    
    def _get_team(self, name: str) -> int:
        pattern = r"_\-?([0-7]|-1)$"
        matched = re.match(pattern, name)

        if matched is None:
            return None
        
        return int(matched.group(1))

    def _get_canvas(self):
        return self.communicator.getCanvas()

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
            with open(path, 'r') as json_file:
                data = json.load(json_file)

                kag_path = data['kag_path']
                return kag_path

        except:
            print(f"Could not find {path}")

        return None