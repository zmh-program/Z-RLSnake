from param import *
from vector.circle import *
from vector.vec2d import hypot_percent
from typing import *
import numpy


class BaseSnake(CircleArray):
    def __init__(self, color: Optional[list] = None, location: Optional[List[float]] = None,
                 direction: Optional[list] = None, length=3):
        super().__init__(length, radius=SNAKE_RADIUS)
        self.color = color or [0, 0, 0]
        self.add_values(location or [0, 0], length)
        self.direction: numpy.ndarray = numpy.array(direction or [0, 0])
        self.alive = True
        self.head = numpy.array([0, 0])

    def __del__(self):
        del self.color
        del self.direction
        del self._size
        del self._array
        del self._array_size

    def death(self):
        self.alive = False
        del self

    def move(self) -> None:
        self.head = self.insert(self.pop() + self.direction)

    def add_body(self) -> None:
        self.append(self.get(-1))

    def update_direction(self, direction):
        self.direction = hypot_percent(direction, SNAKE_BODY_STRIDE)

    def update(self):
        if not self.alive:
            return

    def __str__(self):
        return f"Snake Object (length={self._size}, direction={self.direction})"

    def snake_collided(self, snake: "BaseSnake") -> bool:
        return self.element_is_collide_array(0, snake)

    def border_collide(self) -> bool:
        x, y = self.head
        return x - self.radius < 0 or y - self.radius < 0 or \
            x + self.radius > WIDTH or y + self.radius > HEIGHT


class Coin(Circle):
    def __init__(self, x, y):
        super().__init__(x, y, radius=COIN_RADIUS)

    def __str__(self):
        return f"Coin Object (x={self.x}, y={self.y})"
