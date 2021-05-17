from tile import Tile
from random import randint


class Board:
    def __init__(self, size, probability, bombs):
        self.__lost = False
        self.__uncoveredTiles = 0
        self.__bombs = bombs
        self.__size = size
        self.__bombProbability = probability
        self.__board = self.__set_board()
        self.__place_bombs()
        self.__set_adjacent()

    def __set_board(self):
        board = []
        for row in range(self.__size[0]):
            row = []
            for col in range(self.__size[1]):
                tile = Tile()
                row.append(tile)
            board.append(row)
        return board

    def __set_adjacent(self):
        for row in range(self.__size[0]):
            for col in range(self.__size[1]):
                tile = self.get_tile((row, col))
                adjacent = self.get_adjacent_tiles((row, col))
                tile.set_adjacentTiles(adjacent)

    def get_adjacent_tiles(self, index):
        adjacent = []
        for row in range(index[0] - 1, index[0] + 2):
            for col in range(index[1] - 1, index[1] + 2):
                isOutOfBoard = row < 0 or row >= self.__size[0] or col < 0 or col >= self.__size[1]
                isSameTile = row == index[0] and col == index[1]
                if not (isOutOfBoard or isSameTile):
                    adjacent.append(self.get_tile((row, col)))
        return adjacent

    def get_size(self):
        return self.__size

    def get_board(self):
        return self.__board

    def get_tile(self, index):
        return self.__board[index[0]][index[1]]

    def handle_click(self, tile, flag):
        if tile.is_clicked() or (not flag and tile.is_flagged()):
            return
        if flag:
            tile.toggle_flag()
            return
        tile.click()
        if tile.is_bomb():
            self.__lost = True
            return
        self.__uncoveredTiles += 1
        if tile.get_bombsAroundNo() != 0:
            return
        for adjacent in tile.get_adjacentTiles():
            if not adjacent.is_bomb() and not adjacent.is_clicked():
                self.handle_click(adjacent, False)

    def check_if_victory(self):
        return self.__uncoveredTiles == self.__size[0] * self.__size[1] - self.__bombs

    def get_lost(self):
        return self.__lost

    def __place_bombs(self):
        for n in range(self.__bombs):
            while True:
                x = randint(0, self.__size[1] - 1)
                y = randint(0, self.__size[0] - 1)
                if not self.get_tile((x, y)).is_bomb():
                    self.get_tile((x, y)).set_bomb()
                    break
