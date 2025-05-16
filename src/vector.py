from argparse import ArgumentError
from math import radians, degrees, sin, cos, atan2
from logger import printWarning

class Size:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.size = Vector(x, y)
    def __str__(self): return f"Size({self.x}, {self.y})"
    def get(self): return self.size()
    def __call__(self, *args, **kwargs): return self.get()
    def __getitem__(self, item): return self.get()[item]
    def setx(self, x): self.x, self.size.x = x, x
    def sety(self, y): self.y, self.size.y = y, y
    def rescale(self, scale):
        self.size * scale
        self.x, self.y = self.size()
    def length(self): return self.x
    def width(self): return self.y

class Vector:
    def __init__(self, x=0, y=0, define_by_angle=False, angle=None, norm=None):
        if not define_by_angle:
            self.x: int | float = x
            self.y: int | float = y
            self.angle: float = atan2(self.y, self.x) % 6.2831
            self.norm = abs(self)
        else:
            self.norm = norm if (norm is not None) else 1
            self.angle = angle % 6.2831
            self.x = cos(angle) * self.norm
            self.y = sin(angle) * self.norm

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.angle
        else:
            printWarning(f"[VECTOR] __getitem__ : Argument Error -> {item}")
            return 0

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        elif isinstance(other, (list, tuple)) and len(other) == 2 and all((isinstance(elt, (int, float)) for elt in other)):
            return Vector(self.x + other[0], self.y + other[1])
        else:
            printWarning(f"[VECTOR] __add__ : Argument Error -> {other}")
            return NullVector()
    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other)
        elif isinstance(other, Vector):
            return Vector(self.x * other.x, self.y * other.x)
        elif isinstance(other, (list, tuple)) and len(other) == 2 and all((isinstance(elt, (int, float)) for elt in other)):
            return Vector(self.x * other[0], self.y * other[1])
        else:
            printWarning(f"[VECTOR] __mul__ : Argument Error -> {other}")
            raise ArgumentError
    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        elif isinstance(other, (list, tuple)) and len(other) == 2 and all((isinstance(elt, (int, float)) for elt in other)):
            return Vector(self.x - other[0], self.y - other[1])
        else:
            printWarning(f"[VECTOR] __sub__ : Argument Error -> {other} (type {type(other)})")
            return NullVector()
    def __rsub__(self, other):
        return -1 * self.__sub__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(1/other if other != 0 else 0)
        else:
            printWarning(f"[VECTOR] __rtruediv__ : {self} cannot be divided by {other}")
            return NullVector()
    def __rtruediv__(self, other):
        printWarning(f"[VECTOR] __rtruediv__ : {other} cannot be divided by a {self}")
        return NullVector()

    def __floordiv__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x // other, self.y // other)
        else:
            printWarning(f"[VECTOR] __rfloordiv__ : {self} cannot be divided by {other}")
            return NullVector()
    def __rfloordiv__(self, other):
        printWarning(f"[VECTOR] __rfloordiv__ : {other} cannot be divided by a {self}")
        return NullVector()

    def __str__(self):
        return f"Vector({self.x:.2f}, {self.y:.2f} | ({degrees(self.angle):.1F}°))"

    def __len__(self):
        return 2

    def __abs__(self):
        return (self.x**2 + self.y**2)**0.5

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, (list, tuple)) and len(other) == 2 and all((isinstance(elt, (int, float)) for elt in other)):
            return self.x == other[0] and self.y == other[1]
        else:
            printWarning(f"[VECTOR] __eq__ : {other} cannot be compared to {self} -> False")
            return False

    def __bool__(self): return self != NullVector()
    def __copy__(self): return Vector(self.x, self.y)
    def __call__(self, *args, **kwargs) -> list[int | float] | None:
        if len(args) == 0:
            return [self.x, self.y]
        elif len(args) == 2:
            x, y = args
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                self.__init__(x, y)
            else:
                printWarning(f"[VECTOR] __call__ : error, x and y must be int or float")
        else:
            printWarning(f"[VECTOR] __call__ : error, use Vector(new_x, new_y)")
        return None
    def __round__(self, n=None):
        return Vector(round(self.x, n), round(self.y, n))
    def __pow__(self, power, modulo=None):
        return Vector(self.x ** power, self.y ** power)
    def __neg__(self):
        return self.__mul__(-1)

    def scale(self, scale): return self * scale
    def scalexy(self, scale_x=1, scale_y=1): return self * (scale_x, scale_y)
    def opposite(self): return -self
    def normalised(self): return self / abs(self)
    def dot(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        elif isinstance(other, (list, tuple)) and len(other) == 2 and all((isinstance(elt, (int, float)) for elt in other)):
            return self.x * other[0] + self.y * other[1]
        else:
            printWarning(f"[VECTOR] dot() : incompatible dot product between : {self} {other} -> False")
            return 0


def NullVector() -> Vector:
    return Vector(0, 0)
def rad(x): return radians(x)
def deg(x): return degrees(x)
