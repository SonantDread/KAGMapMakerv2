from PyQt6.QtGui import QPixmap, QImage, QColor
from utils.vec import vec
from PIL import Image
import os

class CBlob:
    def __init__(self, img: QPixmap, name: str, pos: vec, layer: int, team: int = 0, z: int = 0):
        self.img = img
        self.name = name
        self.pos = pos
        self.layer = layer # unused for now
        self.team = team
        self.z = z # TODO: if a Z value isn't specified, it should be based on the sprite size
        # self.swapPNGColorsToTeam(self.img, 1)

    # ! IGNORE ALL CODE BELOW THIS POINT, COMPLETELY UNFINISHED

    # def swapPNGColorsToTeam(self, img: QPixmap = None, team: int = None) -> None:
    #     if team == self.team:
    #         return  # do nothing if same team

    #     if img is None:
    #         img = self.img

    #     if team is None:
    #         team = self.team

    #     if img is None:
    #         return None

    #     if team < 0:
    #         team = 0
    #     elif team > 7:
    #         team = 7

    #     img = img.toImage().convertToFormat(QImage.Format.Format_RGBA8888) # convert to RGBA
    #     width, height = img.width(), img.height()
    #     teampalette = self._getColorPalette()

    #     # for x in range(width):
    #     #     for y in range(height):
    #     #         pixel_color = img.pixelColor(x, y)
    #     #         pixel_color_tuple = (pixel_color.red(), pixel_color.green(), pixel_color.blue(), pixel_color.alpha())

    #     #         # search for the pixel_color in the original team palette (self.team)
    #     #         for i, original_color in enumerate(teampalette[self.team]):
    #     #             if pixel_color_tuple == original_color:
    #     #                 # swap to the corresponding color in the target team's palette
    #     #                 new_color = teampalette[team][i]
    #     #                 # print(f"Swapping {pixel_color_tuple} to {new_color} at position ({x}, {y}) in {self.name}")
    #     #                 img.setPixelColor(x, y, QColor(new_color[0], new_color[1], new_color[2], new_color[3]))
    #     #                 break

    #     # self.img = QPixmap.fromImage(img)
    #     self.img = self._swapToColorPalette(img, teampalette, team)
    #     self.team = team # for some reason this code only works on keg?

    # def _getColorPalette(self) -> dict:
    #     """
    #     Retrieves the color palette from the TeamPalette.png image.

    #     Returns:
    #         dict: A dictionary where each key represents a team and its corresponding value is a list of RGBA color tuples.
    #     """
    #     palette = Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Sprites", "Default", "TeamPalette.png"))
    #     palette = palette.convert("RGBA")
    #     palette.load()

    #     width, height = palette.size
    #     colors = {} # 0: blue colors, 1: red colors, etc

    #     for x in range(width):
    #         col = []
    #         for y in range(height):
    #             col.append(palette.getpixel((x, y)))
    #         colors[x] = col

    #     palette.close()
    #     return colors

    # def _isWithinColorRange(self, pixel_color: QColor, teampalette: list) -> bool:
    #     """
    #     Checks if a given pixel color is within a range of 10.

    #     Args:
    #         pixel_color (QColor): The RGB values of the pixel color.
    #         teampalette (list): A list of colors to check against.

    #     Returns:
    #         bool: True if the pixel color is within the color range, False otherwise.
    #     """
    #     pixel_rgb = pixel_color.getRgb()[:3]  # Extract the RGB values from QColor as a tuple
    #     for color in teampalette:
    #         if abs(color[0] - pixel_rgb[0]) >= 10 or abs(color[1] - pixel_rgb[1]) >= 10 or abs(color[2] - pixel_rgb[2]) >= 10:
    #             return False
    #     return True

    
    # def _swapToColorPalette(self, img: QImage, palette: dict, team: int) -> QPixmap:
    #     width, height = img.width(), img.height()
    #     new_img = QImage(width, height, QImage.Format.Format_RGBA8888)
    #     teampalette = palette[team]
        
    #     for x in range(width):
    #         for y in range(height):
    #             pixel_color = img.pixelColor(x, y)

    #             # Check if the pixel color is within the color range to be swapped
    #             if self._isWithinColorRange(pixel_color, palette[self.team]):
    #                 pixel_rgb = pixel_color.getRgb()[:3]  # Extract RGB values from the QColor object
                    
    #                 # Initialize the minimum distance as infinity
    #                 min_dist = float('inf')
    #                 closest_color = teampalette[0]  # Default to the first color in the palette

    #                 # Find the closest color in the team palette
    #                 for color in teampalette:
    #                     dist = sum([abs(c1 - c2) for c1, c2 in zip(color[:3], pixel_rgb)])
    #                     if dist < min_dist:
    #                         min_dist = dist
    #                         closest_color = color

    #                 # Set the closest matching color
    #                 new_color = QColor(closest_color[0], closest_color[1], closest_color[2], pixel_color.alpha())
    #                 new_img.setPixelColor(x, y, new_color)
    #             else:
    #                 # If not within range, keep the original color
    #                 new_img.setPixelColor(x, y, pixel_color)

    #     return QPixmap.fromImage(new_img)


    #     # FOR TEAM SWAPPING
    #     # TODO: this should iterate through the every pixel in 'img' and use
    #     # TODO: _isWithinColorRange to determine if the pixel is available to be swapped
    #     # TODO: then swap it to the closest color within teampalette using 'team' for the target team
    #     # TODO: after the color is swapped to the new team, the difference (positive or negative) between the closest palette color
