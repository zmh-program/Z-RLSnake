from . import vec2d
from typing import *


def circle_collide(pos1, radius1, pos2, radius2) -> bool:
    return vec2d.get_distance(
        pos1, pos2,
    ) <= (radius1 + radius2)


class Circle(vec2d.Point2d):
    def __init__(self, position: Iterable[float], radius=5):
        super().__init__(*position)
        self.radius = radius

    def _is_collide(self, pos, radius) -> bool:
        return circle_collide(self.array, self.radius, pos, radius)

    def is_collide_circle(self, circle: "Circle") -> bool:
        return self._is_collide(circle.array, circle.radius)

    def is_collide_array(self, array: "CircleArray") -> bool:
        for arr in array.array:
            if self._is_collide(arr, array.radius):
                return True
        return False

    def get_collide_indexes(self, array: "CircleArray") -> Iterable[int]:
        for idx, arr in enumerate(array.array):
            if self._is_collide(arr, array.radius):
                yield idx


class CircleArray(vec2d.DynamicArray2d):
    def __init__(self, length: int = 3, radius=5):
        super().__init__(length)
        self.radius = radius

    def is_collide_array(self, array: "CircleArray") -> bool:
        for arr in self.array:
            for arr_ in array.array:
                if circle_collide(
                    arr, self.radius,
                    arr_, array.radius,
                ):
                    return True
        return False

    def element_is_collide_array(self, index: int, array: "CircleArray") -> Union[int, "False"]:
        arr = self.get(index)
        for idx_, arr_ in enumerate(array.array):
            if circle_collide(
                arr, self.radius,
                    arr_, array.radius,
            ):
                return idx_
        return False

    def get_collide_indexes(self, array: "CircleArray") -> Iterable[Tuple[int, int]]:
        for idx, arr in enumerate(self.array):
            for idx_, arr_ in enumerate(array.array):
                if circle_collide(
                        arr, self.radius,
                        arr_, array.radius,
                ):
                    yield idx, idx_
