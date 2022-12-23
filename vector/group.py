from .sprite import *
from itertools import combinations
from typing import *


class CoinGroup(object):
    def __init__(self, parent: "AbstractGameGroup"):
        self.coins: List[Coin] = []
        self.nature_coins: List[Coin] = []
        self._coin_length = 0
        self.parent = parent

    def add_coin(self, position=None, score=1, natural=False):
        coin = Coin(score, position)
        self.coins.append(coin)
        self._coin_length += 1

        if natural:
            self.nature_coins.append(coin)

    def snake_death_as_coin(self, snake: BaseSnake):
        for arr in snake.array:
            self.add_coin(arr, 5)

    def update(self):
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


class SnakeGroup(object):
    def __init__(self, parent: "AbstractGameGroup"):
        self.snakes: List[BaseSnake] = []
        self.parent = parent

    def add_snake(self, name="", otype=None):
        self.snakes.append((otype or BaseSnake)(name=name))

    def remove_snake(self, snake: BaseSnake):
        self.snakes.remove(snake)

    def update(self):
        for snake in self.snakes:
            snake.update()

    @property
    def length(self) -> int:
        return len(self.snakes)

    @property
    def iter_combinations(self):
        return combinations(self.snakes, 2)

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


class AbstractGameGroup(object):
    def __init__(self):
        self.coin_group = CoinGroup(self)
        self.snake_group = SnakeGroup(self)

        self._tick = 0

    def snake_death(self, snake: "BaseSnake"):
        self.coin_group.snake_death_as_coin(snake)
        self.snake_group.call_death(snake)

    def tick(self):
        self._tick += 1
        if self._tick % GENERATE_COIN_TICK == 0:
            self.coin_group.add_coin()

    def update(self):
        self.snake_group.update()
        self.coin_group.update()
        self.tick()
