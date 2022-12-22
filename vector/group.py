from .sprite import *
from itertools import combinations
from typing import *


class CoinGroup(object):
    def __init__(self):
        self.coins: List[Coin] = []
        self._coin_length = 0

    def add_coin(self):
        self.coins.append(Coin())
        self._coin_length += 1

    def remove_coin(self, coin: Coin):
        self.coins.remove(coin)
        self._coin_length -= 1

    def delete_coin(self, index):
        assert index + 1 <= self._coin_length
        del self.coins[index]

    def collide_coin(self, coin: Coin):
        self.remove_coin(coin)

    @property
    def length(self):
        return self._coin_length


class SnakeGroup(object):
    def __init__(self):
        self.snakes = []

    def add_snake(self, otype=None):
        self.snakes.append(otype or BaseSnake)

    @property
    def length(self) -> int:
        return len(self.snakes)

    @property
    def iter_combinations(self):
        return combinations(self.snakes, 2)

    def get_snake_collide(self) -> Set[BaseSnake]:
        return set(self._iter_snake_collide())

    def _iter_snake_collide(self) -> Iterable[BaseSnake]:
        for s1, s2 in self.iter_combinations:
            b1, b2 = snake_combination_collide(s1, s2)
            if b1:
                yield s1
            if b2:
                yield s2
