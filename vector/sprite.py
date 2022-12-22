from param import *
from .circle import *
from .vec2d import hypot_percent
from typing import *
import numpy


def generate_position():
    return numpy.array([
        numpy.random.randint(WIDTH_BLOCK) * BLOCK_STRIDE,
        numpy.random.randint(HEIGHT_BLOCK) * BLOCK_STRIDE,
    ])


def snake_combination_collide(s1: "BaseSnake", s2: "BaseSnake") -> Tuple[bool, bool]:
    """
    :return: s1 was collided, s2 was collided
    """
    response = s1.snake_collided(s2)
    if response is not False:
        if response == 0:  # 双方碰撞头部
            return True, True
    return not not response, not not s2.snake_collided(s1)  # 包含双方都由对方身体碰撞头部 (由自身身体碰撞头部不会视为碰撞)


class BaseSnake(CircleArray):
    def __init__(self, color: Optional[list] = None, location: Optional[List[float]] = None,
                 direction: Optional[list] = None, length=3):
        super().__init__(length, radius=SNAKE_RADIUS)
        self.color = color or [0, 0, 0]
        self.add_values(location or generate_position(), length)
        self.direction: numpy.ndarray = numpy.array(direction or [0, 0])
        self.alive = True
        self.head = numpy.array([0, 0])

        self.score = 0
        self.score__added = 0
        self.score__queue = 0
        self.kill = 0
        self.kill__added = 0

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

    def add_body(self, num=1) -> None:
        for _ in range(num):
            self.append(self.get(-1))

    def update_direction(self, direction):
        self.direction = hypot_percent(direction, SNAKE_BODY_STRIDE)

    def update(self):
        if not self.alive:
            return

        self.kill += self.kill__added
        self.score += self.score__added
        self.kill__added = 0
        self.score__added = 0

    def __str__(self):
        return f"Snake Object (length={self._size}, direction={self.direction})"

    def add_killed(self, val=1):
        self.kill__added += val

    def add_score(self, val=1):
        self.score += val

        queue = self.score__queue + val
        score__ready = queue // 5
        self.score__queue = queue % 5
        self.add_body(score__ready)
        return score__ready

    def snake_collided(self, snake: "BaseSnake") -> bool:
        return self.element_is_collide_array(0, snake)

    def border_collide(self) -> bool:
        x, y = self.head
        return x - self.radius < 0 or y - self.radius < 0 or \
            x + self.radius > WIDTH or y + self.radius > HEIGHT


class Coin(Circle):
    def __init__(self, position: Optional[Iterable[float]] = None):
        super().__init__(position or generate_position(), radius=COIN_RADIUS)

    def __str__(self):
        return f"Coin Object (x={self.x}, y={self.y})"