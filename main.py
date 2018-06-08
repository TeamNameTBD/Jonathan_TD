import sys
from os import path
from jtd_mobs.sprites import *
from jtd_towers.towers import *
from jtd_ui.tilemap import *
from jtd_ui.buttons import Button
from jtd_ui import pathing
from jtd_ui import game_intro


"""

Jonathan's Tower Defence Game
- Better name tbd :)

Developed by Tensor Studios
Jonathan Layman
Andrew Albright
Devin Emnett

Art by Kenny
Kenny.nl


"""


# This is the main game class. All methods of the game are called as a part of this class. it is called at the bottom
# of the file.
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
        # Directories
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, "maps")
        img_folder = path.join(game_folder, "img")

        # Pathing algorythm
        self.map = TiledMap(path.join(map_folder, "Map2.tmx"))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()


        # determing pathing solution
        pathing.load_tiled_map(self.map)
        width, height, walls, start, end = pathing.load_map("map.txt")
        mob_path = pathing.AStar()
        mob_path.init_grid(width, height, walls, start, end)
        mob_path = (mob_path.solve())
        mob_path = [vec(x * TILESIZE + TILESIZE / 2, y * TILESIZE + TILESIZE / 2) for (x, y) in mob_path]
        self.mob_path = pathing.find_change_in_dir(mob_path)

        # Load all images
        self.zombie_img = pg.image.load(path.join(img_folder, MOB_IMAGES["Zombie"])).convert_alpha()
        self.single_barrel_img = pg.image.load(path.join(img_folder, TOWER_IMAGES["Single Barrel"])).convert_alpha()
        self.gun_fire_img = pg.image.load(path.join(img_folder, "fire1.png")).convert_alpha()

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
        # Player Money
        self.credits = STARTING_CASH

        # Time between mob spawns
        # TODO create a more complex way of determining this so that better waves can be created
        self.mob_timer_delay = pg.time.get_ticks()

        # Sprite groups
        self.all_sprites = pg.sprite.Group()
        self.nodes = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.buttons = pg.sprite.Group()

        # Spawn buttons on screen
        # Initial Gun Selection
        self.tower_selection = "Gun"
        # Create and spawn buttons
        self.gun_tower_button = Button(self, ["Gun Tower", f"Cost: {TOWERS['Gun']['Cost']}"],
                                       WIDTH * 0.05, HEIGHT * 0.85, "Gun")
        self.cannon_tower_button = Button(self, ["Cannon Tower", f"Cost: {TOWERS['Cannon']['Cost']}"],
                                          WIDTH * 0.15, HEIGHT * 0.85, "Cannon")
        self.sell_tower_button = Button(self, ["Sell Tower", "75% Refund"], WIDTH * 0.25, HEIGHT * 0.85, "Sell")

        # End condition is string, can be "win" or "lose"
        self.end_condition = ""

        # Spawn Camera
        self.camera = Camera(WIDTH, HEIGHT, self.map.width, self.map.height)

        # Spawn Tiles according to Tiled Map
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == "Wall":
                Wall(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == "Start":
                Spawn(self, tile_object.x, tile_object.y)
            if tile_object.name == "End":
                self.end = End(self, tile_object.x, tile_object.y)
            if tile_object.name == "Tower":
                TowerNode(self, tile_object.x, tile_object.y)

    # Once the game is started, run the game until it ends
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
        # not all sprite groups need to be updated
        self.all_sprites.update()
        self.buttons.update()
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

        # Check if the first mob has been spawned before determining if the "win" condition has been achieved
        now = pg.time.get_ticks()
        if now - self.mob_timer_delay > SPAWN_DELAY:
            if len(self.mobs) == 0:
                self.end_condition = "win"
                self.playing = False

    # Draw the screen
    def draw(self):
        # draw the map onto the screen
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        # draw health bars for mobs and End point
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob) or isinstance(sprite, End):
                sprite.draw_health()

        # update sprites
        # draw all sprites onto the screen
        for sprite in self.all_sprites:
            if self.nodes not in sprite.groups:
                self.screen.blit(sprite.image, self.camera.apply(sprite.rect))

        # if the mouse is hovering over a tower, draw that tower's range
        for tower in self.towers:
            mouse_pos = list(pg.mouse.get_pos())
            mouse_pos[0] -= self.camera.x
            mouse_pos[1] -= self.camera.y
            mouse_pos = tuple(mouse_pos)
            if tower.rect.collidepoint(mouse_pos):
                pg.draw.circle(self.screen, WHITE, self.camera.apply_circle(tower.pos), tower.attack_radius, 5)

        # Draw the player's current money
        self.draw_text(f"Credits: {self.credits}", FONT, 30, WHITE, 35, 30, align="nw")
        # Draw all buttons
        self.buttons.draw(self.screen)
        # Draw text on buttons
        for button in self.buttons:
            button.draw_text()

        # Display all loaded data to physical screen
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            # Quit if Window Close is pressed
            if event.type == pg.QUIT:
                self.quit()
            # Quit if ESC is presses
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        # Run the game intro screen
        self.intro = True
        game_intro.game_intro(self)

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

while g.running:
    g.show_start_screen()
    g.new()
    g.run()
    g.show_go_screen()

