import numpy
from typing import *


def _limit(num, max_=100, min_=1):
    return max_ if num > max_ else (min_ if num < min_ else num)


def get_distance(pos1, pos2):
    return numpy.hypot(
        pos1[0] - pos2[0],
        pos1[1] - pos2[1],
    )


def hypot_percent(arr, total: Optional[float] = 1.) -> numpy.ndarray:
    return arr / numpy.hypot(*arr) * total


class Point2d(object):
    """
    1 Dimension Array.

    :param x, y

    e.g.
    >>> Point2d(1, 2)
    Point2d(1, 2)
    >>> Point2d(3., 2) + (32, 1)
    Point2d(35.0, 3.0)
    >>> (Point2d(3., 2) + (32, 1)).get_length()
    35.12833614050059
    (type: `numpy.float64`)

    property <decorate function> features:
    >>> point = Point2d(3., 8.)
    >>> Point2d.x = 2
    >>> point.x
    2
    >>> point
    Point2d(2, 8.0)
    """

    def __init__(self, x: Union[int, float], y: Union[int, float]):
        self.array = numpy.array([x, y])

    @property
    def x(self) -> Union[int, float]:
        return self.array[0]

    @x.setter
    def x(self, value: Union[int, float]):
        self.array[0] = value

    @property
    def y(self) -> Union[int, float]:
        return self.array[1]

    @y.setter
    def y(self, value: Union[int, float]):
        self.array[1] = value

    def __add__(self, other: Tuple[Union[int, float], Union[int, float]]):
        assert len(other) == 2
        return Point2d(
            self.x + other[0],
            self.y + other[1]
        )

    __radd__ = __add__

    def __len__(self) -> int:
        return 2

    def __str__(self) -> str:
        return "Point2d(%s, %s)" % (self.x, self.y)

    __repr__ = __str__

    def __getitem__(self, item):
        return self.array[item]

    def get_length(self) -> Union[int, float]:
        return numpy.hypot(self.x, self.y)

    def set_length(self, length: Union[int, float]) -> "Point2d":
        length_ = self.get_length()
        self.x, self.y = self.x / length_ * length, self.y / length_ * length
        return self


class DynamicArray2d(object):
    """
    2 Dimensions Array.
    类似于java ArrayList
    """

    def __init__(self, length: int):
        self._array = numpy.zeros([length, 2])
        self._size = 0
        self._array_size = length

    def __repr__(self):
        return repr(self.array)

    def fill(self, value: Union[int, float, complex]):
        self._array.fill(value)

    @property
    def length(self) -> int:
        return self._size

    @property
    def array(self) -> numpy.ndarray:
        return self._array[:self._size]

    def append(self, value: Tuple[Union[int, float]]) -> numpy.ndarray:
        value = numpy.array(value)
        if self._size >= self._array_size:
            self._array_size += round(_limit(self._array_size * 0.5))
            self._array = numpy.resize(self._array, [self._array_size, 2])
        self._array[self._size] = value
        self._size += 1
        return value

    def insert(self, value: Tuple[Union[int, float]], index: int = 0) -> numpy.ndarray:
        value = numpy.array(value)
        self._array = numpy.insert(self._array, index, value, axis=0)
        self._size += 1
        self._array_size += 1
        return value

    def add_values(self, value, times: int) -> None:
        for _ in range(times):
            self.append(value)

    def extend(self, values: Iterable[Tuple[Union[int, float]]]) -> None:
        for value in values:
            self.append(value)

    def delete(self, index: int) -> None:
        assert index < self._size, "list index out of range."
        self._array = numpy.delete(self._array, index, axis=0)
        self._size -= 1
        self._array_size -= 1

    def get(self, index: int = 0) -> Tuple[Union[int, float]]:
        assert index < self._size, "list index out of range."
        return self._array[index]

    def pop(self, index: int = -1) -> Tuple[Union[int, float]]:
        response = self.get(index)
        self.delete(index)
        return response

    def __len__(self):
        return self._size
