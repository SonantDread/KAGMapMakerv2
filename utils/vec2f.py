# KAGMapMakerV2 - An unofficial map maker for King Arthur's Gold.
# Copyright (C) 2026 SonantDread
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
Used to store 2D vector positions.
"""
from typing import Union
class Vec2f:
    """
    Stores a 2D vector of integer or float.
    """
    def __init__(self, x: Union[float, int] = 0, y: Union[float, int] = 0):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x + other.x, self.y + other.y)

        if isinstance(other, (int, float)):
            return Vec2f(self.x + other, self.y + other)

        raise TypeError("Unsupported operand type for addition")

    def __sub__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x - other.x, self.y - other.y)

        if isinstance(other, (int, float)):
            return Vec2f(self.x - other, self.y - other)

        raise TypeError("Unsupported operand type for subtraction")

    def __mul__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x * other.x, self.y * other.y)

        if isinstance(other, (int, float)):
            return Vec2f(self.x * other, self.y * other)

        raise TypeError("Unsupported operand type for multiplication")

    def __truediv__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x / other.x, self.y / other.y)

        if isinstance(other, (int, float)):
            return Vec2f(self.x / other, self.y / other)

        raise TypeError("Unsupported operand type for division")

    def __floordiv__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x // other.x, self.y // other.y)

        if isinstance(other, (int, float)):
            return Vec2f(self.x // other, self.y // other)

        raise TypeError("Unsupported operand type for floor division")

    def __mod__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x % other.x, self.y % other.y)

        if isinstance(other, (int, float)):
            return Vec2f(self.x % other, self.y % other)

        raise TypeError("Unsupported operand type for modulo")

    def __pow__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x ** other.x, self.y ** other.y)

        if isinstance(other, (int, float)):
            return Vec2f(self.x ** other, self.y ** other)

        raise TypeError("Unsupported operand type for power")

    def __neg__(self):
        return Vec2f(-self.x, -self.y)

    def __abs__(self):
        return Vec2f(abs(self.x), abs(self.y))

    def __round__(self, n=None):
        return Vec2f(round(self.x, n), round(self.y, n))

    def __int__(self):
        return Vec2f(int(self.x), int(self.y))

    def __float__(self):
        return Vec2f(float(self.x), float(self.y))

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Vec2f):
            return self.x == other.x and self.y == other.y

        return False

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Vec2f({self.x}, {self.y})"
