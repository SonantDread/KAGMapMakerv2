"""
Used to get the data for tiles and blobs from JSON files.
"""
import os

from base.image_handler import ImageHandler
from utils.config_handler import ConfigHandler
from utils.file_handler import FileHandler
from utils.vec2f import Vec2f

class CustomItem:
    def __init__(self, fp: str) -> None:
        """
        Loads the data from the json file at the specified path.

        Parameters:
            fp (str): The path to the custom item's json file.
        """
        self._fp = fp

        self.type = None            # type
        self.name = None            # name
        self.display_name = None    # displayname
        self.section_name = None    # section_name
        self.image = None           # sprite -> image
        self.z_index = None         # sprite -> z_index
        self.rotatable = None       # sprite -> properties -> is_rotatable
        self.can_swap_teams = None  # sprite -> properties -> can_swap_teams
        self.team = None            # sprte -> properties -> team
        self.offset = None          # sprite -> offset
        self.search_keywords = None # search_keywords

        self._load_data()

    def get_data(self):
        return [
                self.name, self.display_name, self.section_name, self.image,
                self.z_index, self.rotatable, self.can_swap_teams, self.team,
                self.offset, self.search_keywords
            ]

    def _load_data(self):
        file = self._fp
        cfg = ConfigHandler()
        name = FileHandler().get_file_truename(file)
        cfg.load_config_file(file, name)
        data = cfg.get_modded_data(name)

        self.type = data.pop(0)
        self.name = data.pop(0)
        self.display_name = data.pop(0)
        self.section_name = data.pop(0)
        self.image = data.pop(0)
        self.z_index = data.pop(0)
        self.rotatable = data.pop(0)
        self.can_swap_teams = data.pop(0)
        self.team = data.pop(0)
        offset = data.pop(0)
        if offset is not None:
            self.offset = Vec2f(offset.get("x"), offset.get("y"))
        else:
            self.offset = Vec2f(0, 0)
        self.search_keywords = data.pop(0)
        if isinstance(self.image, int) or isinstance(self.image, str) and self.type == "tile":
            self.image = int(self.image)
            mod_dir = os.path.dirname(self._fp)
            self.image = ImageHandler().get_modded_image(self.name, mod_dir, self.image)
