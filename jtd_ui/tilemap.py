import pygame as pg
from settings import *
import pytmx

vec = pg.math.Vector2


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


class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    # Camera class
    # Uses Arrow Keys to move around and stops at the edge of maps
    def __init__(self, width, height, map_width, map_height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

        # x and y values are in the negative, keep that in mind where any math is involved here
        self.map_width = map_width
        self.map_height = map_height

        # TODO find a better way of determining the starting location of the camera
        self.x = -int(map_width / 2) + 250
        self.y = -int(map_height / 2)
        # self.x = 0
        # self.y = 0

    def apply(self, entity):
        return entity.move(self.camera.topleft)

    def apply_circle(self, pos):
        # POS must be a vector2
        adj_pos = pos + vec(self.x, self.y)
        adj_pos = (int(adj_pos.x), int(adj_pos.y))
        return adj_pos

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self):
        keystate = pg.key.get_pressed()
        if keystate[pg.K_LEFT]:
            self.x += CAMERA_SPEED
            if self.x > 0:
                self.x = 0
        if keystate[pg.K_RIGHT]:
            self.x -= CAMERA_SPEED
            if self.x - self.width < -self.map_width:
                self.x = -self.map_width + self.width
        if keystate[pg.K_UP]:
            self.y += CAMERA_SPEED
            if self.y > 0:
                self.y = 0
        if keystate[pg.K_DOWN]:
            self.y -= CAMERA_SPEED
            if self.y - self.height < -self.map_height:
                self.y = -self.map_height + self.height
        self.camera = pg.Rect(self.x, self.y, self.width, self.height)
