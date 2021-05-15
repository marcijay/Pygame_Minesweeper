from tile import Tile


class Board:
    def __init__(self, size):
        self.__size = size
        self.__board = self.set_board()

    def set_board(self):
        board = []
        for row in range(self.__size[0]):
            row = []
            for col in range(self.__size[1]):
                tile = Tile()
                row.append(tile)
            board.append(row)
        return board

    def get_size(self):
        return self.__size

    def get_boaed(self):
        return self.__board
