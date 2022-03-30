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


class Barrier(pygame.sprite.Sprite):
    # 获得一个随机数
    def __init__(self, x, y, h):
        pygame.sprite.Sprite.__init__(self)
        self.rect = Rect(x, y, 25, h)
        image = pygame.Surface([25, h]).convert_alpha()
        image.fill(green)
        self.image = image
        self.last_time = 0
        assert 1 == 1

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

    def update(self, current_time, rate=30, speed=3):
        if current_time >= self.last_time + rate:
            if self.current_image:
                self.image = self.image_up
            else:
                self.image = self.image_down
                self.current_image = 1
            self.last_time = current_time
            self.Y += speed


class BarrierManager(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
        self.last_barrier = None
        self.second_barrier = None
        self.first_barrier = None

    def group_update(self, ticks, rate=50, speed=3):
        self.update(ticks, rate, speed)
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
        self.is_over = True
        self.bird = Bird()
        self.group = pygame.sprite.Group()
        self.group.add(self.bird)
        self.barrier_group = BarrierManager()
        self.capture_name = './capture.png'
        self.count = 0

    def startGame(self):
        self.reset()
        while True:
            self.framerate.tick(30)
            ticks = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                keys = pygame.key.get_pressed()
                if keys[K_SPACE]:
                    if self.is_over:
                        self.is_over = False
                    else:
                        if self.bird.Y > 10:
                            self.bird.Y -= 11
                            self.bird.current_image = 0

            Screen.fill(blue)
            if self.is_over:
                self.group.update(ticks, 50, 0)
                self.barrier_group.group_update(ticks, speed=0)
            else:
                self.group.update(ticks, 50)
                if self.barrier_group.group_update(ticks):
                    self.count += 1
            self.group.draw(Screen)
            print_text(font, 5, 5, str(self.count), black)
            if pygame.sprite.spritecollide(self.bird, self.barrier_group, False) or self.bird.Y >= HEIGHT:
                print_text(font, 300, 100, "GAME OVER")
                self.end_game()
                self.reset()
            pygame.display.update()
            pygame.image.save(Screen, self.capture_name)

    def reset(self):
        self.framerate = pygame.time.Clock()
        self.is_over = True
        self.bird.X = 100
        self.bird.Y = 150
        self.barrier_group.reset()
        self.count = 0

    @staticmethod
    def end_game():
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                keys = pygame.key.get_pressed()
                if keys[K_SPACE]:
                    return


game = Game()
game.startGame()
