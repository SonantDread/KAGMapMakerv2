"""
Holds basic information for blobs.
"""

from PyQt6.QtGui import QPixmap
from utils.vec2f import Vec2f

class CBlob:
    """
    Represents a blob object with basic information.

    Attributes:
        img (QPixmap): The image of the blob.
        name (str): The name of the blob.
        pos (Vec2f): The position of the blob.
        layer (int): The layer of the blob (currently unused).
        team (int): The team the blob belongs to.
        z (int): The depth of the blob in the rendering (0 by default).
    """
    def __init__(self, img: QPixmap, name: str, pos: Vec2f, layer: int, team: int = 0, z: int = 0, r: int = 0):
        self.img = img
        self.name = name
        self.pos = pos
        self.layer = layer # unused for now
        self.team = team
        self.z = z
        self.rotation = r
