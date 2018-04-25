import pygame as pg
from settings import *


class Button(pg.sprite.Sprite):
    def __init__(self, game, text_list, x, y, name):
        self.groups = game.all_sprites, game.buttons
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((BUTTON_WIDTH, BUTTON_HEIGHT))
        self.image.fill(BUTTON_BACKGROUND)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.outline_rect = self.rect.copy()
        self.text_list = text_list
        self.name = name

    def draw_text(self):
        for offset, text in enumerate(self.text_list):
            offset *= BUTTON_FONT_SIZE
            font = pg.font.Font(FONT, BUTTON_FONT_SIZE)
            text_surface = font.render(text, True, WHITE)
            text_rect = text_surface.get_rect()
            text_rect.midtop = (self.rect.centerx, self.rect.y + 5 + offset)
            self.game.screen.blit(text_surface, text_rect)

    def get_clicked(self):
        mouse = pg.mouse.get_pressed()
        if mouse[0]:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.game.tower_selection = self.name

    def update(self, *args):
        self.get_clicked()
        if self.game.tower_selection == self.name:
            self.image.fill(BLACK)
        else:
            self.image.fill(BUTTON_BACKGROUND)
