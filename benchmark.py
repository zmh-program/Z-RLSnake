import time
import numpy
from vector import group, core, sprite
import cProfile
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="benchmark:%(levelname)s (%(asctime)s) >> %(message)s",
    datefmt=".:%M:%S",
)

logger = logging.getLogger(__name__)


class BenchmarkGameGroup(group.AbstractGameGroup):
    def __init__(self):
        super().__init__()

        self.base_fps = 0
        self.total_fps = []

        self.last_check = 0

    def output_params(self):
        if time.time() - self.last_check < 2:
            return
        self.last_check = time.time()

        logger.info(", ".join((
            f"coins: {self.coin_group.length}",
            f"snakes: {self.snake_group.length}",
            f"base-fps: {self.base_fps}",
            f"average-fps: {round(numpy.average(self.total_fps), 2) if self.total_fps else 0}",
            f"memory: {core.convert_size(core.get_size(self))}",
            f"migration-length: {core.convert_size(len(str(self.migration)))}",
        )))

    def bench(self, n, otype=sprite.BaseSnake):
        for idx in range(n):
            self.snake_group.add_snake(f"robot {idx}", otype=otype)
        cProfile.runctx("self.run_forever()", globals(), locals())

    def update(self):
        startup = time.time()
        super().update()
        benchmark = time.time() - startup
        self.base_fps = round(1 / benchmark, 3) if benchmark != 0 else 0
        self.total_fps.append(self.base_fps)

        self.output_params()

    def run_forever(self):
        try:
            super().run_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    game = BenchmarkGameGroup()
    game.bench(10, otype=sprite.SeniorSnakeRobot)
