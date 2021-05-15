from game import Game
from board import Board

boardSize = (10, 10)
board = Board(boardSize)
windowSize = (800, 800)
game = Game(board, windowSize)
game.run()
