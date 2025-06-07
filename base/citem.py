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
    team_from_alpha: bool = False
    angle_from_alpha: bool = False

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
                if FileHandler().paths.get("modded_items_path") in file_path:
                    image = image_handler.get_image(data.get("name"), mod_dir=mod_dir)
                else:
                    image = image_handler.get_image(image)

        image = SpriteConfig(
            image=image,
            z=sprite_data.get("z", 0),
            properties=sprite_props,
            offset=offset,
            position=Vec2f(0, 0),
            team=team,
            rotation=0
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
            offset=Vec2f(offset.get("x", 0), offset.get("y", 0)),
            team_from_alpha=pixel_data.get("team_from_alpha", False),
            angle_from_alpha=pixel_data.get("angle_from_alpha", False)
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

    def get_color(self, rotation: int = None, team: int = None, rotational_symmetry: bool = False) -> tuple[int, int, int, int]:
        """
        Returns an ARGB tuple representing the color for the item.
        """
        can_rotate = self.sprite.properties.is_rotatable
        can_swap_teams = self.sprite.properties.can_swap_teams

        current_rotation = self.sprite.rotation if rotation is None else rotation
        current_team = self.sprite.team if team is None else team

        pd = self.pixel_data
        colors = pd.colors

        # determine rotation key for color lookup
        lookup_rotation_key = current_rotation
        if rotational_symmetry:
            lookup_rotation_key = current_rotation % 180

        # try to get a full match first
        color_match_key = f'rotation{lookup_rotation_key}_team{current_team}'
        current_match_argb = colors.get(color_match_key)

        # fallback if no direct match
        if current_match_argb is None:
            # try with just lookup_rotation_key and team 0 if current_team is not 0
            if current_team != 0:
                color_match_key_team0 = f'rotation{lookup_rotation_key}_team0'
                current_match_argb = colors.get(color_match_key_team0)

            # fallback to first defined color if still no match
            if current_match_argb is None:
                current_match_argb = list(colors.values())[0] if colors else None
                if current_match_argb is None:
                    # no color definitions found
                    return None

        # make mutable copy of the ARGB list
        output_argb = list(current_match_argb)
        base_alpha = output_argb[0]

        final_alpha = base_alpha

        # encode rotation in alpha channel if rotatable
        if pd.angle_from_alpha and can_rotate:
            final_alpha = (final_alpha & ~0x30) | self.get_alpha_from_angle(current_rotation)

        # encode team in alpha channel
        if pd.team_from_alpha and can_swap_teams:
            final_alpha = (final_alpha & ~0x0F) | self.get_alpha_from_team(current_team)

        output_argb[0] = final_alpha
        return tuple(output_argb)

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

    def get_team_from_alpha(self, alpha: int) -> int:
        alpha &= 0x0F
        return 0 if (alpha > 7 or alpha < 0) else alpha

    def get_alpha_from_team(self, team: int) -> int:
        return team if 0 <= team <= 7 else 0x0F

    def get_angle_from_alpha(self, channel: int) -> int:
        channel &= 0x30
        return {
            0x10: 90,
            0x20: 180,
            0x30: 270
        }.get(channel, 0)

    def get_alpha_from_angle(self, angle: int) -> int:
        return {
            90: 0x10,
            180: 0x20,
            270: 0x30
            }.get(angle, 0)

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
