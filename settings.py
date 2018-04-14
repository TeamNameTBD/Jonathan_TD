import pygame as pg

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

TILESIZE = 32
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Tower settings
TOWER_DAMAGE = 10
TOWER_ATTACK_RADIUS = 200
TOWER_FIRE_RATE = 250

# Mob settings
MOB_SPEED = 100
MOB_HEALTH = 100
MOB_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE)
MOB_DAMAGE = 500

# Spawn settings
SPAWN_DELAY = 1000
WAVE_SIZE = 5

# End settings
END_HEALTH = 1000

# Bullet settings
BULLET_SPEED = 800

# Effects
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]
