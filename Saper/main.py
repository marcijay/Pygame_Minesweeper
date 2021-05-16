from game import Game
from board import Board

boardSize = (10, 10)
probability = 0.3
board = Board(boardSize, probability)
windowSize = (800, 800)
game = Game(board, windowSize)
game.run()
