from settings import *
from jtd_mobs.mobs import Mob


class TowerNode(pg.sprite.Sprite):
    # Sprite that creates a node where towers can be placed
    def __init__(self, game, x, y):
        self.groups = game.nodes, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Temporary image
        self.rect = pg.Rect(x, y, TILESIZE, TILESIZE)
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


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self._layer = WALL_LAYER
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y