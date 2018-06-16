from jtd_towers.towers import *

vec = pg.math.Vector2


# Main Mob Class
class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y, name="Zombie"):
        # Layer mob is drawn
        self._layer = MOB_LAYER
        # sprite groups
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        # Name for determining which mob to spawn
        self.name = name
        self.game = game
        # debug value
        self.number = len(self.game.mobs)
        # Temporary Image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        # Get rect of sprite
        self.rect = self.image.get_rect()
        # Place sprite on the screen
        self.rect.topleft = (x, y)
        # Define vectors to calculate mob movement
        self.pos = vec(self.rect.center)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        # Mob Stats
        self.health = MOBS[self.name]["Health"]
        self.health_bar = None
        self.speed = MOBS[self.name]["Speed"]
        self.damage = MOBS[self.name]["Damage"]
        # Predefined path of mob
        self.path = self.game.mob_path
        # How far along the path the mob is
        self.path_step = 0
        # Current direction the mob is following (part of the path variable)
        self.current_direction = self.path[self.path_step][1]
        # This is now broken because I am calculating the path differently
        # works good enough for now
        self.distance_from_end = len(self.game.mob_path) - self.path_step

    def draw_health(self):
        # Display health bar as percentage of health
        health_pct = self.health / MOBS[self.name]["Health"]
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
        # depending on mob's current position, determine if it needs to change direction by comparing current position
        # to the next position
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

    # Update this frame
    def update(self):
        # check pathing algorithm
        self.follow_path()
        # Update image **TEMPORARY**
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(LIGHTGREY)
        # update position
        self.rect.center = self.pos
        # check if mob died
        if self.health <= 0:
            self.game.credits += MOBS[self.name]["Credit Value"]
            self.kill()
        # Show how far the mob is from the end for targeting purposes
        self.distance_from_end = len(self.path) - self.path_step


class Zombie(Mob):
    def __init__(self, game, x, y):
        Mob.__init__(self, game, x, y, "Zombie")
