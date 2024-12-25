"""
Used to store Vector 2 positions.
"""
class Vec2f:
    """
    Used to store Vector 2 positions.
    """
    def __init__(self, x: int = 0, y: int = 0):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, other):
        return Vec2f(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2f(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vec2f(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        if isinstance(other, Vec2f):
            return Vec2f(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return Vec2f(self.x / other, self.y / other)
        else:
            raise TypeError("Unsupported operand type for division")


    def __floordiv__(self, other):
        return Vec2f(self.x // other.x, self.y // other.y)

    def __mod__(self, other):
        return Vec2f(self.x % other.x, self.y % other.y)

    def __pow__(self, other):
        return Vec2f(self.x ** other.x, self.y ** other.y)

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
