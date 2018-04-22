import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
import pathing


class Game:
    # Initialize pygame and load data
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.end = None
        self.playing = True
        self.running = True
        self.load_data()

    # Loads files into pygame
    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map_data = []
        with open(path.join(game_folder, 'map.txt'), 'rt') as f:
            for line in f:
                self.map_data.append(line)
        # determing pathing solution
        width, height, walls, start, end = pathing.load_map("map.txt")
        mob_path = pathing.AStar()
        mob_path.init_grid(width, height, walls, start, end)
        mob_path = (mob_path.solve())
        mob_path = [vec(x * TILESIZE + TILESIZE / 2, y * TILESIZE + TILESIZE / 2) for (x, y) in mob_path]
        self.mob_path = pathing.find_change_in_dir(mob_path)

    # Clear all and create new game
    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.mob_timer_delay = pg.time.get_ticks()
        self.bullets = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == "1":
                    Wall(self, col, row)
                if tile == "S":
                    Spawn(self, col * TILESIZE, row * TILESIZE)
                if tile == "E":
                    self.end = End(self, col * TILESIZE, row * TILESIZE)
                if tile == "T":
                    TowerNode(self, col * TILESIZE, row * TILESIZE)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

        # mobs hit end
        hits = pg.sprite.spritecollide(self.end, self.mobs, False)
        for hit in hits:
            self.end.health -= hit.damage
            hit.kill()

        # Check for ending conditions:
        # print(f"end health: {self.end.health}")
        # print(f"# of mobs: {len(self.mobs)}")
        if self.end.health == 0:
            self.playing = False
        now = pg.time.get_ticks()
        if now - self.mob_timer_delay > SPAWN_DELAY:
            if len(self.mobs) == 0:
                self.playing = False

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob) or isinstance(sprite, End):
                sprite.draw_health()
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


# create the game object
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.run()
    g.show_go_screen()
