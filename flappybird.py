import random

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


# 画出蓝色的障碍 width是一定的，定20。如果是上边的，y是0。需要知道x和h。下面的需要知道h和x，y是400-h
def make_couple_barrier(x):
    blank_width = 70
    blank_y = random.randint(blank_width, HEIGHT-blank_width*2)
    bar1 = Barrier(x, 0, blank_y)
    bar2 = Barrier(x, blank_y+blank_width, HEIGHT-blank_width-blank_y)
    barrier_group.add(bar1)
    barrier_group.add(bar2)
    return bar1


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

    def update(self, current_time, rate=30, speed=3):
        if current_time >= self.last_time + rate:
            self.last_time = current_time
            self.X -= speed


# 读入两帧动画，用以表现小鸟的飞行
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.image_up = pygame.transform.scale(pygame.image.load('./bird_up.PNG').convert_alpha(), [25, 25])
        self.image_down = pygame.transform.scale(pygame.image.load('./bird_down.PNG').convert_alpha(), [25, 25])
        self.rect = self.image_down.get_rect()
        self.current_image = 0              # 一个toggle，记录目前是up还是down
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

    def update(self, current_time, rate=30, speed=3):
        if current_time >= self.last_time + rate:
            if self.current_image:
                self.image = self.image_up
            else:
                self.image = self.image_down
                self.current_image = 1
            self.last_time = current_time
            self.Y += speed


class BarrierManager:
    pass


last_barrier = None


def init_barriers():
    global last_barrier
    for x in range(200, 400, 120):
        print(x)
        make_couple_barrier(x)
    last_barrier = make_couple_barrier(440)


def barriers_update(ticks, rate=50, speed=3):
    global last_barrier
    barrier_group.update(ticks, rate, speed)
    barrier_group.draw(Screen)
    # 生成新的
    if last_barrier.X < 321:
        last_barrier = make_couple_barrier(440)

    # 销毁老的
    for b in barrier_group:
        if b.X <= -25:
            barrier_group.remove(b)


framerate = pygame.time.Clock()
bird = Bird()
bird.X = 100
bird.Y = 200
group = pygame.sprite.Group()
group.add(bird)
# 用两个bg交替生成背景，决定采用随机动态生成
barrier_group = pygame.sprite.Group()
init_barriers()
is_over = True

while True:
    framerate.tick(30)
    ticks = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            if is_over:
                is_over = False
            else:
                if bird.Y > 10:
                    bird.Y -= 11
                    bird.current_image = 0

    Screen.fill(blue)
    if is_over:
        group.update(ticks, 50, 0)
        barriers_update(ticks, speed=0)
    else:
        group.update(ticks, 50)
        barriers_update(ticks)
    group.draw(Screen)
    if pygame.sprite.spritecollide(bird, barrier_group, False) or bird.Y >= HEIGHT:
        print_text(font, 300, 100, "GAME OVER")
        is_over = True
    pygame.display.update()


# todo 加分
#  barrier_manager建立
#  建立game
#  碰撞检测软边一点，可以用for b in group方法
#  开始页面 调整参数，实现截屏
