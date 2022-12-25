import time

from param import *
from .circle import *
from .vec2d import hypot_percent
from .color import generate_color, generate_background
from typing import *
import numpy


def generate_position():
    return numpy.array([
        numpy.random.randint(BLOCK_SIZE, WIDTH_BLOCK * (BLOCK_SIZE - 1)),
        numpy.random.randint(BLOCK_SIZE, HEIGHT_BLOCK * (BLOCK_SIZE - 1)),
    ])


def generate_direction():
    return hypot_percent(numpy.random.rand(2), SNAKE_BODY_STRIDE)


def snake_combination_collide(s1: "BaseSnake", s2: "BaseSnake") -> Tuple[bool, bool]:
    """
    :return: s1 was collided, s2 was collided
    """
    response = s1.snake_collided(s2)
    if response is not False:
        if response == 0:  # 双方碰撞头部
            return True, True
    return not not response, not not s2.snake_collided(s1)  # 包含双方都由对方身体碰撞头部 (由自身身体碰撞头部不会视为碰撞)


class Migration(object):
    """
    Migration 机制:
        1. 当客户端进入时, 提出全部数据
            取出的数据是即刻生成 即刻释放的, 因为数据的生成不会占用过大的内存 (4 KiB * n ± 1 KiB),
            反而缓存json过的数据占用内存反而大, 尤其是动态数据, 每帧还需刷新, 客户端的增减不是大幅度的,
            约 ((409 Bytes * b ± 1.5KiB) * n)

            (两个数据来自动态内存计算工具 NpStat, 有可能不太准哈仅供参考)

        2. 在进行时, 因为每次发全部数据不大现实,
            为了节省带宽, 节省网络传输带来的延迟, 减少损失的性能, 因此只更改变化的数据, 其他固定的数据
            (如蛇方向未变, 交给客户端javascript计算)         即采用客户端渲染计算
            并且还有一点就是 如果每次都发送所有数据, 反而会占用客户端更多的处理, 计算时间, 加上网络和带宽的延迟, 帧率会大幅降低
            依赖于tcp传输的准确性, 依赖于websocket协议来解决tcp分包粘包, 每次计算几乎都会无误(除了网络故障, 应用层丢失)

            这也是Minecraft的区块刷新的网络传输方法之一 (不过人家是udp, 大概因为要求数据准确率不是极高, 且通过双方算法弥补, 否则不可能每帧近GB传输吧)
                                                (别问我是怎么知道的)
        3. Migrations 机制
        100条蛇, Migration约0-4000bytes (平均1210bytes, 1.12KiB), 全部数据 12301bytes (12KiB)
            计算实际全部流量: data * tick * client
    """

    def __init__(self):
        self.migration_ = {}

    def release_migration(self):
        self.migration_ = {}

    def add_migration(self, key, value):
        self.migration_[key] = value

    @property
    def has_migration(self) -> bool:
        return bool(self.migration_)

    def add_number_migration(self, key, value):
        self.migration_[key] = self.migration_.get(key, 0) + value

    def add_list_migration(self, key, value):
        (self.migration_[key].append(value)) if key in self.migration_ else (self.migration_.setdefault(key, [value, ]))

    def add_dict_migration(self, key, value, sub_value):
        if key in self.migration_:
            self.migration_[key][value] = sub_value
        else:
            self.migration_[key] = {
                value: sub_value
            }

    @property
    def migration(self):
        migrate = self.migration_
        self.release_migration()
        return migrate

    def get_data(self) -> dict:
        pass


