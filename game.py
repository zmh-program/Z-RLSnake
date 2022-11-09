from time import time
import logging
import math
from typing import Tuple

import numpy
import pygame
import random
import sys
import torch

from parameter import *

BoundSize = block_size * 2

# About Interface and Display:
pygame.init()
pygame.display.set_caption("Snake Deep Reinforcement Learning")

BLACK = (0, 0, 0)
BACKGROUND_COLOR = BLACK
LINE_COLOR = (180, 180, 180)
WHITE = (255, 255, 255)
DEBUG_COLORS = {
    0: WHITE,
    1: (255, 0, 0),
    2: (0, 162, 255),
    3: LINE_COLOR,
    4: (255, 0, 100),
}

# About Logging:
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def relu(num: (int, float)) -> (int, float):
    return 0 if is_negative(num) else num


def is_negative(num: (int, float)) -> bool:
    return num < 0


def to_pygame(x, y):
    return x, -y


def convert_number(num: (int, float), conv) -> (int, float):
    return -num if conv else num


def absolute_count(target_value, direct_value):
    return target_value + convert_number(direct_value, is_negative(target_value))


def is_similar(*nums) -> bool:
    return len(set(map(is_negative, nums))) == 1


def format_value(array: numpy.ndarray, value: (int, float), _hypot: bool = True) -> Tuple[float, numpy.ndarray]:
    """get the percent of the array."""
    total = math.hypot(*array) if _hypot else sum(
        list(map(abs, map(int, array))))  # math.hypot -> math.sqrt(x**2, y**2, ...)
    return total, array / total * value


def get_percent_total(array: numpy.ndarray, index: int, absolution=True) -> float:
    return (abs(array[index]) if absolution else array[index]) / sum(abs(array) if absolution else array)


def zero_(value: (int, float)) -> (int, float):
    return 0 if is_negative(value) else value


def timeit(objname: str, display=True):
    def setup_function(func_name):
        def _exec_function(*args, **kwargs):
            if display:
                start_time = time()
                _resp = func_name(*args, **kwargs)
                logger.debug("Execute the function %s, timeit %0.3f" % (objname.title(),
                                                                        time() - start_time))
                return _resp
            else:
                return func_name(*args, **kwargs)

        return _exec_function

    return setup_function


