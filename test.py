import pygame
import numpy as np
import time

pygame.init()

screen = pygame.display.set_mode((3, 3))
screen.fill((0, 254, 0))

r = np.zeros((3, 3))
g = np.zeros((3, 3))
b = np.zeros((3, 3))

for i in range(3):
    for j in range(3):
        r[i][j], g[i][j], b[i][j], _ = screen.get_at((i, j))

print(r, g, b, sep='\n')
