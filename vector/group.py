from .sprite import *
from itertools import combinations
from typing import *
from .vec2d import get_closest_element


class CoinGroup(Migration):
    def __init__(self, parent: "AbstractGameGroup"):
        super().__init__()
        self.coins: List[Coin] = []
        self.nature_coins: List[Coin] = []
        self._coin_length = 0
        self.parent = parent

        self.add_coin()

    @staticmethod
    def generate_coin(score, position):
        return Coin(score=score, position=position)

    def add_coin(self, position=None, score=1, natural=False):
        coin = self.generate_coin(score, position)
        self.coins.append(coin)
        self._coin_length += 1

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

    def delete_coin(self, index):
        assert index + 1 <= self._coin_length
        del self.coins[index]

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

    def get_data(self) -> list:
        return [coin.data for coin in self.coins]


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

    @property
    def iter_combinations(self):
        return combinations(self.snakes, 2)

    def get_closest_coin(self, snake: JuniorSnakeRobot):
        return get_closest_element(snake.head, self.parent.coin_group.coins)

    def call_death(self, snake: BaseSnake):
        snake.death()
        self.remove_snake(snake)

    def get_snake_collide(self) -> Set[BaseSnake]:
        return set(self._iter_snake_collide())

    def _iter_snake_collide(self) -> Iterable[BaseSnake]:
        for s1, s2 in self.iter_combinations:
            b1, b2 = snake_combination_collide(s1, s2)
            if b1:
                yield s1
            if b2:
                yield s2

    @property
    def migration(self):
        return {snake: snake.migration for snake in self.snakes if snake.has_migration}

    def get_data(self) -> list:
        return [snake.get_data() for snake in self.snakes if snake.alive]


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
            self.coin_group.add_coin()

    def update(self):
        self.coin_group.update()
        self.snake_group.update()
        self.tick()

    @property
    def migration(self):
        return {
            "coin": self.coin_group.migration,
            "snake": self.snake_group.migration,
        }

    def run_forever(self):
        while True:
            self.update()
