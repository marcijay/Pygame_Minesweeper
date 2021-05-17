class Tile:
    def __init__(self):
        self.__isBomb = False
        self.__isClicked = False
        self.__isFlagged = False
        self.__adjacentTiles = []
        self.__bombsAroundNo = 0

    def is_bomb(self):
        return self.__isBomb

    def set_bomb(self):
        self.__isBomb = True

    def is_clicked(self):
        return self.__isClicked

    def is_flagged(self):
        return self.__isFlagged

    def set_adjacentTiles(self, adjacent):
        self.__adjacentTiles = adjacent
        self.__set_bombsAroundNo()

    def get_adjacentTiles(self):
        return self.__adjacentTiles

    def get_bombsAroundNo(self):
        return self.__bombsAroundNo

    def __set_bombsAroundNo(self):
        bombs = 0
        for tile in self.__adjacentTiles:
            if tile.is_bomb():
                bombs += 1
        self.__bombsAroundNo = bombs

    def toggle_flag(self):
        self.__isFlagged = not self.__isFlagged

    def click(self):
        self.__isClicked = True
