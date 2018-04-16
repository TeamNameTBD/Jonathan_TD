import pygame as pg
from settings import *
from itertools import chain


vec = pg.math.Vector2


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


def collide_with_walls(sprite, group, dir):
    if dir == "X":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == "Y":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


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
            if 0 < dist.length() < TOWER_ATTACK_RADIUS:
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
        # print(self.target.alive())
        if self.target and self.target.alive():
            if now - self.last_shot > TOWER_FIRE_RATE:
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


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Temporary Image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        # Create hit rect for colision purposes, may not be needed
        self.hit_rect = MOB_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.pos = vec(self.rect.center)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.health = MOB_HEALTH
        self.health_bar = None
        self.speed = MOB_SPEED
        self.damage = MOB_DAMAGE
        self.path = self.game.mob_path
        self.path_step = 0
        self.current_direction = vec(-1, 0)
        self.distance_from_end = len(self.path) - self.path_step

    def draw_health(self):
        # Display health bar as percentage of health
        health_pct = self.health / MOB_HEALTH
        if health_pct > 0.6:
            col = GREEN
        elif health_pct > 0.3:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * health_pct)
        self.health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(self.image, col, self.health_bar)

    def update_direction(self):
        if self.path[self.path_step] - self.pos == -self.current_direction:
            self.path_step += 1
        try:
            self.current_direction = vec(self.path[self.path_step] - self.pos).normalize()
        except ValueError:
            self.path_step += 1
            self.current_direction = vec(self.path[self.path_step] - self.pos).normalize()

    def follow_path(self):
        dir = self.update_direction()
        if dir in [(1, 1), (1, -1), (-1, 1), (-1, -1), -self.current_direction]:
            self.pos = self.path[self.path_step]
            dir = self.update_direction()
        else:
            self.vel = dir * self.speed
            self.pos += self.vel * self.game.dt

        self.current_direction = dir

    def update(self):
        # The mob only needs to travel to the left
        # self.follow_path()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        self.vel = self.current_direction * self.speed
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "X")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "Y")
        self.rect.center = self.hit_rect.center
        self.update_direction()
        if self.health <= 0:
            self.kill()
        self.distance_from_end = len(self.path) - self.path_step


class TowerNode(pg.sprite.Sprite):
    # Sprite that creates a node where towers can be placed
    # Maybe should be a subclass of wall?
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Temporary image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = pg.time.get_ticks()
        self.tower = None

    def get_clicked(self):
        # If the sprite is left clicked, spawn a tower
        mouse = pg.mouse.get_pressed()
        if mouse[0]:
            if self.rect.collidepoint(pg.mouse.get_pos()) and self.tower is None:
                self.tower = Tower(self.game, self.rect.x, self.rect.y)

    def update(self):
        self.get_clicked()


class Spawn(pg.sprite.Sprite):
    # Spawning point
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.last_spawn = pg.time.get_ticks()
        self.mobs_spawned = 0

    def spawn_mob(self):
        Mob(self.game, self.rect.x, self.rect.y)

    def update(self, *args):
        now = pg.time.get_ticks()
        if now - self.last_spawn > SPAWN_DELAY and self.mobs_spawned < WAVE_SIZE:
            self.last_spawn = now
            self.mobs_spawned += 1
            self.spawn_mob()


class End(pg.sprite.Sprite):
    # Ending point - Defend this!
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = END_HEALTH

    def draw_health(self):
        health_pct = self.health / END_HEALTH
        if health_pct > 0.6:
            col = GREEN
        elif health_pct > 0.3:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * health_pct)
        self.health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(self.image, col, self.health_bar)

    def update(self, *args):
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(CYAN)


# It seems like it will be very difficult to have bullets hit mobs, expecially when they have to track them around
# corners. I am going to scrap this sprite for now, and maybe call it back if slow towers like missiles or something are
# in play.
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((5, 5))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * BULLET_SPEED
        self.damage = damage

    def update(self, *args):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
