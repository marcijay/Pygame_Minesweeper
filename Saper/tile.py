class Tile:
    def __init__(self, isBomb):
        self.__isBomb = isBomb
        self.__isClicked = False
        self.__isFlagged = False
        self.__adjacentTiles = []
        self.__bombsAroundNo = 0

    def isBomb(self):
        return self.__isBomb

    def isClicked(self):
        return self.__isClicked

    def isFlagged(self):
        return self.__isFlagged

    def set_adjacentTiles(self, adjacent):
        self.__adjacentTiles = adjacent
        self.__set_bombsAroundNo()

    def get_bombsAroundNo(self):
        return self.__bombsAroundNo

    def __set_bombsAroundNo(self):
        bombs = 0
        for tile in self.__adjacentTiles:
            if tile.isBomb():
                bombs += 1
        self.__bombsAroundNo = bombs
