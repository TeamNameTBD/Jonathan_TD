import pygame as pg
import random
import sys
from os import path
from settings import *
from sprites import *
from towers import *
from tilemap import *
from buttons import Button
import pathing


class Game:
    # Initialize pygame and load data

    def __init__(self):
        # Initialize Pygame
        pg.init()
        # Create screen object
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        # Set Caption
        pg.display.set_caption(TITLE)
        # Start game clock
        self.clock = pg.time.Clock()
        # Set the rate that a key will repeat while held down
        pg.key.set_repeat(500, 100)
        # Variable to know if the game has ended
        self.end = None
        # Variable if game is playing
        self.playing = True
        # Variable if game is running
        self.running = True
        # Load base game data
        self.load_data()

        # Buttons
        self.gun_tower_button = None
        self.cannon_tower_button = None
        self.sell_tower_button = None

    # Loads files into pygame
    def load_data(self):
        # Directory of the game
        game_folder = path.dirname(__file__)

        # Pathing algorythm
        self.map = Map(path.join(game_folder, 'map2.txt'))


        # determing pathing solution
        width, height, walls, start, end = pathing.load_map("map2.txt")
        mob_path = pathing.AStar()
        mob_path.init_grid(width, height, walls, start, end)
        mob_path = (mob_path.solve())
        mob_path = [vec(x * TILESIZE + TILESIZE / 2, y * TILESIZE + TILESIZE / 2) for (x, y) in mob_path]
        self.mob_path = pathing.find_change_in_dir(mob_path)

    # Method to draw text on the screen
    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    # Clear all and create new game
    def new(self):
        # initialize all variables and do all the setup for a new game
        self.credits = STARTING_CASH
        self.all_sprites = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.mob_timer_delay = pg.time.get_ticks()
        self.bullets = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.buttons = pg.sprite.Group()
        self.tower_selection = "Gun"
        self.end_condition = ""
        self.gun_tower_button = Button(self, ["Gun Tower", f"Cost: {TOWERS['Gun']['Cost']}"],
                                       WIDTH * 0.05, HEIGHT * 0.85, "Gun")
        self.cannon_tower_button = Button(self, ["Cannon Tower", f"Cost: {TOWERS['Cannon']['Cost']}"],
                                          WIDTH * 0.15, HEIGHT * 0.85, "Cannon")
        self.sell_tower_button = Button(self, ["Sell Tower", "75% Refund"], WIDTH * 0.25, HEIGHT * 0.85, "Sell")

        self.camera = Camera(self.map.width, self.map.height)

        # Read through map and spawn tiles accordingly
        for row, tiles in enumerate(self.map.data):
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
            # Game Clock
            self.dt = self.clock.tick(FPS) / 1000

            # Main loop
            self.events()
            self.update()
            self.draw()

    # Quit the game and close the window
    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update()

        # mobs hit end
        hits = pg.sprite.spritecollide(self.end, self.mobs, False)
        for hit in hits:
            self.end.health -= hit.damage
            hit.kill()

        # Check for ending conditions:
        if self.end.health == 0:
            self.end_condition = "lose"
            self.playing = False
        now = pg.time.get_ticks()
        if now - self.mob_timer_delay > SPAWN_DELAY:
            if len(self.mobs) == 0:
                self.end_condition = "win"
                self.playing = False

    # Debug method to show grid
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    # Draw the screen
    def draw(self):
        self.screen.fill(BGCOLOR)
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob) or isinstance(sprite, End):
                sprite.draw_health()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite.rect))
        self.draw_text(f"Credits: {self.credits}", FONT, 30, WHITE, 35, 30, align="nw")
        for button in self.buttons:
            button.draw_text()
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    # Intro Screen Methods
    def text_objects(self, text, font):
        textSurface = font.render(text, True, BLACK)
        return textSurface, textSurface.get_rect()

    def button(self, msg, x, y, w, h, ic, ac, action=None):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()

        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            pg.draw.rect(self.screen, ac, (x, y, w, h))
            if click[0] == 1 and action != None:
                if action == "play":
                    self.intro = False
                elif action == "quit":
                    pg.quit()
                    quit()
        else:
            pg.draw.rect(self.screen, ic, (x, y, w, h))

        smallText = pg.font.Font("freesansbold.ttf", 20)
        textSurf, textRect = self.text_objects(msg, smallText)
        textRect.center = ((x + (w / 2)), (y + (h / 2)))
        self.screen.blit(textSurf, textRect)

        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            pg.draw.rect(self.screen, ac, (x, y, w, h))
        else:
            pg.draw.rect(self.screen, ic, (x, y, w, h))

        textSurf, textRect = self.text_objects(msg, smallText)
        textRect.center = ((x + (w / 2)), (y + (h / 2)))
        self.screen.blit(textSurf, textRect)

    def game_intro(self):
        self.intro = True
        while self.intro:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            self.screen.fill(WHITE)
            largeText = pg.font.Font('freesansbold.ttf', 90)
            TextSurf, TextRect = self.text_objects("TOWER DEFENSE!!!", largeText)
            TextRect.center = ((WIDTH / 2), (HEIGHT / 2))
            self.screen.blit(TextSurf, TextRect)

            self.button("START", 150, 450, 150, 100, LIGHTGREEN, GREEN, "play")
            self.button("QUIT", 150, 550, 150, 100, LIGHTRED, RED, "quit")

            pg.display.update()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        # game over/continue
        self.screen.fill(BLACK)
        if self.end_condition == "win":
            self.draw_text("You win!", FONT, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
        elif self.end_condition == "lose":
            self.draw_text("You lose!", FONT, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press a key to return to main menu", FONT, 75, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

# create the game object

g = Game()
g.show_start_screen()


while g.running:
    g.game_intro()
    g.new()
    g.run()
    g.show_go_screen()

