import pygame as pg
from settings import *


intro = True


# Intro Screen Methods
def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()


def button(game, msg, x, y, w, h, ic, ac, action=None):
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pg.draw.rect(game.screen, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            if action == "play":
                game.intro = False
            elif action == "quit":
                pg.quit()
                quit()
    else:
        pg.draw.rect(game.screen, ic, (x, y, w, h))

    smallText = pg.font.Font("freesansbold.ttf", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    game.screen.blit(textSurf, textRect)

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pg.draw.rect(game.screen, ac, (x, y, w, h))
    else:
        pg.draw.rect(game.screen, ic, (x, y, w, h))

    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    game.screen.blit(textSurf, textRect)


def game_intro(game):
    while game.intro:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
        game.screen.fill(WHITE)
        largeText = pg.font.Font('freesansbold.ttf', 90)
        TextSurf, TextRect = text_objects("TOWER DEFENSE!!!", largeText)
        TextRect.center = ((WIDTH / 2), (HEIGHT / 2))
        game.screen.blit(TextSurf, TextRect)

        button(game, "START", 150, 450, 150, 100, LIGHTGREEN, GREEN, "play")
        button(game, "QUIT", 150, 550, 150, 100, LIGHTRED, RED, "quit")

        pg.display.update()
