import pygame
from pygame.locals import *

pygame.init()

canvas = pygame.display.set_mode((160, 90))
canvas.fill((255, 255, 255))


def handleEvent():
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            print(event.pos[0])


while True:
    handleEvent()