import pygame as pg
from settings import *
from towers import *

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


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.number = len(self.game.mobs)
        # Temporary Image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.pos = vec(self.rect.center)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.health = MOB_HEALTH
        self.health_bar = None
        self.speed = MOB_SPEED
        self.damage = MOB_DAMAGE
        self.path = self.game.mob_path
        self.path_step = 0
        self.current_direction = self.path[self.path_step][1]
        # This is now broken because I am calculating the path differently
        self.distance_from_end = len(self.game.mob_path) - self.path_step

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

    def follow_path(self):
        current_step = self.path_step
        self.vel = self.current_direction * self.speed
        self.pos += self.vel * self.game.dt
        # check if self.pos is past the change vector
        # Check x value
        # Going Right
        if self.current_direction.x == 1:
            if self.path[self.path_step + 1][0].x < self.pos.x:
                self.path_step += 1
                self.pos.x = self.path[self.path_step][0].x
                self.current_direction = self.path[self.path_step][1]
        # Going left
        elif self.current_direction.x == -1:
            if self.path[self.path_step + 1][0].x > self.pos.x:
                self.path_step += 1
                self.pos.x = self.path[self.path_step][0].x
                self.current_direction = self.path[self.path_step][1]
        # Check y value
        # Down
        elif self.current_direction.y == 1:
            if self.path[self.path_step + 1][0].y < self.pos.y:
                self.path_step += 1
                self.pos.y = self.path[self.path_step][0].y
                self.current_direction = self.path[self.path_step][1]
        # Up
        elif self.current_direction.y == -1:
            if self.path[self.path_step + 1][0].y > self.pos.y:
                self.path_step += 1
                self.pos.y = self.path[self.path_step][0].y
                self.current_direction = self.path[self.path_step][1]

    def update(self):
        self.follow_path()
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        self.rect.center = self.pos
        if self.health <= 0:
            self.game.credits += CREDIT_VALUE
            self.kill()
        self.distance_from_end = len(self.path) - self.path_step


class TowerNode(pg.sprite.Sprite):
    # Sprite that creates a node where towers can be placed
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
        mouse_pos = list(pg.mouse.get_pos())
        mouse_pos[0] -= self.game.camera.x
        mouse_pos[1] -= self.game.camera.y
        mouse_pos = tuple(mouse_pos)
        if self.rect.collidepoint(mouse_pos):
            print("Collide")
        if mouse[0]:
            if self.rect.collidepoint(
                    mouse_pos) and self.tower is None and self.game.tower_selection != "Sell":
                if self.game.credits >= TOWERS[self.game.tower_selection]["Cost"]:
                    if self.game.tower_selection == "Gun":
                        self.tower = GunTower(self.game, self.rect.x, self.rect.y)
                        self.game.credits -= TOWERS[self.game.tower_selection]["Cost"]
                    elif self.game.tower_selection == "Cannon":
                        self.tower = CannonTower(self.game, self.rect.x, self.rect.y)
                        self.game.credits -= TOWERS[self.game.tower_selection]["Cost"]
            elif self.rect.collidepoint(mouse_pos) and self.tower and self.game.tower_selection == "Sell":
                self.game.credits += int(TOWERS[self.tower.name]["Cost"] * TOWERS[self.tower.name]["Refund"])
                self.tower.kill()
                self.tower = None

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
