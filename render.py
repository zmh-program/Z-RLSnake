import sys
import time

import numpy
import pygame
from vector import sprite, group, color, core
import param

MARGIN = param.BLOCK_SIZE * param.DATA_SPREAD
MARGIN_TUPLE = numpy.array([MARGIN, MARGIN])

MAX_ROBOT = 10
MIN_ROBOT = 3
DEFAULT_SNAKE_TYPE = sprite.SnakeTrainer


def state_el_color(el):
    return {
        1: color.GRAY,
        2: color.GOLD,
        3: color.RED,
        4: color.RED,
    }.get(el)


def render_state(snake: sprite.SnakeTrainer):
    start_data, state = snake.start_position_index, snake.generate_state()
    window.blit(small_font.render(f"Batch - Reward {snake.total_reward}", True, color.WHITE, ), (start_data - 1) *
                param.BLOCK_SIZE + MARGIN_TUPLE + [12, 0])
    pygame.draw.rect(window, color.WHITE, (*(start_data * param.BLOCK_SIZE + MARGIN_TUPLE),
                                           param.DATA_SIZE * param.BLOCK_SIZE, param.DATA_SIZE * param.BLOCK_SIZE),
                     1, border_radius=1)
    start_data *= param.BLOCK_SIZE
    for idx_y, y in enumerate(state):
        for idx_x, x in enumerate(y):
            if x != 0:
                pos = start_data + numpy.array([idx_x, idx_y]) * param.BLOCK_SIZE + MARGIN_TUPLE
                col = state_el_color(x)
                window.blit(small_font.render(str(int(x)), True, col, ), pos + [2, 2])
                pygame.draw.rect(window, col, (*pos, param.BLOCK_SIZE, param.BLOCK_SIZE), 1, 1)


def lazy_vertical_line(surface: pygame.Surface, start, length):
    pygame.draw.line(surface, color.WHITE, start, (start[0] + length, start[1]))


def lazy_horizontal_line(surface: pygame.Surface, start, length):
    pygame.draw.line(surface, color.WHITE, start, (start[0], start[1] + length))


class PygameCoin(pygame.sprite.Sprite, sprite.Coin):
    def __init__(self, group_, *args, **kwargs):
        super().__init__(group_)
        sprite.Coin.__init__(self, *args, **kwargs)
        self.image = pygame.Surface((param.BLOCK_RADIUS * 2, param.BLOCK_RADIUS * 2))
        self.image.fill(color.BLACK)
        pygame.draw.circle(self.image, color.YELLOW,
                           (param.BLOCK_RADIUS, param.BLOCK_RADIUS), param.BLOCK_RADIUS)
        pygame.draw.circle(self.image, color.GOLD,
                           (param.BLOCK_RADIUS, param.BLOCK_RADIUS), param.BLOCK_RADIUS, 1)
        self.image.blit(small_font.render(str(self.score), True, color.GOLD, ), [4, 0])
        self.image.set_colorkey(color.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = self.array


class PygameCoinGroup(pygame.sprite.Group, group.CoinGroup):
    def __init__(self, parent):
        super(PygameCoinGroup, self).__init__()
        group.CoinGroup.__init__(self, parent)

    def generate_coin(self, score, position, index):
        return PygameCoin(self, score=score, position=position, index=index)

    def remove_coin(self, coin: PygameCoin):
        super(PygameCoinGroup, self).remove_coin(coin)
        self.remove(coin)

    def update(self):
        super(PygameCoinGroup, self).update()
        group.CoinGroup.update(self)
        self.draw(screen)


class PygameSnakeGroup(group.SnakeGroup):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.player = self.add_snake("zmh-program", otype=sprite.SnakePlayer)

        self.cursor = MAX_ROBOT
        for idx in range(MAX_ROBOT):
            self.add_snake(f"robot {idx + 1}", otype=DEFAULT_SNAKE_TYPE)

    def update(self):
        super().update()
        for snake in self.snakes:
            for arr in snake.array:
                pygame.draw.circle(screen, snake.color, arr, param.BLOCK_RADIUS)
                pygame.draw.circle(screen, snake.background, arr, param.BLOCK_RADIUS, 1)
            screen.blit(font.render(snake.name, True, color.WHITE), snake.head + [5, 5])

    def render_states(self):
        for snake in self.snakes:
            if isinstance(snake, sprite.SnakeTrainer) and snake.alive:
                render_state(snake)

    def update_player_direction(self):
        self.player.update_direction_from_point(numpy.array(pygame.mouse.get_pos()) - MARGIN_TUPLE)

    def call_death(self, snake: sprite.BaseSnake):
        super().call_death(snake)
        if self.length < MIN_ROBOT:
            self.cursor += 1
            self.add_snake(f"robot {self.cursor}", otype=DEFAULT_SNAKE_TYPE)


class PygameGameGroup(group.AbstractGameGroup):
    CoinGroupType = PygameCoinGroup
    SnakeGroupType = PygameSnakeGroup

    coin_group: PygameCoinGroup
    snake_group: PygameSnakeGroup

    def __init__(self):
        super().__init__()

        self.base_fps = 0
        self.total_fps = []

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                self.snake_group.update_player_direction()

    @staticmethod
    def _render_params(content):
        for y, cont in enumerate(content):
            window.blit(small_font.render(cont, True, color.WHITE, ), [0, y * param.BLOCK_SIZE])

    def render_params(self):
        self._render_params((
            f"coins: {self.coin_group.length}",
            f"snakes: {self.snake_group.length}",
            f"base-fps: {self.base_fps}",
            f"average-fps: {round(numpy.average(self.total_fps), 2) if self.total_fps else 0}",
            "",
            f"memory: {core.convert_size(core.get_size(self), 2)}",
            f"migration-length: {core.convert_size(len(str(self.migration)))}",
        ))

    def update_without_tick(self):
        window.fill(color.BLACK)
        screen.fill(color.BLACK)
        super().update()
        self.event_handler()

        window.blit(screen, MARGIN_TUPLE)
        pygame.draw.rect(window, color.WHITE, [MARGIN, MARGIN, param.WIDTH, param.HEIGHT], 1, border_radius=2)
        self.snake_group.render_states()
        self.render_params()
        pygame.display.update()

    def update(self):
        startup = time.time()
        self.update_without_tick()
        benchmark = time.time() - startup
        self.base_fps = round(1 / benchmark, 3) if benchmark != 0 else 0
        self.total_fps.append(self.base_fps)
        clock.tick(param.FPS)


if __name__ == "__main__":
    pygame.init()

    window = pygame.display.set_mode((param.WIDTH + MARGIN * 2, param.HEIGHT + MARGIN * 2))
    screen = pygame.Surface((param.WIDTH, param.HEIGHT))

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 20, bold=True)
    small_font = pygame.font.SysFont("monospace", 14, bold=True)
    pygame.display.set_caption("Snake Deep Reinforcement Learning")
    game = PygameGameGroup()
    game.run_forever()
