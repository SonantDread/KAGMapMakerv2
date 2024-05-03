
class vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return vec(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return vec(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        if isinstance(other, vec):
            return vec(self.x / other.x, self.y / other.y)
        elif isinstance(other, (int, float)):
            return vec(self.x / other, self.y / other)
        else:
            raise TypeError("Unsupported operand type for division")


    def __floordiv__(self, other):
        return vec(self.x // other.x, self.y // other.y)

    def __mod__(self, other):
        return vec(self.x % other.x, self.y % other.y)

    def __pow__(self, other):
        return vec(self.x ** other.x, self.y ** other.y)

    def __neg__(self):
        return vec(-self.x, -self.y)

    def __abs__(self):
        return vec(abs(self.x), abs(self.y))

    def __round__(self, n=None):
        return vec(round(self.x, n), round(self.y, n))

    def __int__(self):
        return vec(int(self.x), int(self.y))

    def __float__(self):
        return vec(float(self.x), float(self.y))
