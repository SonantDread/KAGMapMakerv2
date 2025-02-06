import os
from dataclasses import dataclass

from PyQt6.QtGui import QPixmap

from base.image_handler import ImageHandler
from utils.vec2f import Vec2f

@dataclass
class SpriteProperties:
    is_rotatable: bool = False
    can_swap_teams: bool = False
    team: int = 0

@dataclass
class SpriteConfig:
    image: QPixmap # todo: this should convert it to a qpixmap if it isnt already
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
class CItem:
    type: str
    name: str
    display_name: str
    section_name: str
    sprite: SpriteConfig
    search_keywords: list[str]
    mod_info: ModInfo
    pixel_colors: dict[str, list[int, int, int, int]]
    team_from_channel: bool
    angle_from_channel: bool

    @classmethod
    def from_dict(cls, data: dict, file_path: str = "") -> 'CItem':
        """
        Creates a CItem instance from a dictionary.
        """
        sprite_data = data.get("sprite", {})
        properties = sprite_data.get("properties", {})

        offset_data = sprite_data.get("offset", {"x": 0, "y": 0})
        offset = Vec2f(offset_data.get("x", 0), offset_data.get("y", 0))

        sprite_props = SpriteProperties(
            is_rotatable=properties.get("is_rotatable", False),
            can_swap_teams=properties.get("can_swap_teams", False),
            team=properties.get("team", 0)
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

        pixel_colors=data.get("pixel_colors", {})

        return cls(
            type=data.get("type", ""),
            name=data.get("name", ""),
            display_name=str(data.get("display_name", "")).strip(),
            section_name=data.get("section_name", ""),
            sprite=image,
            search_keywords=data.get("search_keywords", []),
            mod_info=mod_info,
            pixel_colors=pixel_colors,
            team_from_channel=pixel_colors.get("team_from_channel", False),
            angle_from_channel=pixel_colors.get("angle_from_channel", False)
        )

    # todo: important notes from kag_color.py:
    # water_backdirt needs implementation
    # necromancer_teleport needs implementation
    # do we need spike variations?

    def get_color(self, rotation: int = 0, team: int = 0, rotational_symmetry: bool = False) -> tuple[int, int, int, int]:
        """
        Returns an ARGB tuple representing the color for the item.

        Parameters:
            rotation (int): The rotation for the item.
            team (int): the team for the item.
            rotational_symmetry (bool): Rotations are normalized to 0 or 90,
            allowing for easier matching to objects such as doors.

        Returns:
            The pixel color of the item.
        """
        colors = self.pixel_colors

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
        return self.name in names or self.name is None
