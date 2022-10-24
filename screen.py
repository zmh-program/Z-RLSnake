import pygame, sys, random, math
from time import time

pygame.init()

use_matplotlib_to_rank_snake = False
# 使用matplotlib来排名蛇,这回让你的帧数先将到个位数,如果你想性能保持在100+,请勿使用
# 使用 matplotlib -> --canvas.tostring-->  --pygame.fromstring--> 显示,如果蛇们木有更新,直接返回上个图像,提升性能
if use_matplotlib_to_rank_snake:
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import matplotlib.backends.backend_agg as agg

    mpl.use("Agg")


    class figure(object):

        def __init__(self, h, dpi=100, pos=None):
            self.h, self.dpi, self.pos = h, dpi, pos
            self.last_name, self.last_length = None, None
            self.last_Figure = None

        # @jit
        def draw(self, name, length, ):
            length = list(length)
            dic = dict()
            for n, c in zip(name, length):
                if c in dic.keys():
                    dic[c] = dic[c] + [n]
                else:
                    dic[c] = [n]
            length = sorted(set(length), reverse=False)
            for c in length:
                rank = len(length) - length.index(c)
                dic[c][round(len(dic[c]) / 2)] = 'No.{}{}{}'.format(rank, (
                            9 - len(str(rank)) - len(dic[c][round(len(dic[c]) / 2)])) * " ",
                                                                    dic[c][round(len(dic[c]) / 2)])  # \t制表符不可用
            name = ['\n'.join(dic[c]) for c in length]
            if self.last_name == name and self.last_length == length:
                surfig = self.last_Figure
            else:
                # 图像绘制
                fig, ax = plt.subplots()
                ax.set_title("Snakes Score Rank")
                fig.set_dpi(self.dpi)
                fig.set_figheight(self.h / self.dpi)
                fig.set_figwidth(Secondary_interface_width / self.dpi)
                b = ax.barh(range(len(name)), length, color='r')
                # 添加数据标签
                for rect in b:
                    ax.text(rect.get_width(), rect.get_y() + rect.get_height() / 2, '%d' % int(rect.get_width()),
                            ha='left', va='center')
                # 设置Y轴刻度线标签
                ax.set_yticks(range(len(name)))
                ax.set_yticklabels(name)
                canvas = agg.FigureCanvasAgg(fig)
                canvas.draw()
                renderer = canvas.get_renderer()
                surfig = pygame.image.fromstring(renderer.tostring_rgb(), canvas.get_width_height(), "RGB")

                self.last_name, self.last_length, self.last_Figure = name, length, surfig
            self.blit(surfig)
            plt.close('all')
            return

        def blit(self, surfig):
            if self.pos:
                sec_screen.blit(surfig, self.pos)
