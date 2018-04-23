import pygame as pg
from settings import *
from itertools import chain


class Tower(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.towers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Temporary Image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.pos = vec(self.rect.center)
        self.damage = TOWER_DAMAGE
        self.attack_radius = TOWER_ATTACK_RADIUS
        self.fire_rate = TOWER_FIRE_RATE
        self.color = WHITE
        self.target = None
        self.last_shot = pg.time.get_ticks()
        self.shooting = False
        self.damage_alpha = None

    # Chooses target based on how close it is to the end
    def acquire_target(self):
        mobs_in_range = []
        closest_mob = None
        # Find mobs within range of tower's radius
        for mob in self.game.mobs:
            dist = self.pos - mob.pos
            if 0 < dist.length() < self.attack_radius:
                mobs_in_range.append(mob)
        # Target the closest mob the the End sprite
        for mob in mobs_in_range:
            if closest_mob is None:
                closest_mob = mob
            elif closest_mob.distance_from_end > mob.distance_from_end and mob.alive():
                closest_mob = mob
            self.target = closest_mob
        # If there are no mobs in range, clear target
        if len(mobs_in_range) == 0:
            self.target = None

    def shoot(self):
        now = pg.time.get_ticks()
        if self.target and self.target.alive():
            if now - self.last_shot > self.fire_rate:
                self.last_shot = now
                self.shooting_anim()
                self.target.health -= self.damage

    def shooting_anim(self):
        # Flash as shooting
        self.shooting = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 2)

    def update(self, *args):
        self.acquire_target()
        self.shoot()
        self.image.fill(WHITE)
        if self.shooting:
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.shooting = False


class GunTower(Tower):
    def __init__(self):

