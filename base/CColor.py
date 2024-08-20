"""
Used to represent 
"""

class CColor:
    """
    Represents a color in the game, either ARGB or RGBA.

    Attributes:
        color (tuple): The color as a tuple of integers in ARGB format.
        is_argb (bool): Whether the color is in ARGB format.
    """
    def __init__(self, color: tuple, is_argb: bool):
        self.color: tuple = color
        self.is_argb = is_argb

    def get_alpha(self) -> int:
        """
        Returns the alpha value of the color.

        Returns:
            int: The alpha value.
        """
        return self.color[0]

    def get_red(self) -> int:
        """
        Returns the red value of the color.

        Returns:
            int: The red value.
        """
        return self.color[1]

    def get_green(self) -> int:
        """
        Returns the green value of the color.

        Returns:
            int: The green value.
        """
        return self.color[2]

    def get_blue(self) -> int:
        """
        Returns the blue value of the color.

        Returns:
            int: The blue value.
        """
        return self.color[3]

    def get_rgb(self):
        """
        Returns the RGB values of the color.

        Returns:
            tuple: The RGB values as a tuple.
        """
        return self.color[1:3]

    def get_color_argb(self) -> tuple:
        """
        Returns the color as a tuple in ARGB format.

        Returns:
            tuple: The color as a tuple in ARGB format.
        """
        return self.color

    def get_color_rgba(self) -> tuple:
        """
        Returns the color as a tuple in RGBA format.

        Returns:
            tuple: The color as a tuple in RGBA format.
        """
        return (self.color[3], self.color[0], self.color[1], self.color[2])
