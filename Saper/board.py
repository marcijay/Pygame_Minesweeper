import pygame
from tile import Tile
from random import randint
from state import GameState


def create_background(rows, cols, tileSize, bgColor, lineColor):
    field = pygame.Surface((cols * tileSize, rows * tileSize))
    field.fill(bgColor)

    for i in range(rows):
        pygame.draw.line(field, lineColor, (0, i * tileSize), (cols * tileSize, i * tileSize))

    for j in range(cols):
        pygame.draw.line(field, lineColor, (j * tileSize, 0), (j * tileSize, rows * tileSize))

    return field


class Board:
    def __init__(self, size, bombs, tileSize, owner):
        self.__size = size
        self.__bombs = bombs
        self.__flagsLeft = bombs
        self.__clearTilesLeft = self.__size[0] * self.__size[1] - self.__bombs

        self.__tileSize = tileSize
        self.__owner = owner
        self.__bgColour = pygame.Color(210, 210, 210)
        self.__linesColour = pygame.Color(10, 10, 10)
        self.__background = create_background(self.__size[0], self.__size[1], self.__tileSize,
                                              self.__bgColour, self.__linesColour)
        self.__grid = self.__set_grid()

        self.__startTime = None
        self.__time = 0

        self.__rect = pygame.Rect(0, 0, self.__size[0] * self.__tileSize, self.__size[1] * self.__tileSize)
        self.__status = GameState.waiting

    def draw(self, surface):
        background = self.__background.copy()
        self.__draw_tiles(background)
        surface.blit(background, self.__rect)

    def __draw_tiles(self, background):
        leftCorner = (0, 0)
        for row in range(self.__size[0]):
            for col in range(self.__size[1]):
                tile = self.get_tile((row, col))
                icon = self.__owner.get_tile_icon(tile)
                background.blit(icon, leftCorner)
                leftCorner = leftCorner[0] + self.__tileSize, leftCorner[1]
            leftCorner = 0, leftCorner[1] + self.__tileSize

    def __set_grid(self):
        board = []
        x = y = 0
        for row in range(self.__size[0]):
            row = []
            for col in range(self.__size[1]):
                tile = Tile(self, (x, y))
                row.append(tile)
                y += 1
            board.append(row)
            y = 0
            x += 1
        return board

    def __reset_grid(self):
        for row in self.__grid:
            for tile in row:
                tile.reset()

    def __set_adjacent(self):
        for row in range(self.__size[0]):
            for col in range(self.__size[1]):
                tile = self.get_tile((row, col))
                adjacent = self.__get_adjacent_tiles((row, col))
                tile.set_adjacentTiles(adjacent)

    def __get_adjacent_tiles(self, index):
        adjacent = []
        for row in range(index[0] - 1, index[0] + 2):
            for col in range(index[1] - 1, index[1] + 2):
                isOutOfBoard = row < 0 or row >= self.__size[0] or col < 0 or col >= self.__size[1]
                isSameTile = row == index[0] and col == index[1]
                if not (isOutOfBoard or isSameTile):
                    adjacent.append(self.get_tile((row, col)))
        return adjacent

    def get_tile(self, index):
        return self.__grid[index[0]][index[1]]

    def handle_mouse_down(self, button):
        if self.__status in [GameState.waiting, GameState.won, GameState.lost]:
            return

        if button == 3:  # RMB
            xm, ym = pygame.mouse.get_pos()
            xc, yc = self.__rect.topleft
            i = (ym - yc) // self.__tileSize
            j = (xm - xc) // self.__tileSize
            if i < 0 or i >= self.__size[0]:
                i = None
            if j < 0 or j >= self.__size[1]:
                j = None

            if j is not None and i is not None:
                tile = self.get_tile((i, j))
                if not tile.is_clicked():
                    if tile.is_flagged():
                        tile.toggle_flag()
                        self.__flagsLeft += 1
                    elif not self.__flagsLeft == 0:
                        tile.toggle_flag()
                        self.__flagsLeft -= 1

    def handle_mouse_up(self, button):
        if self.__status in [GameState.won, GameState.lost]:
            return

        if button == 1:  # LMB
            xm, ym = pygame.mouse.get_pos()
            xc, yc = self.__rect.topleft
            i = (ym - yc) // self.__tileSize
            j = (xm - xc) // self.__tileSize
            if i < 0 or i >= self.__size[0]:
                i = None
            if j < 0 or j >= self.__size[1]:
                j = None
            if j is not None and i is not None:
                tile = self.get_tile((i, j))
                self.__check_tile_open(tile)

    def __check_tile_open(self, tile):
        if tile.is_flagged():
            return
        if tile.is_bomb():
            self.__change_status(GameState.lost)
            tile.click()
            return
        if not tile.is_clicked():
            if self.__status == GameState.waiting:
                self.__place_bombs(tile)
                self.__startTime = pygame.time.get_ticks()
                self.__change_status(GameState.running)
            self.__open_tiles(tile)
            return
        if tile.get_bombsAroundNo() == 0:
            return

    def __open_tiles(self, tile):
        tile.click()
        self.__clearTilesLeft -= 1
        if tile.get_bombsAroundNo() != 0:
            return
        for adjacent in tile.get_adjacentTiles():
            if not adjacent.is_bomb() and not adjacent.is_clicked() and not adjacent.is_flagged():
                self.__open_tiles(adjacent)

        if self.__clearTilesLeft == 0:
            self.__change_status(GameState.won)
            self.__bombsLeft = 0

    def check_if_won(self):
        if self.__clearTilesLeft == 0:
            self.__change_status(GameState.won)
            self.__flagsLeft = 0

    def reset(self, size=None, bombs=None):
        if size is not None:
            self.__size = size
        if bombs is not None:
            self.__bombs = bombs
        self.__flagsLeft = self.__bombs
        self.__clearTilesLeft = self.__size[0] * self.__size[1] - self.__bombs
        self.__background = create_background(self.__size[0], self.__size[1], self.__tileSize,
                                              self.__bgColour, self.__linesColour)
        self.__reset_grid()
        self.__startTime = None
        self.__time = 0
        self.__status = GameState.waiting

    def get_bombsLeft(self):
        return self.__bombsLeft

    def get_rect(self):
        return self.__rect

    def get_status(self):
        return self.__status

    def __change_status(self, newStatus):
        self.__status = newStatus

    def __place_bombs(self, tile):
        for n in range(self.__bombs):
            while True:
                x = randint(0, self.__size[1] - 1)
                y = randint(0, self.__size[0] - 1)
                if not (self.get_tile((x, y)).is_bomb()) and \
                        not (tile.get_position()[0] == x and tile.get_position()[1] == y):
                    self.get_tile((x, y)).set_bomb()
                    break
        self.__set_adjacent()