class BaseSnake(CircleArray, Migration):
    def __init__(self, name="", color: Optional[list] = None, location: Optional[List[float]] = None,
                 direction: Optional[list] = None, length=3, parent=None):
        super().__init__(length, radius=BLOCK_RADIUS)
        Migration.__init__(self)
        self.color = color or generate_color()
        self.background = generate_background(self.color)
        self.name = name

        assert parent
        self.parent = parent

        self.add_values(location or generate_position(), length)
        self.direction: numpy.ndarray = numpy.array(direction or generate_direction())
        self.alive = True
        self.head = numpy.array([0, 0])

        self.score = 0
        self.score__added = 0
        self.score__queue = 0
        self.kill = 0
        self.kill__added = 0

    def death(self):
        self.alive = False
        self.add_migration("alive", self.alive)

    def move(self) -> None:
        self.delete(-1)
        self.head = self.insert(self.get(0) + self.direction)

        # do not add migration

    def add_body(self, num=1) -> None:
        for _ in range(num):
            self.append(self.get(-1))

    def update_direction(self, direction):
        self.direction = hypot_percent(direction, SNAKE_BODY_STRIDE)
        self.add_migration("direction", self.direction)

    def update_direction_from_point(self, position):
        self.update_direction(self.get_head_distances(position))

    def get_head_distances(self, pos) -> numpy.ndarray:
        (x1, y1), (x2, y2) = pos, self.head
        return numpy.array([x1 - x2, y1 - y2])

    def update(self):
        if not self.alive:
            return

        self.move()
        self.score_detection()
        self.killed_detection()

    def __str__(self):
        return f"Snake Object (name={self.name}, length={self._size}, direction={self.direction})"

    def add_killed(self, val=1):
        self.kill__added += val

    def killed_detection(self):
        if self.kill__added:
            self.kill += self.kill__added
            self.add_migration("kill", self.kill__added)
            self.kill__added = 0

    def add_score(self, val=1):
        self.score__added += val

    def score_detection(self):
        if self.score__added:
            self.score += self.score__added
            queue = self.score__queue + self.score__added
            score__ready = queue // 5
            self.score__queue = queue % 5
            self.add_body(score__ready)

            self.add_migration("score", self.score__added)
            self.score__added = 0

            if score__ready:
                self.add_migration("body", self.score__added)

    def snake_collided(self, snake: "BaseSnake") -> bool:
        return self.element_is_collide_array(0, snake)

    def border_collide(self) -> bool:
        x, y = self.head
        return x - self.radius < 0 or y - self.radius < 0 or \
            x + self.radius > WIDTH or y + self.radius > HEIGHT

    def get_data(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "background": self.background,
            "direction": self.direction,
            "array": self.array,
            "kill": self.kill,
            "score": self.score,
            "length": self.length,
        }


class SnakePlayer(BaseSnake):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def gradient_up(self):
        pass

    def gradient_down(self):
        pass

    def gradient_left(self):
        pass

    def gradient_right(self):
        pass


class JuniorSnakeRobot(BaseSnake):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def refresh_direction(self):
        self.update_direction(generate_direction())

    def _border_collide_detection(self) -> bool:
        x, y = self.head + self.direction
        return x - self.radius < 0 or y - self.radius < 0 or \
            x + self.radius > WIDTH or y + self.radius > HEIGHT

    def collide_detection(self):
        breakup = 0
        while self._border_collide_detection() and breakup < 100:
            self.refresh_direction()
            breakup += 1

    def update(self):
        resp = self.parent.get_closest_coin(self)
        if resp:
            self.update_direction_from_point(resp)
        self.collide_detection()
        super().update()


class SeniorSnakeRobot(JuniorSnakeRobot):
    def __promise(self, idx, positive: 1):
        self.direction[idx] = positive * abs(numpy.random.randn(1))

    def _promise_x(self, positive: 1):
        self.__promise(0, positive)

    def _promise_y(self, positive: 1):
        self.__promise(1, positive)

    def _intelligence_border_collide_detection(self) -> None:
        x, y = self.head + self.direction
        if x - self.radius < 0:
            self._promise_x(1)
        elif x + self.radius > WIDTH:
            self._promise_x(-1)
        if y - self.radius < 0:
            self._promise_y(1)
        elif y + self.radius > HEIGHT:
            self._promise_y(-1)
        self.update_direction(self.direction)

    def refresh_direction(self):
        self._intelligence_border_collide_detection()

    def collide_detection(self):
        self._intelligence_border_collide_detection()


class SnakeTrainer(BaseSnake):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reward_total = 0.
        self.reward_current = 0.

    def handle(self, reward):
        data = self.generate_data
        print(reward)

    @property
    def generate_data(self):
        return self.parent.detect_train_data(self)

    def update(self):
        super().update()
        self.reward_total += self.reward_current
        self.handle(self.reward_current)
        self.reward_current = 0.

    def killed_detection(self):
        self.reward_current += self.kill__added * 0.5
        super().killed_detection()

    def score_detection(self):
        self.reward_current += self.score__added * 0.1
        super().score_detection()

    def death(self):
        self.reward_current -= 1
        super().death()


class Coin(Circle):
    def __init__(self, score: int = 1, position: Optional[Iterable[float]] = None, index=0):
        super().__init__(generate_position() if position is None else position, radius=BLOCK_RADIUS)
        self.score = score
        self.index = index
        self.generated = 0
        self.natural = False

    def setNatural(self):
        self.natural = True
        self.generated = int(time.time())

    @property
    def is_clear(self) -> bool:
        return self.natural and ((time.time() - self.generated) > NATURAL_COIN_DISAPPEAR)

    def __str__(self):
        return f"Coin Object (x={self.x}, y={self.y})"

    @property
    def data(self):
        return (self.x, self.y), self.score
