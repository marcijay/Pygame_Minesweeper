class Tile:
    """Class responsible for depicting state of singular board tile"""
    def __init__(self, owner, position):
        self.__isMine = False
        self.__isClicked = False
        self.__isFlagged = False
        self.__position = position
        self.__adjacentTiles = []
        self.__minesAroundNo = 0
        self.__owner = owner

    def __set_minesAroundNo(self):
        mines = 0
        for tile in self.__adjacentTiles:
            if tile.is_mine():
                mines += 1
        self.__minesAroundNo = mines

    def is_mine(self):
        return self.__isMine

    def set_mine(self):
        self.__isMine = True

    def is_clicked(self):
        return self.__isClicked

    def is_flagged(self):
        return self.__isFlagged

    def set_adjacentTiles(self, adjacent):
        self.__adjacentTiles = adjacent
        self.__set_minesAroundNo()

    def get_adjacentTiles(self):
        return self.__adjacentTiles

    def get_position(self):
        return self.__position

    def get_minesAroundNo(self):
        return self.__minesAroundNo

    def toggle_flag(self):
        self.__isFlagged = not self.__isFlagged

    def click(self):
        self.__isClicked = True
