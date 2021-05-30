import enum


class GameState(enum.Enum):
    waiting = 0
    running = 1
    won = 2
    lost = 3


class WindowMode(enum.Enum):
    game = 0
    leaderboard = 1
    entry = 2
    delete = 3
