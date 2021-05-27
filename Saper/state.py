import enum


class GameState(enum.Enum):
    waiting = 0
    running = 1
    won = 3
    lost = 4


class WindowState(enum.Enum):
    game = 0
    leaderboard = 1
    winner_entry = 3
