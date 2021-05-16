from tile import Tile
from random import random


class Board:
    def __init__(self, size, probability):
        self.__size = size
        self.__bombProbability = probability
        self.__board = self.set_board()
        self.set_adjacent()

    def set_board(self):
        board = []
        for row in range(self.__size[0]):
            row = []
            for col in range(self.__size[1]):
                isBomb = random() < self.__bombProbability
                tile = Tile(isBomb)
                row.append(tile)
            board.append(row)
        return board

    def set_adjacent(self):
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
