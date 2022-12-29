import numpy
#  from . import sprite, group 互相导入层级问题
import param
from .vec2d import hypot_percent
import sys
import inspect

SIZE_UNITS = ["bytes", "KiB", "MiB", "GiB", "TiB"]


def get_size(obj, seen=None):
    # from https://github.com/bosswissam/pysize
    """Recursively finds size of objects in bytes"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if hasattr(obj, '__dict__'):
        for cls in obj.__class__.__mro__:
            if '__dict__' in cls.__dict__:
                d = cls.__dict__['__dict__']
                if inspect.isgetsetdescriptor(d) or inspect.ismemberdescriptor(d):
                    size += get_size(obj.__dict__, seen)
                break
    if isinstance(obj, dict):
        size += sum((get_size(v, seen) for v in obj.values()))
        size += sum((get_size(k, seen) for k in obj.keys()))
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum((get_size(i, seen) for i in obj))

    if hasattr(obj, '__slots__'):  # can have __slots__ with __dict__
        size += sum(get_size(getattr(obj, s), seen) for s in obj.__slots__ if hasattr(obj, s))

    return size


def convert_size(n_bytes: int, fixed=1):
    unit_idx = 0

    while n_bytes > 1024 and unit_idx < len(SIZE_UNITS):
        n_bytes /= 1024
        unit_idx += 1

    return f"{round(n_bytes, fixed)} {SIZE_UNITS[unit_idx]}"


def count_range(center):
    x, y = center
    x_startup, y_startup = x // param.BLOCK_SIZE - param.DATA_SPREAD, y // param.BLOCK_SIZE - param.DATA_SPREAD
    return (
        x_startup * param.BLOCK_SIZE,
        y_startup * param.BLOCK_SIZE,
        (x_startup + param.DATA_SIZE) * param.BLOCK_SIZE,
        (y_startup + param.DATA_SIZE) * param.BLOCK_SIZE
    )


def filter_point(arr: numpy.ndarray):
    # arr.__le__(param.DATA_SIZE).all(), 即Less and Equal ( <= ), 等同于 (arr <= param.DATA_SIZE).all()
    # return arr.__le__(param.DATA_SIZE).all()
    # 不能为 arr <= param.DATA_SIZE, 最大索引值5, 即长6, 抛出IndexError: index 5 is out of bounds for axis 0 with size 5
    return ((0 <= arr) & (arr < param.DATA_SIZE)).all()


def filter_range(cls, coins, snakes) -> numpy.ndarray:
    """

    :param cls: vector.sprite.SnakeTrainer
    :param coins: vector.group.CoinGroup
    :param snakes: vector.group.SnakeGroup

    :return: numpy.ndarray

    [i] notice:
        batch_tensor [ y ][ x ]

    :return <torch.Tensor> - (5 x 5)
        :returns   [[float tensor, ...], ...]
        0: empty data
        1: other <Snake>s
        2: <coinGroup.Coin> position
        (before 3: self <Snake.SnakeHead> position)
        4: Bounds
    """

    tensor = numpy.zeros([param.DATA_SIZE, param.DATA_SIZE], )
    start_block = cls.start_position_index

    # TODO 1: SELF HEAD DATA
    tensor[param.DATA_SPREAD][param.DATA_SPREAD] = 1

    # TODO 2: COIN DATA
    for arr in filter(filter_point, [numpy.array(coin.array // param.BLOCK_SIZE - start_block, dtype=numpy.int)
                                     for coin in coins.coins]):
        x, y = arr
        tensor[y][x] = 2

    # TODO 3: OTHER SNAKES DATA
    for arr in filter(filter_point, [numpy.array(arr, dtype=numpy.int) for snake in (set(snakes.snakes) - {cls, })
                                     for arr in (snake.array // param.BLOCK_SIZE - start_block)]):
        x, y = arr
        tensor[y][x] = 3

    # TODO 4: BORDER DATA
    start_x, start_y = start_block
    end_x, end_y = start_block + param.DATA_SIZE - (param.WIDTH_BLOCK, param.HEIGHT_BLOCK)
    if start_y < 0:
        tensor[:-start_y] = 4
    elif end_y > 0:
        tensor[-end_y:] = 4
    if start_x < 0:
        tensor[:][..., :-start_x] = 4
    elif end_x > 0:
        tensor[:][..., -end_x:] = 4

    return tensor


def position_to_degree(x, y) -> float:
    r"""
    y
    ^
    ┊
    ┊ A
    ┊\
    ┊ \
h   ┊  \
    ┊   \  B
    └┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈> x
      w

      A -> B

      tan A = w / h
      deg A = arc-tan A / Pi * 180
      ( B = 180 - A )

      center: A

    Position to Degree (Python achieve):
        >>> tan = numpy.array(x/y)
        >>> arc = numpy.math.atan(tan)
        >>> deg = arc / numpy.math.pi * 180
        >>> return deg
    function zipped

    e.g.:
        >>> position_to_degree(1, 2)
        >>> 26.56505117707799
        >>>
    """
    return numpy.math.degrees(numpy.math.atan2(x, y))


def degree_to_position(deg, total=1.) -> numpy.ndarray:
    r"""
    Position to Degree (Python achieve):
        ...

    Reverse:
      inpput [ deg ]:
        >>> rad = deg * numpy.math.pi / 180
        >>> tan = numpy.math.tan(rad)  # value of x/y
        >>> x, y = hypot_percent([tan, 1])
      output [percent x, y ]

    function zipped

    e.g.:
        >>> degree_to_position(11)
        >>> numpy.array([0.190809  , 0.98162718])


    validate:
        >>> degree_to_position(position_to_degree(108, 79))
        >>> numpy.array([0.80711718, 0.59039127])

        >>> hypot_percent([108, 79])
        >>> numpy.array([0.80711718, 0.59039127])

    """
    return hypot_percent([numpy.math.tan(numpy.math.radians(deg)), 1], total=total)
