import os
from dataclasses import dataclass, field

from copy import deepcopy
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QBuffer, QByteArray
from PIL import Image
import io
import colorsys

from base.image_handler import ImageHandler
from utils.vec2f import Vec2f

# acceptable range of colors
BLUE_HUE_RANGE = (150 / 360.0, 250 / 360.0)
TEAM_HUE_SHIFT = {
    0: 0,    # No shift
    1: 157,  # Blue -> Red
    2: 244,  # Blue -> Green
    3: 73,   # Blue -> Purple
    4: 177,  # Blue -> Gold
    5: 322,  # Blue -> Teal
    6: 24,   # Blue -> Indigo
}

@dataclass
class Name:
    name: str
    display_name: str
    section_name: str

@dataclass
class SpriteProperties:
    is_rotatable: bool = False
    can_swap_teams: bool = False
    team: int = 0
    merges_with: dict = field(default_factory=dict)
    in_picker_menu: bool = True

@dataclass
class SpriteConfig:
    image: QPixmap
    z: int
    properties: SpriteProperties
    offset: Vec2f = Vec2f(0, 0)
    position: Vec2f = Vec2f(0, 0)
    team: int = 0
    rotation: int = 0

@dataclass
class ModInfo:
    folder_name: str
    file_name: str
    full_path: str

@dataclass
class PixelData:
    colors: dict[str, list[int, int, int, int]]
    offset: Vec2f

