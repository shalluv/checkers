from pygame import Surface

from const import *


class Cell:
    def __init__(self, row: int, col: int, color: int) -> None:
        self.row = row
        self.col = col
        self.color = color

    def draw(self, surface: Surface, spritesheet: Surface) -> None:
        if(self.color == EMPTY):
            return

        cell = (
            self.row * CELL_WIDTH + (CELL_WIDTH - SPRITE_WIDTH) / 2,
            self.col * CELL_HEIGHT + (CELL_HEIGHT - SPRITE_HEIGHT) / 2,
        )
        pic = (
            (self.color % SPRITE_PER_ROW) * SPRITE_WIDTH,
            (self.color // SPRITE_PER_ROW) * SPRITE_HEIGHT,
            SPRITE_WIDTH,
            SPRITE_HEIGHT,
        )

        surface.blit(spritesheet, cell, pic)
