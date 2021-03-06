import pygame as pg
# from towers import GunTower, CannonTower

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LIGHTRED = (200, 0, 0)
GREEN = (0, 255, 0)
LIGHTGREEN = (0, 200, 0)
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
TITLE = "TOWER DEFENSE!!!!!"
BGCOLOR = DARKGREY
FONT = pg.font.match_font("arial")

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Button Settings
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 100
BUTTON_FONT_SIZE = 15
BUTTON_BACKGROUND = LIGHTGREY

# Player settings
STARTING_CASH = 500

# Tower settings
TOWERS = {
    "Gun": {
        # "Class": GunTower,
        "Damage": 10,
        "Attack Radius": 200,
        "Fire Rate": 250,
        "Cost": 250,
        "Refund": 0.75,
    },
    "Cannon": {
        # "Class": CannonTower,
        "Damage": 50,
        "Attack Radius": 400,
        "Fire Rate": 1000,
        "Cost": 350,
        "Refund": 0.75,
    },
}

# Tower Images
TOWER_IMAGES = {"Double Barrel": "DoubleBarrelTower.png",
                "Double Missile": "DoubleMissileTower.png",
                "Large Missile": "LargeMissileTower.png",
                "Single Barrel": "SingleBarrelTower.png",
                "Base Tower": "Tower1.png"}

# Bullet Images
BULLET_IMAGES = {}

# MOB Images
MOB_IMAGES = {"Knight": "Knight.png",
              "Plane1": "Plane1.png",
              "Plane2": "Plane2.png",
              "Robot": "Robot.png",
              "Soldier": "Soldier.png",
              "Zombie": "Zombie.png"}

# Mob settings
MOBS = {
    "Zombie": {
        # add image later
        "Image": None,
        "Speed": 100,
        "Health": 100,
        "Damage": 500,
        "Credit Value": 25
    }
}

# Spawn settings
SPAWN_DELAY = 1000
WAVE_SIZE = 50

# End settings
END_HEALTH = 1000

# Bullet settings
BULLET_SPEED = 800

# Effects
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]

# Camera Settings
CAMERA_SPEED = 10

# Layers
WALL_LAYER = 1
MOB_LAYER = 2
TOWER_LAYER = 3
EFFECTS_LAYER = 4