@dataclass
class CItem:
    type: str
    name_data: Name
    sprite: SpriteConfig
    mod_info: ModInfo
    pixel_data: PixelData
    search_keywords: list[str]

    @classmethod
    def from_dict(cls, data: dict, file_path: str = "") -> 'CItem':
        """
        Creates a CItem instance from a dictionary.
        """
        sprite_data = data.get("sprite", {})
        properties = sprite_data.get("properties", {})

        offset_data = sprite_data.get("offset", {"x": 0, "y": 0})
        offset = Vec2f(offset_data.get("x", 0), offset_data.get("y", 0))

        team = properties.get("team", 0)
        sprite_props = SpriteProperties(
            is_rotatable=properties.get("is_rotatable", False),
            can_swap_teams=properties.get("can_swap_teams", False),
            team=team,
            merges_with=properties.get("merges_with", {}),
            in_picker_menu=properties.get("in_picker_menu", True)
        )

        # handle image loading for tiles
        image = sprite_data.get("image")
        if isinstance(image, (int, str)):
            if data.get("type") == "tile":
                image = int(image)
            else:
                image = str(image)

            if file_path:
                mod_dir = os.path.dirname(file_path)
                # modded item
                # todo: ideally this would use filehandler for this path
                # but was getting circular import error
                if os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Modded") in file_path:
                    image = ImageHandler().get_modded_image(data.get("name"), mod_dir, image)
                else:
                    image = ImageHandler().get_image(image)

        image = SpriteConfig(
            image=image,
            z=sprite_data.get("z", 0),
            properties=sprite_props,
            offset=offset
        )

        mod_info = ModInfo(
            folder_name=os.path.basename(os.path.dirname(file_path)),
            file_name=os.path.basename(file_path),
            full_path=file_path
        )

        pixel_data = data.get("pixel_data", {})
        offset = pixel_data.get("offset", {"x": 0, "y": 0})
        pixel_colors = PixelData(
            colors=pixel_data.get("colors", {}),
            offset=Vec2f(offset.get("x", 0), offset.get("y", 0))
        )

        name_data = Name(
            name=data.get("name", ""),
            display_name=str(data.get("display_name", "")).strip(),
            section_name=data.get("section_name", "")
        )

        item = cls(
            type=data.get("type", ""),
            name_data=name_data,
            sprite=image,
            mod_info=mod_info,
            pixel_data=pixel_colors,
            search_keywords=data.get("search_keywords", [])
        )

        # default sprites are team 0 (in vanilla), if they arent 0 the sprite needs to be swapped
        # may need to be adjusted for modded items that dont do this but for now this is fine
        if team != 0:
            item.swap_team(team)

        return item

    def get_color(self, rotation: int = 0, team: int = 0, rotational_symmetry: bool = False) -> tuple[int, int, int, int]:
        """
        Returns an ARGB tuple representing the color for the item.

        Parameters:
            rotation (int): The rotation for the item.
            team (int): the team for the item.
            allowing for easier matching to objects such as doors.

        Returns:
            The pixel color of the item.
        """
        colors = self.pixel_data.colors

        full_match: list = colors.get(f'rotation{rotation}_team{team}')
        if full_match is not None:
            return tuple(full_match)

        if rotational_symmetry:
            rotation = rotation % 180

        match = colors.get(f'rotation{rotation}_team{team}')
        if match is not None:
            return tuple(match)

        return None

    def is_eraser(self) -> bool:
        names = [
            "sky",
            "tile_empty",
            ""
        ]
        n = self.name_data.name
        return n in names or n is None

    def copy(self) -> 'CItem':
        """
        Creates a deep copy of the CItem instance.
        """
        image = self.sprite.image
        self.sprite.image = None
        sprite = deepcopy(self.sprite)
        self.sprite.image = image
        sprite.image = image

        return CItem(
            type=deepcopy(self.type),
            name_data=deepcopy(self.name_data),
            sprite=sprite,
            mod_info=deepcopy(self.mod_info),
            pixel_data=deepcopy(self.pixel_data),
            search_keywords=deepcopy(self.search_keywords)
        )

    def swap_team(self, team: int) -> None:
        """
        Swaps the team of the sprite.
        """
        # already is blue team
        if team == 0:
            return

        self._swap_sprite_color(team)
        # update sprite's team
        self.sprite.team = team

    def _swap_sprite_color(self, to_team: int) -> None:
        """
        Swaps the color of the sprite using PIL instead of Qt.
        """
        # unfortunately required to be like this because
        # getpixelcolor() was returning [0,0,0,0] instead of the actual color

        # convert QPixmap to PIL Image
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        self.sprite.image.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data().data())).convert("RGBA")

        width, height = pil_image.size

        # create the new image with the same mode
        new_image = pil_image.copy()

        # prevent key errors
        if to_team < 0 or to_team > 6:
            to_team = 7
            hue_shift = 0

        else:
            # convert to fraction
            hue_shift = TEAM_HUE_SHIFT[to_team] / 360.0

        for y in range(width):
            for x in range(height):
                r, g, b, a = pil_image.getpixel((y, x))

                # optimization: skip transparent pixels
                if a == 0:
                    continue

                # convert to HSV
                hue, sat, val = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

                # only shift if within the blue hue range
                if BLUE_HUE_RANGE[0] <= hue <= BLUE_HUE_RANGE[1]:
                    # assume team is -1 / 255 / 7
                    if TEAM_HUE_SHIFT.get(to_team, None) is None:
                        sat = 0
                        h = hue
                    else:
                        # shift and wrap around the wheel
                        h = (hue + hue_shift) % 1.0
                    # back to RGB
                    r, g, b = colorsys.hsv_to_rgb(h, sat, val)
                    new_image.putpixel((y, x), (int(r * 255), int(g * 255), int(b * 255), a))

        # convert back to QPixmap
        buffer = io.BytesIO()
        new_image.save(buffer, format="PNG")
        qimg = QImage.fromData(QByteArray(buffer.getvalue()))
        self.sprite.image = QPixmap.fromImage(qimg)

    def is_mergeable(self) -> bool:
        """
        Determines if the item is mergeable.
        """
        # returns true if it can merge
        return bool(self.sprite.properties.merges_with)

    def merge_with(self, other: str) -> str:
        """
        Merges the item with another item based on it's name.
        """
        return self.sprite.properties.merges_with.get(other, None)

    def is_in_picker_menu(self) -> bool:
        return self.sprite.properties.in_picker_menu