class Snake(object):
    class SnakeHead(pygame.sprite.Sprite):
        def __init__(self, parent, pos):
            pygame.sprite.Sprite.__init__(self)
            self.parent: Snake = parent
            self.image = pygame.Surface([block_size, block_size])
            self.image.set_colorkey(BLACK)
            # 含有黑色边框的圆蛇头
            pygame.draw.circle(self.image, self.parent.color, (radius, radius), radius - 1)
            pygame.draw.circle(self.image, (10, 10, 10), (radius, radius), radius, 1)
            # 黑色边框 左右眼
            pygame.draw.circle(self.image, WHITE, (radius / 2, radius), radius / 3 - 1)
            pygame.draw.circle(self.image, (10, 10, 10), (radius / 2, radius), radius / 3, 1)
            pygame.draw.circle(self.image, WHITE, (block_size - radius / 2, radius), radius / 3 - 1)
            pygame.draw.circle(self.image, (10, 10, 10), (block_size - radius / 2, radius), radius / 3, 1)
            self.rect = self.image.get_rect()
            self.rect.center = pos

        def update(self, pos):
            self.rect.center = pos
            self.death_state_test()

        def death_state_test(self):
            x, y = self.rect.center
            r = block_size / 4 / 2
            if not ((0 + r < x < width - r) and (0 + r < y < height - r)):  # collide the bound
                self.parent.handler.snake_died(self.parent)
            elif self.parent.handler.touch_another_snake_body(self.parent):  # collide the snake
                self.parent.handler.snake_died(self.parent)
                return True

    class SnakeBody(pygame.sprite.Sprite):
        def __init__(self, color):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface([block_size, block_size])
            self.image.set_colorkey(BLACK)
            # 含有黑色边框的圆蛇身
            pygame.draw.circle(self.image, color, (radius, radius), radius - 1)
            pygame.draw.circle(self.image, (10, 10, 10), (radius, radius), radius, 1)
            self.rect = self.image.get_rect()

    class SnakeBodyGroup(pygame.sprite.Group):
        def __init__(self, color):
            pygame.sprite.Group.__init__(self)
            self.color = color

        def update(self, pos):
            pos = list(pos)
            sprs = self.sprites()
            num = len(pos) - len(sprs)
            if num > 0:
                self.add([Snake.SnakeBody(self.color) for _ in range(num)])

        def snakeCollide(self, i):
            return bool(pygame.sprite.spritecollide(i, self, False))

    def __init__(self, handlerObj: object, name="", length=3, color=None):
        self.name = name
        self.handler = handlerObj
        if color is None:
            color = (random.randint(20, 255),
                     random.randint(20, 255),
                     random.randint(20, 255))
        self.color = color
        self.location_tensor = [(random.randint(block_size, width - block_size),
                                 random.randint(block_size, height - block_size))] * length
        self.head = Snake.SnakeHead(self, self.location_tensor[0])
        self.body = Snake.SnakeBodyGroup(self.color)
        self.score = int()
        self.__score_value = int()
        self.kill = int()
        self.speed = radius * 1.5
        self.over = False
        self.time = time()
        self.direction = numpy.array([0, 0])

    def filter_element(self, x_size, y_size) -> iter:
        """
        :param:
        x_size : (max_x, min_x)
        y_size : (max_y, min_y)
        """

        (max_x, min_x), (max_y, min_y) = x_size, y_size
        for x, y in self.location_tensor:
            if min_x <= x < max_x and min_y <= y < max_y:
                yield int((x - min_x) // block_size), int((y - min_y) // block_size)

    def is_alive(self):
        return not self.over

    def is_death(self):
        return self.over

    def update(self):
        if self.is_alive():
            self.add_length()
            self.add_score()
            del self.location_tensor[-1]
            self.location_tensor.insert(0, self.to_direction(*self.location_tensor[0]))
            self.body.update(reversed(self.location_tensor[1:]))
            self.head.update(self.location_tensor[0])  # reversed和先画头在画身体目的->转向时蛇头和转过去的身体在前
        self.updateEvent()

    def updateEvent(self):
        pass

    def count_direction(self, pos1: Tuple[float, float], pos2=None) -> Tuple[float, numpy.ndarray]:
        (x1, y1), (x2, y2) = pos1, (pos2 or self.location_tensor[0])
        return format_value(numpy.array([x1 - x2, y1 - y2]), self.speed)

    def set_direction(self, TargetDirectionPosition: tuple, FromTargetPosition: (tuple, None) = None):
        _, self.direction = self.count_direction(TargetDirectionPosition, FromTargetPosition)

    def to_direction(self, x, y):
        return (x + self.direction[0],
                y + self.direction[1])

    def return_direction(self):
        return self.direction

    def add_length(self):
        while self.score // SCORE_TO_LENGTH > self.get_length() - 3:
            self.location_tensor.append(self.location_tensor[-1])
        return

    def get_length(self):  # -> int
        return len(self.location_tensor)

    def get_random_direction(self):
        _, self.direction = self.count_direction((random.randint(0, width),
                                                  random.randint(0, height)))

    def add_score(self):
        score = self.handler.collide_coin(self.head)  # ≥ 0
        self.score += score

    def _get_data(self):
        return (
            self.name,
            self.direction,
            self.location_tensor,
            self.speed,
            self.is_alive(),
        )


class snake_of_player(Snake):
    def __init__(self, handlerObj, name="player", length=3, color=(255, 0, 0)):
        super(snake_of_player, self).__init__(handlerObj, name, length, color)
        # self.get_random_direction()
        self.turn_value = self.speed // 5
        self.set_direction([random.randint(0, width), random.randint(0, height)])

    def set_direction(self, *args):
        super(snake_of_player, self).set_direction(*args[::-1] if args else [pygame.mouse.get_pos()])
        # < args[::-1] > is the same as < reversed(args) >

    def convert_direction(self, conv: bool) -> None:
        self.direction = format_value(numpy.array([
            absolute_count(self.direction[0], convert_number(self.turn_value, conv)),
            absolute_count(self.direction[1], convert_number(self.turn_value, not conv))
        ]), self.speed)[1]

    def LEFT(self) -> None:
        self.convert_direction(False) if is_similar(*self.direction) else self.convert_direction(True)

    def RIGHT(self) -> None:
        self.convert_direction(False) if not is_similar(*self.direction) else self.convert_direction(True)

    def UP(self) -> None:
        x_dir, y_dir = self.direction
        if x_dir == 0. and is_negative(y_dir):
            return
        elif is_negative(x_dir):  # in 2, 3 quadrants.
            self.RIGHT()
            if self.direction[0] > 0:
                self.direction[0] = 0.
        else:
            self.LEFT()
            if self.direction[0] < 0:  # in 1, 4 quadrant and 0.
                self.direction[0] = 0.

    def DOWN(self) -> None:
        x_dir, y_dir = self.direction
        if x_dir == 0. and not is_negative(y_dir):
            return
        elif not is_negative(x_dir):  # in 1, 4 quadrant and 0.
            self.RIGHT()
            if self.direction[0] < 0:
                self.direction[0] = 0.
        else:
            self.LEFT()
            if self.direction[0] > 0:  # in 2, 3 quadrants.
                self.direction[0] = 0.

    def pressedHandler(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.LEFT()
        elif key[pygame.K_RIGHT]:
            self.RIGHT()
        elif key[pygame.K_UP]:
            self.UP()
        elif key[pygame.K_DOWN]:
            self.DOWN()


class snake_of_robot(Snake):
    def __init__(self, handlerObj, target=0, length=3, color=None):
        super(snake_of_robot, self).__init__(handlerObj, f"robot {target}", length, color)
        self.set_direction()

    def run(self):
        try:
            self.head.rect.center = self.to_direction(*self.location_tensor[0])
            x, y = self.head.rect.center
            r = block_size / 4 / 2
            i = False
            while (((not ((0 + r < x < width - r) and (0 + r < y < height - r))) or
                    self.handler.touch_another_snake_body(self)) and r < fps):
                r += 1  # 运行超时
                self.get_random_direction()
                self.head.rect.center = self.to_direction(*self.location_tensor[0])
                x, y = self.head.rect.center
                i = True
            return i
        except AttributeError:
            return

    def set_direction(self, *args):
        self.direction = super(snake_of_robot, self).count_direction(
            min(self.handler.get_coin_sprites(),
                key=lambda spr: super(snake_of_robot, self).count_direction(spr.rect.center)[0]).rect.center
        )[1]

    def updateEvent(self):
        if super(snake_of_robot, self).is_alive() and (not self.run()):
            self.set_direction()


class snake_of_ai(Snake):
    def __init__(self, handlerObj, length=3, color=(255, 0, 0)):
        super(snake_of_ai, self).__init__(handlerObj, "AI", length, color)
        self._score_before = int()
        self._kill_before = int()
        self.reward = int()
        self.range = block_size * 1.2

        self.queue = []

    def get_reward(self) -> float:
        return self.reward

    def get_bound_reward(self, position=None) -> float:
        x, y = position or self.location_tensor[0]
        return - (relu(self.range - x) + relu(x - (width - self.range)) + relu(self.range - y) + relu(
            y - (height - self.range))) / 3.2

    def get_reward_once(self) -> float:
        reward = (self.score - self._score_before) * 6 + round(
            relu(self.range * block_size - self.get_closest_coin()) * 0.007, 1) + (
                             self.kill - self._kill_before) * 15 + self.get_bound_reward() + (
                     0 if self.is_alive() else - 20) / 10
        self._score_before = self.score
        self._kill_before = self.kill
        self.reward += reward
        return reward

    def get_distance(self, x1: int, y1: int) -> numpy.ndarray:
        return numpy.array([x1 - self.location_tensor[0][0], y1 - self.location_tensor[1][1]])

    def get_closest_coin(self) -> float:
        return sum(abs(self.get_closest_coin_distance()))

    def get_closest_coin_distance(self) -> numpy.ndarray:
        return min([self.get_distance(*coin.rect.center) for coin in
                    self.handler.get_coin_sprites()], key=lambda x: sum(abs(x)))

    @staticmethod
    def degree_to_direction(degree: (int, float), speed: (int, float)) -> numpy.ndarray:
        """
        :param speed: direction speed
        :param degree: 0~360deg
        :return List[x_direction, y_direction]

        """

        """
        [i] notice:
        degree ↑
                      90°
                       ↑
              x↑y↑     |      x↑y↓ 
        (2 quadrant)   |    (1 quadrant)
             0° -------+-------→ 180°
           360°  x↓y↓  |      x↓y↓
        (3 quadrant)   |    (4 quadrant)
                       270°

        :return <direction list [x, y]>
        """

        if 0 <= degree <= 90:  # 2 qua. and (0, 90), x为负且绝对值在缩小(即增大), y为正且在增大
            x, y = degree - 90, degree
        elif 90 < degree <= 180:  # 1 qua. and 180, x为正且在增大, y为正且在缩小
            x, y = degree - 90, 180 - degree
        elif 180 < degree <= 270:  # 4 qua. and 270, x为正且在缩小, y为负且绝对值在增大(即缩小)
            x, y = 270 - degree, 180 - degree
        else:  # 3 qua.  x为负且绝对值在增大(即缩小), y为负且绝对值在缩小(即增大)
            x, y = 270 - degree, degree - 360

        # to_pygame: pygame坐标遵循第四象限, 以左上角为起点真假, 将其以第一象限规则的坐标y轴转为相反数, x轴不变.
        return format_value(numpy.array(to_pygame(x, y)), speed)[1]

    @staticmethod
    def direction_to_degree(direction: Tuple[float, float]) -> float:
        x, y = to_pygame(*direction)
        direction_array = numpy.array([x, y])
        if is_negative(x) and not is_negative(y):
            return get_percent_total(direction_array, 1) * 90
        elif not is_negative(x) and not is_negative(y):
            return (get_percent_total(direction_array, 0) + 1) * 90
        elif not is_negative(x) and is_negative(y):
            return (get_percent_total(direction_array, 1) + 2) * 90
        elif is_negative(x) and is_negative(y):
            return (get_percent_total(direction_array, 0) + 3) * 90

    def get_action_from_direction(self, direction: Tuple[float, float]) -> int:
        return round(self.direction_to_degree(direction)) // (360 // ACTION_NUMBER)

    def set_action(self, action: int):
        self.direction = self.degree_to_direction(action * (360 // ACTION_NUMBER), self.speed)

    def goto_closest_coin_as_action(self) -> int:
        """
        Queue 机制: 预防两个金币距离相同.
        :return: direction ( Tuple[float, float] )
        """
        distance = self.get_closest_coin_distance()
        self.queue.append(distance)
        if len(self.queue) >= 3:
            if (self.queue[0] == self.queue[2]).all():  # ValueError: The truth value of an array with more than one element is ambiguous
                distance = self.queue.pop(1)
            else:
                del self.queue[0]
        return self.get_action_from_direction(tuple(format_value(distance, self.speed)[1]))


class coinGroup(pygame.sprite.Group):
    coinFig = pygame.Surface((20, 20))
    coinFig.fill(BLACK)
    pygame.draw.circle(coinFig, (255, 127, 39), (10, 10), 10)
    coinFig.set_colorkey(BLACK)

    class Coin(pygame.sprite.Sprite):
        def __init__(self, pos=None, level=1):
            pygame.sprite.Sprite.__init__(self)
            self.image = coinGroup.coinFig
            self.rect = self.image.get_rect()
            self.create_time = time()
            if pos is None:
                pos = (random.randint(1, width // block_size - 2) * block_size,
                       random.randint(1, height // block_size - 2) * block_size)
            self.rect.topleft = pos
            self.pos = pos
            self.level = level

    def __init__(self, max_coin_num=10):
        self.max = max_coin_num
        pygame.sprite.Group.__init__(self, [coinGroup.Coin() for _ in range(max_coin_num)])

    def coinLack(self):
        self.add(*[coinGroup.Coin() for _ in range(self.max - len(self.sprites()))])

    def snakeDied(self, args: list):
        for x, y in args:
            r = block_size // 2
            if (0 + r < x < width - r) and (0 + r < y < height - r):
                self.add(coinGroup.Coin((x, y), level=SCORE_TO_LENGTH))

    def draw(self, *args):  # 重写原方法,提高性能
        for spr in self.sprites():
            if isinstance(spr, coinGroup.Coin):
                if time() - spr.create_time > 30:
                    self.remove(spr)

    def filter_element(self, x_size, y_size) -> iter:
        """
        x_size : (max_x, min_x)
        y_size : (max_y, min_y)
        """

        (max_x, min_x), (max_y, min_y) = x_size, y_size
        for spr in self.sprites():
            spr: coinGroup.Coin
            x, y = spr.pos
            if min_x <= x < max_x and min_y <= y < max_y:  # < = ... <= max_x : out of bounds with <tensor_length>
                yield int((x - min_x) // block_size), int((y - min_y) // block_size)


class gameHandler(object):
    def __init__(self, episode=0):
        self.Coin_group: (coinGroup, None) = None
        self.player_control: (snake_of_player, snake_of_ai) = None
        self.snakes = list()

        self.__episode = episode

        self.clock = pygame.time.Clock()
        self.robot_no = int()

    def addEpisode(self, episode: int = 0):
        self.__episode += 1
        if episode:
            self.__episode = episode

    def getEpisode(self) -> int:
        return self.__episode

    def is_alive(self) -> bool:
        return self.player_control.is_alive()

    def is_died(self) -> bool:
        return not self.player_control.is_alive()

    def out_of_range(self) -> bool:  # abandon
        return abs(self.player_control.count_direction(pygame.mouse.get_pos())[0]) > block_size * 2

    def get_coin_sprites(self) -> list:
        return self.Coin_group.sprites()

    def snake_died(self, snake: Snake, not_ref=True):
        if snake.is_alive():  # 防止多次调用.
            snake.over = True
            snake.body.empty()
            del snake.head, snake.body
            if snake in self.snakes:
                self.snakes.remove(snake)
            if not_ref:  # 防止为self.reset方法中调用
                self.Coin_group.snakeDied(snake.location_tensor)
                self.robot_no += 1
                self.snakes.append(snake_of_robot(self, self.robot_no))

    def new_snake_of_robot(self) -> None:
        self.robot_no += 1
        self.snakes.append(snake_of_robot(self, self.robot_no))

    def update(self):
        self.eventHandler()
        for s in self.snakes:
            assert isinstance(s, Snake)
            if isinstance(s, Snake) and s.is_alive():
                s.update()

    def run_once(self) -> None:
        self.update()
        pygame.display.update()

    def run_while_alive(self):  # main.py
        self.reset()
        while self.is_alive():
            self.run_once()

    def touch_another_snake_body(self, snake):
        if snake not in self.snakes:
            return False
        for s in self.filter(snake):
            s: Snake
            if s.body.snakeCollide(snake.head):
                s.kill += 1
                return True
        return False

    def filter(self, exceptSnake: Snake):
        return filter(lambda _snake: _snake.is_alive(), set(self.snakes) - {exceptSnake})

    def terminate(self):
        pygame.display.quit()
        pygame.quit()
        self.terminateEvent()
        sys.exit()

    def terminateEvent(self):
        pass

    def eventHandler(self) -> None:
        pass

    def collide_coin(self, head: Snake.SnakeHead) -> int:
        value = sum([_coin.level for _coin in pygame.sprite.spritecollide(head, self.Coin_group, True)
                     if isinstance(_coin, coinGroup.Coin)])
        if value > 0:
            self.Coin_group.coinLack()
        return value

    def init_player_c(self):  # inherit
        return snake_of_player(self, "me")

    def reset(self):
        if isinstance(self.Coin_group, coinGroup):
            for snake in self.snakes:
                self.snake_died(snake, False)
            self.snakes = list()
            self.Coin_group.empty()
            del self.Coin_group

        self.Coin_group = coinGroup(max_coin_num=COINS)

        [self.new_snake_of_robot() for _ in range(ROBOT_NUMBER)]
        self.player_control = self.init_player_c()
        self.snakes += [self.player_control]


class RLenvironment(gameHandler):
    input_dim = 1

    player_control: snake_of_ai

    def __init__(self, episode=0):
        super(RLenvironment, self).__init__(episode)
        self.batch_c = None
        self.tensor = None

    @staticmethod
    def center_size(x, y):
        start_x_size = (x // block_size) - tensor_radius
        start_y_size = (y // block_size) - tensor_radius
        return ((start_x_size + tensor_length) * block_size, start_x_size * block_size), \
               ((start_y_size + tensor_length) * block_size, start_y_size * block_size)

    def filter_element(self) -> (torch.Tensor, (int, int)):
        """
        [i] notice:
            batch_tensor 以y为一维数组的组合, 先索引y, 再索引x坐标
            tensor[y][x] 而不是 tensor[x][y]

        :return <torch.Tensor> - (tensor_length x tensor_length) - dim 2
            :returns   [[tensor(int), ...], ...]
            0: empty data
            1: other <Snake>s
            2: <coinGroup.Coin> position
            (before 3: self <Snake.SnakeHead> position)
            4: Bounds
        """
        batch_tensor = torch.zeros(tensor_length, tensor_length, dtype=default_tensor_dtype)

        x_size, y_size = self.center_size(*self.get_head())
        # TODO 1: SnakeData
        for _snake in self.filter(self.player_control):
            for x, y in _snake.filter_element(x_size, y_size):
                batch_tensor[y][x] = 1

        # TODO 2: CoinData
        for x, y in self.Coin_group.filter_element(x_size, y_size):
            batch_tensor[y][x] = 2

        # TODO 3: SelfData
        # for x, y in self.player_control.filter_element(x_size, y_size):
        #    batch_tensor[x][y] = 3

        # TODO 4: BoundData
        for x in range(*map(int, x_size[::-1]), block_size):
            for y in range(*map(int, y_size[::-1]), block_size):
                if (-block_size <= x <= 0 and 0 <= y <= height) or \
                        (-block_size <= y <= 0 and 0 <= x <= width) or \
                        (width <= (x + block_size) <= width + block_size and 0 <= y <= height) or \
                        (height <= (y + block_size) <= height + block_size and 0 <= x <= width):
                    batch_tensor[int((y - y_size[1]) // block_size)][int((x - x_size[1]) // block_size)] = 4

        return batch_tensor, (x_size[1], y_size[1])

    def get_head(self) -> tuple:
        return self.player_control.location_tensor[0]

    def get_state(self) -> torch.Tensor:
        self.tensor, self.batch_c = self.filter_element()
        return self.tensor

    def run_once(self) -> float:
        self.update()
        reward = self.player_control.get_reward_once()
        return reward

    def step(self, action: int):
        if not isinstance(self.player_control, snake_of_ai):
            self.reset()
        self.player_control.set_action(action)
        reward = self.run_once()
        return self.get_state(), reward

    def pre_train(self):
        if not isinstance(self.player_control, snake_of_ai):
            self.reset()
        action = self.player_control.goto_closest_coin_as_action()
        action = action if 0 <= action < ACTION_NUMBER else ACTION_NUMBER - 1
        self.player_control.set_action(action)
        reward = self.run_once()
        return self.get_state(), reward, action

    def get_total_reward(self) -> float:
        return self.player_control.get_reward()

    def reset(self):
        super(RLenvironment, self).reset()
        self.addEpisode()
        return self.get_state()

    def init_player_c(self):
        return snake_of_ai(self)
