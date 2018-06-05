import pygame as pg
from settings import *


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line)

        self.tilewidth = len(self.data)
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, entity):
        return entity.move(self.camera.topleft)

    def update(self):
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT]:
            self.x += CAMERA_SPEED
        if keystate[pg.K_RIGHT]:
            self.x -= CAMERA_SPEED
        if keystate[pg.K_UP]:
            self.y += CAMERA_SPEED
        if keystate[pg.K_DOWN]:
            self.y -= CAMERA_SPEED
        self.camera = pg.Rect(self.x, self.y, self.width, self.height)
