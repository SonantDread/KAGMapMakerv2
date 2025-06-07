"""
Handles all image loading.
"""
import inspect
import os
from typing import Union

from PIL import Image
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QBuffer, QByteArray
from utils.file_handler import FileHandler
import colorsys
import io

# acceptable range of colors
# may need to be changed (or have a different system) in the future but this works for now
BLUE_HUE_RANGE = (150 / 360.0, 235 / 360.0)
TEAM_HUE_SHIFT = {
    0: 0,    # No shift
    1: 157,  # Blue -> Red
    2: 244,  # Blue -> Green
    3: 73,   # Blue -> Purple
    4: 177,  # Blue -> Gold
    5: 322,  # Blue -> Teal
    6: 24,   # Blue -> Indigo
}

class SingletonMeta(type):
    """
    Used to share code between all instances of the class.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class ImageHandler(metaclass=SingletonMeta):
    """
    Used to handle all image loading.
    """
    def __init__(self) -> None:
        self._file_handler = FileHandler()
        self._vanilla_images = {}
        self._modded_images = {}

        self.vanilla_tiles_indexes: dict[str, int] = {
            "tile_empty": int(0),
            "tile_ground": int(16),
            "tile_grassy_ground": int(23),
            "tile_grass": int(25),
            "tile_ground_back": int(32),
            "tile_castle": int(48),
            "tile_castle_back": int(64),
            "tile_gold": int(80),
            "tile_stone": int(96),
            "tile_bedrock": int(106),
            "tile_wood_back": int(173),
            "tile_wood": int(196),
            "tile_thickstone": int(208),
            "tile_castle_moss": int(224),
            "tile_castle_back_moss": int(227),
            "sky": int(400),
        }

    def get_image(self, name: Union[str, int], team: int = 0, path: str = None) -> QPixmap:
        if team not in self._vanilla_images:
            self._vanilla_images[team] = {}

        if team not in self._modded_images:
            self._modded_images[team] = {}

        # world.png image
        if isinstance(name, int):
            return self._get_image_by_index(name, path)

        # make the name more friendly
        name = os.path.splitext(str(name).strip().lower())[0]

        # modded item (these get priority)
        image = self._get_modded_image(name, team, path)

        if image:
            return image

        # vanilla item
        image = self._get_vanilla_image(name, team)

        if image:
            return image

        # image not found
        fn = os.path.basename(__file__)
        ln = inspect.currentframe().f_lineno
        print(f"Image not found: {name}. Unable to load in line {ln} of {fn}")
        return None

    def _get_vanilla_image(self, name: str, team: int = 0) -> QPixmap:
        # image is loaded
        image = self._vanilla_images.get(team, {}).get(name)
        if image:
            return image

        # image is not loaded
        return self._load_vanilla_image(name, team)

    def _get_modded_image(self, name: str, team: int = 0, path: str = None) -> QPixmap:
        # image is loaded
        image = self._modded_images.get(team, {}).get(name)
        if image:
            return image

        # image is not loaded
        return self._load_modded_image(name, team, path)

    def _get_image_by_index(self, index: int, world_path: str) -> QPixmap:
        # first check if the image is already cached
        if world_path is None and index in self._vanilla_images[0]:
            return self._vanilla_images[0][index]

        if world_path is not None and (world_path, index) in self._modded_images[0]:
            return self._modded_images[0][(world_path, index)]

        # vanilla image
        is_vanilla_image = world_path is None
        if is_vanilla_image:
            path = self._file_handler.paths.get("world_path")
        # modded image
        else:
            path = self._get_world_path(world_path)

        if not path or not self._file_handler.does_path_exist(path):
            return None

        image = Image.open(path).convert("RGBA")

        width = image.size[0]
        tile_size = width // 8

        x = (index % tile_size) * 8
        y = (index // tile_size) * 8

        image = image.crop((x, y, x + 8, y + 8)).toqpixmap()

        self._cache_image_by_index(image, world_path, index)
        return image

    def _cache_image_by_index(self, image: QPixmap, path: str, index: int) -> None:
        is_vanilla = path is None
        if is_vanilla:
            self._vanilla_images[0][index] = image
        else:
            # store with path and index as a tuple key
            self._modded_images[0][(path, index)] = image

    def _load_modded_image(self, name: str, team: int, mod_path: str) -> QPixmap:
        # loading a modded image
        if mod_path is not None:
            paths = [
                os.path.join(mod_path, f"{name}.png"),
                os.path.join(mod_path, "Sprites", f"{name}.png")
            ]

            for path in paths:
                if os.path.exists(path):
                    image = Image.open(path).convert("RGBA").toqpixmap()
                    image = self._swap_sprite_color(image, team)
                    self._modded_images[team][name] = image
                    return image

            # fallback
            fallback_path = self._file_handler.get_modded_item_path(f"{name}", mod_path)
            if fallback_path and os.path.exists(fallback_path):
                image = Image.open(fallback_path).convert("RGBA").toqpixmap()
                image = self._swap_sprite_color(image, team)
                self._modded_images[team][name] = image
                return image

    def _load_vanilla_image(self, name: str, team: int) -> QPixmap:
        base_path = self._file_handler.paths.get("mapmaker_images")

        img_path = os.path.join(base_path, f"{name}.png")
        if os.path.exists(img_path):
            image = Image.open(img_path).convert("RGBA").toqpixmap()
            image = self._swap_sprite_color(image, team)
            self._vanilla_images[team][name] = image
            return image

        fn = os.path.basename(__file__)
        ln = inspect.currentframe().f_lineno
        print(f"Image not found: '{name}'. Unable to load in line {ln} of {fn}")

        return None

    def _get_world_path(self, world_path: str) -> str:
        if not world_path:
            return None

        # path is to a file
        if os.path.isfile(world_path):
            return world_path

        paths = [
            os.path.join(world_path, "world.png"),
            os.path.join(world_path, "Sprites", "world.png")
        ]

        for path in paths:
            if os.path.isfile(path):
                return path

        # fallback
        print(f"Could not find world.png at '{world_path}'. Attempting to use fallback...")
        for root, _, files in os.walk(world_path):
            for file in files:
                if file == "world.png":
                    return os.path.join(root, file)

        # image wasn't found
        fn = os.path.basename(__file__)
        ln = inspect.currentframe().f_lineno
        print(f"Image not found: world.png. Unable to load in line {ln} of {fn}")
        return None

    #* team swapping code below here
    def _swap_sprite_color(self, original_image: QPixmap, to_team: int) -> QPixmap:
        """
        Swaps the team of a sprite.
        """
        # no change needed
        if to_team == 0:
            return original_image

        # convert QPixmap to PIL Image
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        original_image.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data().data())).convert("RGBA")

        width, height = pil_image.size
        new_image: Image = pil_image.copy()

        # prevent invalid team indices
        if to_team < 0 or to_team > 7:
            to_team = 7

        palette = self._get_team_palette()

        # ensure valid palettes exist
        if to_team not in palette:
            return

        # [R, G, B] colors
        old_team_colors = palette[0]
        new_team_colors = palette[to_team]

        for y in range(height):
            for x in range(width):
                r, g, b, a = pil_image.getpixel((x, y))

                # skip transparent pixels
                if a == 0:
                    continue

                # only swap team colored pixels
                if not self._is_team_color(r, g, b):
                    continue

                try:
                    # try to get a direct match of colors
                    color_index = old_team_colors.index([r, g, b])
                    new_color = new_team_colors[color_index]

                except ValueError:
                    # if the color isn't found, find the closest match
                    old_color = (r, g, b)
                    best_match = self._closest_color(old_color, old_team_colors)
                    color_index = old_team_colors.index(best_match)
                    new_color = new_team_colors[color_index]

                new_image.putpixel((x, y), (new_color[0], new_color[1], new_color[2], a))

        # convert back to QPixmap
        buffer = io.BytesIO()
        new_image.save(buffer, format="PNG")
        qimg = QImage.fromData(QByteArray(buffer.getvalue()))
        return QPixmap.fromImage(qimg)

    def _is_team_color(self, r: int, g: int, b: int) -> bool:
        """
        Checks if a color is within the defined blue hue range.
        """
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        return BLUE_HUE_RANGE[0] <= h <= BLUE_HUE_RANGE[1] and s > 0.2

    def _closest_color(self, target: tuple[int, int, int], color_list: list[tuple[int, int, int]]) -> tuple[int, int, int]:
        """
        Finds the closest color in the color list using Euclidean distance.
        """
        min_dist = float("inf")
        # defaults to first color if no match is found
        closest_match = color_list[0]

        for color in color_list:
            r, g, b = color
            dist = ((target[0] - r) ** 2 + (target[1] - g) ** 2 + (target[2] - b) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_match = color

        return closest_match

    def _get_team_palette(self) -> dict[int, list[list[int, int, int]]]:
        path = FileHandler().paths.get("team_palette_path")
        image = Image.open(path).convert("RGB")

        teams = {}

        w, h = image.size
        for x in range(w):
            for y in range(h):
                r, g, b = image.getpixel((x, y))

                if x not in teams:
                    teams[x] = []

                teams[x].append([r, g, b])

        return teams
