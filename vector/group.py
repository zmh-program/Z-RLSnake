from .sprite import *
from itertools import combinations
from typing import *
from .vec2d import get_closest_element, sorted_closest_element
from . import core


class CoinGroup(Migration):
    def __init__(self, parent: "AbstractGameGroup"):
        super().__init__()
        self.coins: List[Coin] = []
        self.nature_coins: List[Coin] = []
        self._coin_length = 0
        self.parent = parent
        self.cursor = 0  # as index

        self.add_coin()

    @staticmethod
    def generate_coin(score, position, index):
        return Coin(score=score, position=position, index=index)

    def add_coin(self, position=None, score=1, natural=False):
        coin = self.generate_coin(score, position, self.cursor)
        self.coins.append(coin)
        self._coin_length += 1
        self.cursor += 1
        self.add_dict_migration("add", coin.index, coin.data)
        if natural:
            self.nature_coins.append(coin)

    def snake_death_as_coin(self, snake: BaseSnake):
        for arr in snake.array:
            self.add_coin(arr, 5)

    def update(self):
        self.collide_snakes(self.parent.snake_group)
        for coin in self.nature_coins:
            if coin.is_clear:
                self.remove_coin(coin)

    def remove_coin(self, coin: Coin):
        self.coins.remove(coin)
        self._coin_length -= 1

        if coin.natural:
            self.nature_coins.remove(coin)
        self.add_list_migration("remove", coin.index)

    def delete_coin(self, index):
        assert index + 1 <= self._coin_length
        self.remove_coin(self.coins[index])

    def coin_collided(self, coin: Coin) -> int:
        self.remove_coin(coin)
        return coin.score

    def collide_snakes(self, group: "SnakeGroup"):
        for snake in group.snakes:
            for coin in self.coins:
                if coin.is_collide_array(snake):
                    snake.add_score(self.coin_collided(coin))

    @property
    def length(self):
        return self._coin_length

    def get_data(self) -> dict:
        return {coin.index: coin.data for coin in self.coins}


class SnakeGroup(object):
    def __init__(self, parent: "AbstractGameGroup"):
        self.snakes: List[BaseSnake] = []
        self.parent = parent

    def add_snake(self, name="", otype=None):
        snake = (otype or BaseSnake)(name=name, parent=self)
        self.snakes.append(snake)
        return snake

    def remove_snake(self, snake: BaseSnake):
        self.snakes.remove(snake)

    def prediction_collide(self, snake: SeniorSnakeRobot) -> bool:
        for snake_ in self.snakes:
            if snake_ != snake:
                if snake.predict_snake_collide(snake_):
                    return True
        return False

    def update(self):
        for snake in self.snakes:
            snake.update()
            if snake.border_collide():
                self.parent.snake_death(snake)
        for snake in self.get_snake_collide():
            self.parent.snake_death(snake)

    @property
    def length(self) -> int:
        return len(self.snakes)

    def get_closest_coin(self, snake: Union[JuniorSnakeRobot, SnakeTrainer]):
        return get_closest_element(snake.head, self.parent.coin_group.coins)

    def sorted_closest_coin(self, snake: Union[JuniorSnakeRobot, SnakeTrainer]):
        return sorted_closest_element(snake.head, self.parent.coin_group.coins)

    def call_death(self, snake: BaseSnake):
        snake.death()
        self.remove_snake(snake)

    def get_snake_collide(self) -> Set[BaseSnake]:
        return set(self._iter_snake_collide())

    def _iter_snake_collide(self) -> Iterable[BaseSnake]:
        for s1, s2 in combinations(self.snakes, 2):
            b1, b2 = snake_combination_collide(s1, s2)
            if b1:
                s2.add_killed()
                yield s1
            if b2:
                s1.add_killed()
                yield s2

    @property
    def migration(self):
        return {snake.name: snake.migration for snake in self.snakes if snake.has_migration}

    def get_data(self) -> list:
        return [snake.get_data() for snake in self.snakes if snake.alive]

    def detect_state(self, snake: "SnakeTrainer"):
        return self.parent.detect_state(snake)


class AbstractGameGroup(object):
    CoinGroupType = CoinGroup
    SnakeGroupType = SnakeGroup

    coin_group: CoinGroup
    snake_group: SnakeGroup

    def __init__(self):
        self.coin_group = self.CoinGroupType(self)
        self.snake_group = self.SnakeGroupType(self)

        self._tick = 0

    def snake_death(self, snake: "BaseSnake"):
        self.coin_group.snake_death_as_coin(snake)
        self.snake_group.call_death(snake)

    def tick(self):
        self._tick += 1
        if self._tick % GENERATE_COIN_TICK == 0:
            for _ in range(max(self.snake_group.length // 2, 1)):
                self.coin_group.add_coin()

    def update(self):
        self.coin_group.update()
        self.snake_group.update()
        self.tick()

    def detect_state(self, snake: "SnakeTrainer") -> numpy.ndarray:
        return core.filter_range(snake, self.coin_group, self.snake_group)

    @property
    def data(self):
        return {
            "coin": self.coin_group.get_data(),
            "snake": self.snake_group.get_data()
        }

    @property
    def migration(self):
        return {
            "coin": self.coin_group.migration,
            "snake": self.snake_group.migration,
        }

    def run_forever(self):
        while True:
            self.update()
