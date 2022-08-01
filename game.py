import pygame

from cell import Cell
from const import *


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)

        self.spritesheet = pygame.image.load(
            'img/checkers.png').convert_alpha()
        pygame.display.set_icon(self.spritesheet)

        self.menu_background = pygame.image.load("img/help_me.png")
        self.background = pygame.image.load("img/board.png")
        self.font = pygame.font.SysFont(None, 72)
        self.font2 = pygame.font.SysFont(None, 36)

        self.board = [[Cell(i, j, EMPTY) for i in range(8)] for j in range(8)]
        self.select = None
        self.turn = RED
        self.possible_moves = []
        self.forcible_moves = []
        self.selection_changable = True
        self.black_count = 0
        self.red_count = 8

        self.game_state = "menu"

    def play(self) -> None:
        # staring positions
        for i in range(2):
            for j in range(8):
                if((i + j) % 2 == 1):
                    self.board[i][j].color = BLACK
                    self.board[7 - i][7 - j].color = RED

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                    self.handle_click()

            self.surface.blit(self.background, (0, 0))

            if(self.select is not None):
                self.draw_trans_rect(
                    self.select[0], self.select[1], YELLOW_TRANS)
                for p_row, p_col in self.possible_moves:
                    self.draw_trans_rect(p_row, p_col, GREEN_TRANS)
                for fos_row, fos_col in self.forcible_moves:
                    self.draw_trans_rect(fos_row, fos_col, ORANGE_TRANS)

            for i in range(8):
                for j in range(8):
                    self.board[i][j].draw(self.surface, self.spritesheet)

            if(self.game_state == "menu"):
                self.surface.blit(self.menu_background, (0, 0))
                text = self.font.render(
                    "CLICK TO START", True, (255, 0, 0))
                text_rect = text.get_rect(
                    center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                self.surface.blit(text, text_rect)
            elif(self.red_count == 0):
                text = self.font.render(
                    "Black Win!", True, (0, 0, 0))
                text_rect = text.get_rect(
                    center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                text2 = self.font2.render(
                    "Click anywhere to start a new game...", True, (127, 127, 127))
                text_rect2 = text.get_rect(
                    center=(SCREEN_WIDTH/2 - 108, SCREEN_HEIGHT/2 + 72))
                self.draw_trans_rect(
                    0, 0, (200, 200, 200, 127), SCREEN_WIDTH, SCREEN_HEIGHT)
                self.surface.blit(text, text_rect)
                self.surface.blit(text2, text_rect2)
                self.game_state = "ended"
            elif(self.black_count == 0):
                text = self.font.render(
                    "Red Win!", True, (255, 0, 0))
                text_rect = text.get_rect(
                    center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                text2 = self.font2.render(
                    "Click anywhere to start a new game...", True, (127, 127, 127))
                text_rect2 = text.get_rect(
                    center=(SCREEN_WIDTH/2 - 108, SCREEN_HEIGHT/2 + 72))
                self.draw_trans_rect(
                    0, 0, (200, 0, 0, 63), SCREEN_WIDTH, SCREEN_HEIGHT)
                self.surface.blit(text, text_rect)
                self.surface.blit(text2, text_rect2)
                self.game_state = "ended"

            pygame.display.update()

    def handle_click(self) -> None:
        if(self.game_state != "running"):
            self.reset()
            return
        mouse_pos = pygame.mouse.get_pos()
        row, col = mouse_pos[1] // CELL_WIDTH, mouse_pos[0] // CELL_HEIGHT

        if(self.select == (row, col) and self.selection_changable):
            self.select = None
        elif(self.get_color(row, col) == self.turn and self.selection_changable):
            self.select = (row, col)
            self.possible_moves = self.possible_moves_calculator()
            self.forcible_moves = self.forcible_moves_calculator(
                self.select[0], self.select[1])
        elif(self.select is not None and ((row, col) in self.possible_moves and len(self.forcible_moves) == 0)):
            self.move(row, col)
            self.next_turn()
        elif((row, col) in self.forcible_moves):
            self.move(row, col)
            self.forcible_moves = self.forcible_moves_calculator(row, col)

            if(self.turn == RED):
                self.black_count -= 1
            else:
                self.red_count -= 1

            if(len(self.forcible_moves) == 0):
                self.next_turn()
            else:
                self.select = (row, col)
                self.selection_changable = False

    def next_turn(self):
        for i in range(8):
            if(self.get_color(0, i) == RED):
                self.board[0][i].color = RED_KING
            elif(self.get_color(7, i) == BLACK):
                self.board[7][i].color = BLACK_KING

        self.turn = RED if self.turn == BLACK else BLACK
        self.select = None
        self.possible_moves = []
        self.forcible_moves = []
        self.selection_changable = True

        for i in range(8):
            for j in range(8):
                if(self.get_color(i, j) == self.turn):
                    tmp_pos_moves = self.possible_moves_calculator(i, j)
                    if(len(tmp_pos_moves) > 0):
                        return

        if(self.turn == RED):
            self.red_count = 0
        else:
            self.black_count = 0

    def move(self, t_row, t_col) -> None:
        f_row, f_col = self.select
        self.board[t_row][t_col].color = self.board[f_row][f_col].color
        step = abs(t_row - f_row)
        direc = [1 if f_row < t_row else -1, 1 if f_col < t_col else -1]
        for i in range(step):
            self.board[f_row + i * direc[0]
                       ][f_col + i * direc[1]].color = EMPTY

    def draw_trans_rect(self, row, col, color, wid=CELL_WIDTH, hei=CELL_HEIGHT) -> None:
        def draw_transparent_rect_utils(color, rect) -> None:
            rect_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
            pygame.draw.rect(rect_surf, color, rect_surf.get_rect())
            self.surface.blit(rect_surf, rect)

        draw_transparent_rect_utils(color,
                                    pygame.Rect(col * wid, row * hei,
                                                wid, hei))

    def possible_moves_calculator(self, row=None, col=None) -> list:
        possible_moves = []
        if(row == None or col == None):
            if(self.select == None):
                return []
            row, col = self.select

        for i in range(8):
            for j in range(8):
                if(self.get_color(i, j) == self.turn):
                    self.forcible_moves_calculator(i, j)
                    if(len(self.forcible_moves) > 0):
                        return []

        x = -1 if self.turn == RED else 1
        if(not self.is_king(self.board[row][col].color)):
            for y in [1, -1]:
                if(not is_exceed(row + x, col + y) and self.get_color(row + x, col + y) == EMPTY):
                    possible_moves.append((row + x, col + y))
        else:
            for direc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
                for i in range(1, 8):
                    if(is_exceed(row + i * direc[0], col + i * direc[1]) or self.get_color(row + i * direc[0], col + i * direc[1]) != EMPTY):
                        break
                    possible_moves.append(
                        (row + i * direc[0], col + i * direc[1]))

        return possible_moves

    def forcible_moves_calculator(self, row, col) -> list:
        forcible_moves = []
        color = self.get_color(row, col)
        if(not self.is_king(self.board[row][col].color)):
            x = -1 if color == RED else 1
            for y in [1, -1]:
                if(not is_exceed(row + 2 * x, col + 2 * y) and self.get_color(row + x, col + y) != color and self.get_color(row + x, col + y) != EMPTY and self.get_color(row + 2 * x, col + 2 * y) == EMPTY):
                    forcible_moves.append(
                        (row + 2 * x, col + 2 * y))
        else:
            for direc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
                for i in range(1, 8):
                    if(is_exceed(row + (i + 1) * direc[0], col + (i + 1) * direc[1])):
                        break
                    if(self.get_color(row + i * direc[0], col + i * direc[1]) != EMPTY and self.get_color(row + i * direc[0], col + i * direc[1]) != color):
                        if(self.get_color(row + (i + 1) * direc[0], col + (i + 1) * direc[1]) == EMPTY):
                            forcible_moves.append(
                                (row + (i + 1) * direc[0], col + (i + 1) * direc[1]))
                        break
        return forcible_moves

    def get_color(self, row, col):
        return self.board[row][col].color - (self.board[row][col].color % 2)

    def is_king(self, color):
        return True if color % 2 == 1 else False

    def reset(self):
        self.board = [[Cell(i, j, EMPTY) for i in range(8)]
                      for j in range(8)]
        self.select = None
        self.turn = RED
        self.possible_moves = []
        self.forcible_moves = []
        self.selection_changable = True
        self.black_count = 8
        self.red_count = 8

        self.game_state = "running"

        for i in range(2):
            for j in range(8):
                if((i + j) % 2 == 1):
                    self.board[i][j].color = BLACK
                    self.board[7 - i][7 - j].color = RED


def is_exceed(row, col):
    return True if(row > 7 or col > 7 or row < 0 or col < 0) else False
