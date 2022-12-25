import numpy
from . import sprite, group
import param


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


def filter_range(cls: "sprite.SnakeTrainer", coins: "group.CoinGroup", snakes: "group.SnakeGroup") -> numpy.ndarray:
    tensor = numpy.zeros([param.DATA_SIZE, param.DATA_SIZE], )
    start_block = cls.head // param.BLOCK_SIZE - param.DATA_SPREAD

    tensor[param.DATA_CENTER][param.DATA_CENTER] = 1
    for arr in filter(filter_point, [numpy.array(coin.array // param.BLOCK_SIZE - start_block, dtype=numpy.int)
                                     for coin in coins.coins]):
        x, y = arr
        tensor[y][x] = 2

    for arr in filter(filter_point, [numpy.array(arr, dtype=numpy.int) for snake in (set(snakes.snakes) - {cls, })
                                     for arr in (snake.array // param.BLOCK_SIZE - start_block)]):
        x, y = arr
        tensor[y][x] = 3

    return tensor
