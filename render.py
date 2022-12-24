import sys
import time

import numpy
import pygame
from vector import sprite, group, color
import param


class PygameCoin(pygame.sprite.Sprite, sprite.Coin):
    def __init__(self, group_, *args, **kwargs):
        self.image = pygame.Surface((param.COIN_RADIUS * 2, param.COIN_RADIUS * 2))
        self.image.fill(color.BLACK)
        pygame.draw.circle(self.image, color.generate_color(),
                           (param.COIN_RADIUS, param.COIN_RADIUS), param.COIN_RADIUS)
        self.image.set_colorkey(color.BLACK)
        super().__init__(group_)
        sprite.Coin.__init__(self, *args, **kwargs)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.array


class PygameCoinGroup(pygame.sprite.Group, group.CoinGroup):
    def __init__(self, parent):
        super(PygameCoinGroup, self).__init__()
        group.CoinGroup.__init__(self, parent)

    def generate_coin(self, score, position):
        return PygameCoin(self, score=score, position=position)

    def update(self):
        super(PygameCoinGroup, self).update()
        group.CoinGroup.update(self)
        self.draw(screen)


class PygameSnakeGroup(group.SnakeGroup):
    def __init__(self, parent):
        super().__init__(parent=parent)

    def update(self):
        super().update()
        for snake in self.snakes:
            for arr in snake.array:
                pygame.draw.circle(screen, snake.color, arr, param.SNAKE_RADIUS)


class PygameGameGroup(group.AbstractGameGroup):
    CoinGroupType = PygameCoinGroup
    SnakeGroupType = PygameSnakeGroup

    def __init__(self):
        super().__init__()
        # self.spent = []

    @staticmethod
    def event():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

    def update(self):
        startup = time.time()
        screen.fill(color.BLACK)
        super().update()
        self.event()
        pygame.display.update()
        # self.spent.append(time.time() - startup)
        # print((1 / numpy.average(self.spent)), (1 / numpy.max(self.spent)), self.coin_group.length)
        clock.tick(param.FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((param.WIDTH, param.HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Snake Deep Reinforcement Learning")
    game = PygameGameGroup()
    for _ in range(10):
        game.add_snake("zmh-program")
    game.run_forever()