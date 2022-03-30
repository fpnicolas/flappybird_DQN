import random
import numpy as np
import pygame, sys
from pygame.locals import *

WIDTH = 300
HEIGHT = 300

pygame.init()
Screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("flappy bird")
bg = pygame.Surface((Screen.get_rect().width, Screen.get_rect().height))

black = (0, 0, 0)
white = (255, 255, 255)
pink = (255, 182, 193)
green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
font = pygame.font.Font(None, 36)


def print_text(font, x, y, text, color=(255, 255, 255)):
    imgText = font.render(text, True, color)
    screen = pygame.display.get_surface()
    screen.blit(imgText, (x, y))


class Barrier(pygame.sprite.Sprite):
    # 获得一个随机数
    def __init__(self, x, y, h):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(x, y, 25, h)
        image = pygame.Surface([25, h]).convert_alpha()
        image.fill(green)
        self.image = image
        self.last_time = 0

    # X property
    def _getx(self): return self.rect.x

    def _setx(self, value): self.rect.x = value

    X = property(_getx, _setx)

    # Y property
    def _gety(self): return self.rect.y

    def _sety(self, value): self.rect.y = value

    Y = property(_gety, _sety)

    # position property
    def _getpos(self): return self.rect.topleft

    def _setpos(self, pos): self.rect.topleft = pos

    position = property(_getpos, _setpos)

    def update(self, speed=3):
        self.X -= speed


# 读入两帧动画，用以表现小鸟的飞行
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.image_up = pygame.transform.scale(pygame.image.load('./bird_up.PNG').convert_alpha(), [25, 25])
        self.image_down = pygame.transform.scale(pygame.image.load('./bird_down.PNG').convert_alpha(), [25, 25])
        self.rect = self.image_down.get_rect()
        self.current_image = 0  # 一个toggle，记录目前是up还是down
        self.last_time = 0

    # X property
    def _getx(self):
        return self.rect.x

    def _setx(self, value):
        self.rect.x = value

    X = property(_getx, _setx)

    # Y property
    def _gety(self):
        return self.rect.y

    def _sety(self, value):
        self.rect.y = value

    Y = property(_gety, _sety)

    # position property
    def _getpos(self):
        return self.rect.topleft

    def _setpos(self, pos):
        self.rect.topleft = pos

    position = property(_getpos, _setpos)

    def update(self, speed=3):
        if self.current_image:
            self.image = self.image_up
        else:
            self.image = self.image_down
            self.current_image = 1
        self.Y += speed


class BarrierManager(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.last_barrier = None
        self.second_barrier = None
        self.first_barrier = None

    def group_update(self, speed=3):
        self.update(speed)
        self.draw(Screen)
        # 销毁老的
        for b in self:
            if b.X <= -25:
                self.remove(b)
        # 生成新的
        if self.last_barrier.X < 321:
            self.first_barrier = self.second_barrier
            self.second_barrier = self.last_barrier
            self.last_barrier = self.make_couple_barrier(440)
            return True
        else:
            return False

    def init_barriers(self):
        self.first_barrier = self.make_couple_barrier(200)
        self.second_barrier = self.make_couple_barrier(320)
        self.last_barrier = self.make_couple_barrier(440)

    # 画出蓝色的障碍 width是一定的，定20。如果是上边的，y是0。需要知道x和h。下面的需要知道h和x，y是400-h
    def make_couple_barrier(self, x):
        blank_width = 70
        blank_y = random.randint(blank_width, HEIGHT - blank_width * 2)
        bar1 = Barrier(x, 0, blank_y)
        bar2 = Barrier(x, blank_y + blank_width, HEIGHT - blank_width - blank_y)
        self.add(bar1)
        self.add(bar2)
        return bar1

    def reset(self):
        for b in self:
            self.remove(b)
        self.last_barrier = None
        self.first_barrier = None
        self.init_barriers()


class Game:
    def __init__(self):
        self.is_over = False
        self.bird = Bird()
        self.group = pygame.sprite.Group()
        self.group.add(self.bird)
        self.barrier_group = BarrierManager()
        self.capture_name = './capture.png'
        self.rgb = None
        self.count = 0

    def mainGame(self, action):
        Screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        # 更新数据
        if action == 1 and self.bird.Y > 10:
            self.bird.Y -= 11
            self.bird.current_image = 0
        self.group.update()
        self.group.draw(Screen)
        if self.barrier_group.group_update():
            self.count += 1
        # 碰撞检测
        if pygame.sprite.spritecollide(self.bird, self.barrier_group, False) or self.bird.Y >= HEIGHT:
            self.is_over = True
        # 更新画面
        self.capture()
        # if not render 这样能不能加快速度
        pygame.display.update()

    def capture(self):
        """
        抓取图片
        :return: 返回rgb数组
        """
        # 方法1
        # pygame.image.save(Screen, self.capture_name)
        # image = cv2.imread(self.capture_name, cv2.IMREAD_COLOR)
        # return cv2.split(image)
        # 方法2 利用内存，不去写入图片到硬盘
        # pygame.PixelArray
        # print(pygame.PixelArray(Screen))
        # 方法3 同上 但是采用pygame.Surface.get_at
        r = np.zeros((WIDTH, HEIGHT))
        g = np.zeros((WIDTH, HEIGHT))
        b = np.zeros((WIDTH, HEIGHT))
        for i in range(WIDTH):
            for j in range(HEIGHT):
                r[i][j], g[i][j], b[i][j], _ = Screen.get_at((i, j))
        self.rgb = r, g, b

    def get_screen(self):
        # 获得一部分
        r = self.rgb[0][:, 100:228]
        g = self.rgb[1][:, 100:228]
        b = self.rgb[2][:, 100:228]
        return np.array((r, g, b))

    def reset(self):
        self.bird.X = 100
        self.bird.Y = 150
        self.barrier_group.reset()
        self.is_over = False
        self.rgb = None
        self.count = 0
        self.mainGame(1)

    def end_game(self):
        self.is_over = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                keys = pygame.key.get_pressed()
                if keys[K_SPACE]:
                    return

    def step(self, action):
        """
        相当于env.step
        :param action: 动作
        :return: observation, reward, done, info
        obervation 因此这里应该返回图片或None，reward——不死+1，死了-100， done就是检测是否结束，info目前为None
        """
        self.mainGame(action)
        info = None
        reward = 1
        if self.is_over:
            reward = -100
            info = self.count
        return None, reward, self.is_over, info


if __name__ == "__main__":
    game = Game()


# todo 是否需要循环多张图片，可以建一个队列，先来先走？
#   是否需要多线程
#   目前是将图片保存到硬盘，这很耗费资源是有其他的方法
#   解决时序的问题：方法1，按顺序执行，等dqn的进入，capture后再继续运行游戏。方法2加入到env中。方法3，多线程操作？
#       目前采用第一种
#   加快速度的几种可能方法，1 去掉display.update 好像有用啊 2 将游戏变成exe可执行文件 3 好像是网络产生结果的速度太慢
#   截取一部分图片，这是个简单而且非常有效的方法。
#
