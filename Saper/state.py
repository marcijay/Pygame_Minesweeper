import enum


class GameState(enum.Enum):
    waiting = 0
    running = 1
    won = 3
    lost = 4


class WindowMode(enum.Enum):
    game = 0
    leaderboard = 1
    entry = 3
