import os
from dataclasses import dataclass, field

from copy import deepcopy
from PyQt6.QtGui import QPixmap

from base.image_handler import ImageHandler
from utils.file_handler import FileHandler
from utils.vec2f import Vec2f

image_handler = ImageHandler()

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
                # t*odo: ideally this would use filehandler for this path
                # but was getting circular import error
                if FileHandler().paths.get("modded_items_path") in file_path:
                    image = image_handler.get_image(data.get("name"), mod_dir=mod_dir)
                else:
                    image = image_handler.get_image(image)

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
            sprite=sprite, # todo: this should use the new imagehandler system to look up the image
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

        self.sprite.image = image_handler.get_image(self.name_data.name, team)
        # update sprite's team
        self.sprite.team = team

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