else:
    rankFig = pygame.image.load('rank.png')
    rankFig_rect = rankFig.get_rect()


    def _format(*args):
        # SPLIT_STRING = 10
        # return str().join([str(a).ljust(SPLIT_STRING) for a in args]).strip()
        return [str(a) for a in args]


    def _sort(sort_iterable, values):  # 返回被可迭代对象排序过的值
        if len(sort_iterable) != len(values):
            raise ValueError
        if len(values) == 1:
            return sort_iterable, [values]
        if type(sort_iterable) == tuple:
            sort_iterable = list(sort_iterable)
        dic = dict()
        for i, v in zip(sort_iterable, values):
            if i in dic.keys():
                dic[i] = dic[i] + [v]
            else:
                dic[i] = [v]
        Iter = sorted(set(sort_iterable), reverse=True)  # 排名降序排列
        return Iter, [dic[i] for i in Iter]


    def _rank():
        snake = w.CSH.SnakeList
        l, snake = _sort([Snake.score for Snake in snake], snake)
        ENDlist = list()
        for c in snake:
            if len(ENDlist) >= 5:
                break
            _, dt = _sort([Snake.kill for Snake in c], c)
            for d in dt:
                ENDlist.extend(d)

        for s in ENDlist[:5]:
            yield _format(str(), s.name, s.score, s.get_length(), s.kill)
        pl = w.CSH.player
        if len(ENDlist) < 5:
            for _ in range(5 - len(ENDlist)):
                yield [str()] * 5
        yield _format(l.index(pl.score) + 1, pl.name, pl.score, pl.get_length(), pl.kill)


    rank_color = [(255, 128, 64),
                  (88, 88, 88),
                  (53, 60, 1),
                  (0, 30, 60),
                  (247, 211, 129),
                  (255, 2, 0)]
    rank_font = pygame.font.SysFont('comicsansms',
                                    21)


    def _draw_rank():
        y = height - rankFig_rect[3]
        sec_screen.blit(rankFig, [3, y])
        result_iter = _rank()
        data = list(result_iter)
        for nLine in range(len(data)):
            Line = data[nLine]
            for nElement in range(len(Line)):
                string = Line[nElement]
                sec_screen.blit(rank_font.render(string, True, rank_color[nLine]),
                                [21 + nElement * 83, y + (0.8 + nLine) * 50 + (nLine // 5) * 10])


class MessageBox:
    def __init__(self):
        self.image = pygame.image.load("MessageBox.png")
        self.rect = self.image.get_rect()
        self.y = height - 360 - self.rect[3]
        self.pos = 2, self.y
        self.message = list()
        self.font = pygame.font.SysFont('simsunnsimsun', 24)
        self.h = self.font.get_height() + 2  # +2像素 间隔
        self.DISPLAY_LINE = (self.rect[3] // self.h) - 4

    def add_message(self, i):
        self.message.append(i)

    def get_length(self):
        return len(self.message)

    def update(self):
        sec_screen.blit(self.image, self.pos)
        for y in range(self.DISPLAY_LINE):
            if y + 1 <= self.get_length():
                sec_screen.blit(self.font.render(self.message[-(y + 1)], True, (0, 0, 100)),
                                [22, self.y + ((y + 2) * self.h)])  # 等同于 reversed(self.message)[y]


class Snake(object):
    class SnakeHead(pygame.sprite.Sprite):
        def __init__(self, Parent, pos):
            pygame.sprite.Sprite.__init__(self)
            self.Parent = Parent
            self.image = pygame.Surface([block_size, block_size])
            self.image.set_colorkey((0, 0, 0))

            radius = block_size // 2
            # 含有黑色边框的圆蛇头
            pygame.draw.circle(self.image, self.Parent.color, (radius, radius), radius - 1)
            pygame.draw.circle(self.image, (10, 10, 10), (radius, radius), radius, 1)
            # 黑色边框 左右眼
            pygame.draw.circle(self.image, (255, 255, 255), (radius / 2, radius), radius / 3 - 1)
            pygame.draw.circle(self.image, (10, 10, 10), (radius / 2, radius), radius / 3, 1)

            pygame.draw.circle(self.image, (255, 255, 255), (block_size - radius / 2, radius), radius / 3 - 1)
            pygame.draw.circle(self.image, (10, 10, 10), (block_size - radius / 2, radius), radius / 3, 1)
            # eyeColor = [255-c for c in Parent.color]
            # pygame.draw.circle(self.image, eyeColor, (radius/2, radius), radius/3)
            # pygame.draw.circle(self.image, eyeColor, (block_size-radius/2, radius), radius/3)

            self.rect = self.image.get_rect()
            self.rect.center = pos

        def update(self, pos):
            self.rect.center = pos
            self.out()
            screen.blit(pygame.transform.rotate(self.image, math.atan2(*self.Parent.direction) * 180 / math.pi),
                        self.rect)

        def collide(self):
            return len(pygame.sprite.spritecollide(self, self.Parent.Coin_group, True))

        def out(self):
            x, y = self.rect.center
            r = block_size / 4 / 2

            die, _snake = w.CSH.touch_another_snake_body(self.Parent)
            if not ((0 + r < x < width - r) and (0 + r < y < height - r)):
                self.Parent.died(u"你 因触碰边缘死亡", u"{}触碰边缘死亡".format(self.Parent.name.ljust(8)))
            elif die:
                _snake.kill += 1
                snake = _snake.name
                self.Parent.died(u"你 碰撞到{}而死亡".format(snake),
                                 u"{}碰撞到{}而死亡".format(self.Parent.name.ljust(8), snake.center(8)))
                return True

    class SnakeBody(pygame.sprite.Sprite):
        def __init__(self, color):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.Surface([block_size, block_size])
            self.image.set_colorkey((0, 0, 0))

            radius = block_size // 2
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
            for p in range(len(sprs)):
                spr = sprs[p]
                spr.rect.center = pos[p]
                screen.blit(spr.image,
                            spr.rect)

        def snakeCollide(self, i):
            return bool(pygame.sprite.spritecollide(i, self, False))

    def __init__(self, Coin_group, name="", length=3, color=None):
        self.stlen = length
        self.name = name
        if color is None:
            color = (random.randint(20, 255),
                     random.randint(20, 255),
                     random.randint(20, 255))
        self.color = color
        self.Coin_group = Coin_group
        self.Location = [(random.randint(block_size, width - block_size),
                          random.randint(block_size, height - block_size))] * length
        self.head = Snake.SnakeHead(self, self.Location[0])
        self.body = Snake.SnakeBodyGroup(self.color)
        self.direction = [0, 0]
        self.score = 0
        self.kill = 0
        self.speed = 15
        self.over = False
        self.time = time()

    def update(self):
        if not self.over:
            self.add_length()
            self.add_score()
            del self.Location[-1]
            self.Location.insert(0, self.to_direction(*self.Location[0]))
            sx, sy = self.Location[0]
            screen.blit(snake_font.render(self.name, True, (255, 255, 255)), [sx, sy + block_size // 2 + 1])
            self.body.update(reversed(self.Location[1:]))
            self.head.update(self.Location[0])  # reversed和先画头在画身体目的->转向时蛇头和转过去的身体在前
        return self.over

    def count_direction(self, pos1, pos2=None):  # 长度矢量化->return length, direction
        x1, y1 = pos1
        if not pos2:
            pos2 = self.Location[0]
        x2, y2 = pos2
        xlength, ylength = x1 - x2, y1 - y2
        length = math.hypot(xlength, ylength)  # 返回欧几里德范数 sqrt(x**2, y**2)  eg.勾股定理
        if length == 0:
            return 0, [0, 0]
        return length, [(xlength / length) * self.speed, (ylength / length) * self.speed]

    def set_direction(self, TargetDirectionPosition: tuple):
        _, self.direction = self.count_direction(TargetDirectionPosition)

    def to_direction(self, x, y):
        return (x + self.direction[0],
                y + self.direction[1])

    def return_direction(self):
        return self.direction

    def add_length(self):
        while self.score // SCORE_TO_LENGTH > self.get_length() - 3:
            self.Location.append(self.Location[-1])
        return

    def get_length(self):  # -> int
        return len(self.Location)

    def get_random_direction(self):
        _, self.direction = self.count_direction((random.randint(0, width),
                                                  random.randint(0, height)))

    def add_score(self):
        if hasattr(self.head, "collide"):
            score = self.head.collide()
            if score > 0:
                self.score += score
                self.Coin_group.coinLack()
            return score

    def died(self, r, DC):
        self.Coin_group.snakeDied(self.Location)
        self.died_reason = r
        w.dieCall(DC)
        self.over = True
        self.head = None
        self.body.empty()


class snake_of_player(Snake):
    def __init__(self, Coin_group, name="player", length=3, color=(255, 0, 0)):
        Snake.__init__(self, Coin_group, name, length, color)
        # self.get_random_direction()

    def set_direction(self):
        Snake.set_direction(self, pygame.mouse.get_pos())


class snake_of_AI(Snake):
    def __init__(self, Coin_group, name="AI", length=3, color=None):
        Snake.__init__(self, Coin_group, name, length, color)
        self.set_direction()

    def AICOUNT(self):
        try:
            self.head.rect.center = self.to_direction(*self.Location[0])
            x, y = self.head.rect.center
            r = block_size / 4 / 2
            i = False
            r = 0
            while (((not ((0 + r < x < width - r) and (0 + r < y < height - r))) or
                    w.CSH.touch_another_snake_body(self)[0]) and r < fps):
                r += 1  # 运行超时
                self.get_random_direction()
                self.head.rect.center = self.to_direction(*self.Location[0])
                x, y = self.head.rect.center
                i = True
            return i
        except AttributeError:
            return

    def set_direction(self):
        minLength = \
        sorted(list(map(lambda spr: Snake.count_direction(self, spr.rect.center)[0], self.Coin_group.sprites())),
               reverse=False)[0]
        # sorted.reverse=False, 倒序为否, 则升序排列, 获取第一个及是最短长度的金币

        dataDict = dict()
        for l, d in map(lambda spr: Snake.count_direction(self, spr.rect.center), self.Coin_group.sprites()):
            dataDict[l] = d

        self.direction = dataDict[minLength]

    def update(self):
        if (not Snake.update(self)) and (not self.AICOUNT()):
            self.set_direction()


class coinGroup(pygame.sprite.Group):
    class Coin(pygame.sprite.Sprite):
        Fig = pygame.image.load('coin.png')

        def __init__(self, pos=None):
            pygame.sprite.Sprite.__init__(self)
            self.image = coinGroup.Coin.Fig
            self.image.set_colorkey((0, 0, 0))
            self.rect = self.image.get_rect()
            self.create_time = time()
            if pos is None:
                pos = (random.randint(0, width // block_size - 1) * block_size,
                       random.randint(0, height // block_size - 1) * block_size)
            self.rect.topleft = pos
            self.pos = pos

    def __init__(self, max_coin_num=10):
        self.max = max_coin_num
        pygame.sprite.Group.__init__(self, [coinGroup.Coin() for _ in range(max_coin_num)])

    def coinLack(self):
        n = self.max - len(self.sprites())
        if n > 0:
            self.add(*[coinGroup.Coin() for _ in range(n)])

    def snakeDied(self, args: list):
        for pos in args:
            x, y = pos
            r = block_size // 2
            if ((0 + r < x < width - r) and (0 + r < y < height - r)):
                self.add([coinGroup.Coin(pos) for _ in range(SCORE_TO_LENGTH)])

    def draw(self):  # 重写原方法,提高性能
        sprs = self.sprites()
        if time() - sprs[0].create_time > 30:
            self.remove(sprs[0])
        for spr in sprs:
            screen.blit(spr.image, spr.pos)


class CenterSpriteHandle(object):
    def __init__(self):
        self.Coin_group = coinGroup()
        self.player = snake_of_player(self.Coin_group, "me")
        self.AI = [snake_of_AI(self.Coin_group, "AI {}".format(n + 1)) for n in range(AI_NUMBER)]
        self.SnakeList = [self.player] + self.AI
        if use_matplotlib_to_rank_snake:
            self.figHandle = figure((height / 2), dpi, [3, height / 2])

    def sprites_nameLength(self):
        # for s in self.SnakeList:
        # yield s.name, s.get_length()
        return list(zip(*[(s.name, s.score) for s in self.SnakeList]))

    def update(self):
        for s in self.SnakeList:
            if s.over:
                del self.SnakeList[self.SnakeList.index(s)]
                ai = snake_of_AI(self.Coin_group, "AI {}".format(len(self.AI) + 1))
                self.AI.append(ai)
                self.SnakeList.append(ai)

            else:
                s.update()
        self.Coin_group.draw()
        if use_matplotlib_to_rank_snake:
            self.figHandle.draw(*self.sprites_nameLength())
        else:
            _draw_rank()

        self.sprites_nameLength()
        if self.player.over is True:
            self.empty()
            w.gameover()

    def empty(self):
        for s in self.SnakeList:
            s.over = True
        self.Coin_group.empty()

    def touch_another_snake_body(self, snake):
        if snake not in self.SnakeList:
            return False, None
        for s in self.filter(snake):  # 去除蛇头身精灵碰撞{set}-{set} -> {1,3,4,2} - {3} -> return {1,4,2} (iterable可迭代的对象set)
            if s.body.snakeCollide(snake.head):
                return True, s
        return False, None

    def filter(self, exceptSnake):
        return set(self.SnakeList) - {exceptSnake}


def center_figureHandle(fpath, ck=(255, 255, 255)):  # 图片pos.x居中center
    i = pygame.image.load(fpath)
    i.set_colorkey(ck)
    rect = i.get_rect()
    return i, rect, (width - rect[2]) // 2


class Window(object):
    def __init__(self):
        global screen, sec_screen, Allscreen
        Allscreen = pygame.display.set_mode((width + Secondary_interface_width,
                                             height))
        screen = pygame.Surface((width, height))
        sec_screen = pygame.Surface((Secondary_interface_width, height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.music = pygame.mixer.Sound('music.mp3')
        self.music.play(-1, )
        self.start()
        self.CNfont = pygame.font.SysFont('fangsou', 20)
        self.MessageBox = MessageBox()
        pygame.display.set_caption("Snake")
        # self.CNfont.set_bold(True)

    def start(self):
        self.CSH = CenterSpriteHandle()
        self.running = True

    def drawLines(self):
        for x in range(0, width, block_size):
            pygame.draw.line(screen, (180, 180, 180), (x, 0), (x, height))
        for y in range(0, height, block_size):
            pygame.draw.line(screen, (180, 180, 180), (0, y), (width, y))

    def Quit(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()
        return

    def dieCall(self, n):
        self.MessageBox.add_message(n)

    def update(self):
        STtime = time()
        screen.fill((0, 0, 0))
        sec_screen.fill((255, 255, 255))
        pygame.draw.line(sec_screen, (255, 255, 255), (0, 0), (0, height), 3)
        self.drawLines()
        self.CSH.update()
        for event in pygame.event.get():
            {pygame.QUIT: self.Quit,
             pygame.MOUSEBUTTONUP: self.CSH.player.set_direction,
             }.get(event.type, lambda: None)()

        data = [u"得分: {}".format(self.CSH.player.score),
                u"长度 : {}".format(len(self.CSH.player.Location)),
                u"击杀 : {}".format(self.CSH.player.kill),
                u"计算帧 / 固定帧 : {} / {}".format(int(1 / (time() - STtime)), fps)
                ]
        for n in range(len(data)):
            sec_screen.blit(self.CNfont.render(data[n], True, (0, 0, 0)), [3, n * (font_height + 5)])
        self.MessageBox.update()
        Allscreen.blit(screen, [0, 0])
        Allscreen.blit(sec_screen, [width, 0])
        pygame.display.update()
        self.clock.tick(fps)

    def run(self):
        while self.running:
            self.update()

    def gameover(self):

        f1, r1, x1 = center_figureHandle('restart0.png')
        f2, r2, x2 = center_figureHandle('restart1.png')
        fg, rg, xg = center_figureHandle('gameover.jpg')
        dr = self.CNfont.render(self.CSH.player.died_reason, True, (0, 0, 0))
        while True:
            screen.fill((255, 255, 255))
            screen.blit(dr, [xg + 140, rg[3] - 20])
            screen.blit(fg, [xg, 0])
            x, y = pygame.mouse.get_pos()
            if (0 < x - x1 < r1[2]) and (0 < y - rg[3] < r1[3]):
                screen.blit(f2, [x2, rg[3]])
                collide = True
            else:
                screen.blit(f1, [x1, rg[3]])
                collide = False
            Allscreen.blit(screen, [0, 0])
            Allscreen.blit(sec_screen, [width, 0])
            pygame.display.update()
            self.clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.Quit()
                if event.type == pygame.MOUSEBUTTONUP and collide:
                    self.restart()

    def restart(self):
        self.start()
        self.run()
        return


if __name__ == '__main__':
    fps = 20
    dpi = 85
    height = 720
    width = 1100

    Secondary_interface_width = 420
    block_size = 20
    SCORE_TO_LENGTH = 5
    AI_NUMBER = 6


    class LengthError(Exception):
        None


    if height % block_size != 0 or width % block_size != 0:
        raise LengthError('Length is not divisible by')

    font = pygame.font.SysFont('consolas', 17)
    snake_font = pygame.font.SysFont('comicsansms', 17)
    font_height = font.get_height()
    from cProfile import run

    w = Window()
    run("w.run()")