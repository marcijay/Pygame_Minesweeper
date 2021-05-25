import os
from time import sleep

import pygame

from board import Board
from ui import *
from state import *

ASSETS_DIR_PATH = os.path.join(os.path.dirname(__file__), 'assets')


def load_image(name, size=None):
    path = os.path.join(ASSETS_DIR_PATH, name)
    try:
        image = pygame.image.load(path)
    except pygame.error as error:
        raise SystemError(error)

    if size is not None:
        if isinstance(size, int):
            size = (size, size)
        image = pygame.transform.scale(image, size)

    return image


class Game:
    TILE_EDGE_LEN = 30
    FACE_EDGE_LEN = 40
    TIMER_DIG_HEIGHT = 40
    TIMER_DIG_WIDTH = 20
    TOP_BAR_HEIGHT = 50
    MARGIN_SIZE = 20
    MAX_BOARD_SIZE = 50
    MIN_BOARD_SIZE = 10
    BACKGROUND_COLOR = pygame.Color(150, 150, 150)

    def __init__(self, rows, cols, bombs):
        display_info = pygame.display.Info()
        self.__max_cols = (int(0.95 * display_info.current_w) - 3 * self.MARGIN_SIZE) // self.TILE_EDGE_LEN
        self.__max_rows = (int(0.95 * display_info.current_h) - 3 * self.MARGIN_SIZE) // self.TILE_EDGE_LEN
        self.__rows = rows
        self.__cols = cols
        self.__bombs = bombs
        self.__tileSize = self.TILE_EDGE_LEN, self.TILE_EDGE_LEN
        self.__counterSize = self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT
        self.__faceSize = self.FACE_EDGE_LEN, self.FACE_EDGE_LEN

        self.__icons = self.load_icons()

        self.__board = Board((self.__rows, self.__cols), self.__bombs, self.TILE_EDGE_LEN, self)

        self.__screen = None
        self.__screen_Rect = None
        self.__board_Rect = None
        self.__top_bar_Rect = None

        self.__face = None
        self.__flagCounter = None
        self.__timer = None

        self.__init_screen()

        self.__running = None
        self.__mode = WindowState.game

    def __init_screen(self):
        board_area_width = max(self.__cols, self.MIN_BOARD_SIZE) * self.TILE_EDGE_LEN
        board_area_height = max(self.__rows, self.MIN_BOARD_SIZE) * self.TILE_EDGE_LEN
        window_width = 2 * self.MARGIN_SIZE + board_area_width
        window_height = 2 * self.MARGIN_SIZE + self.TOP_BAR_HEIGHT + board_area_height

        self.__board_area_Rect = pygame.Rect(self.MARGIN_SIZE, self.MARGIN_SIZE + self.TOP_BAR_HEIGHT,
                                             board_area_width, board_area_height)

        self.__board.get_rect().size = (self.__cols * self.TILE_EDGE_LEN, self.__rows * self.TILE_EDGE_LEN)
        self.__board.get_rect().center = self.__board_area_Rect.center

        self.__top_bar_Rect = pygame.Rect(self.MARGIN_SIZE, self.MARGIN_SIZE, board_area_width, self.TOP_BAR_HEIGHT)
        self.__face = ImageButton(self.__icons["face_happy"],  self.__board.reset)
        self.__face.replace_rect(pygame.Rect((window_width / 2 - self.FACE_EDGE_LEN / 2,
                                              self.MARGIN_SIZE + self.TOP_BAR_HEIGHT / 2 - self.FACE_EDGE_LEN / 2),
                                             self.__faceSize))
        self.__flagCounter = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__flagCounter.replace_rect(pygame.Rect((self.MARGIN_SIZE + 5,
                                              self.MARGIN_SIZE + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5),
                                                    (3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)))
        self.__flagCounter.set_value(self.__board.get_flagsLeft())
        self.__timer = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__timer.replace_rect(pygame.Rect((window_width - self.MARGIN_SIZE - 3 * self.TIMER_DIG_WIDTH - 5,
                                                     self.MARGIN_SIZE + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5),
                                                    (3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)))

        self.__screen = pygame.display.set_mode((window_width, window_height))
        self.__screen_Rect = self.__screen.get_rect()
        self.__screen.fill(self.BACKGROUND_COLOR)

    def start_loop(self):
        self.__running = True
        while self.__running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = pygame.mouse.get_pos()
                    isRMB = pygame.mouse.get_pressed(3)[2]
                    self.handle_click(position, isRMB)
            self.draw()
            pygame.display.flip()
            if self.__board.check_if_victory():
                sound = pygame.mixer.Sound("assets/victory_sound.wav")
                sound.play()
                sleep(3)
                self.__running = False

    def start_game_loop(self):
        clock = pygame.time.Clock()
        self.__running = True
        while self.__running:
            clock.tick(30)
            self.__process_events()
            self.__draw_all()

    def __reset_game(self):
        self.__board.reset((self.__rows, self.__cols), self.__bombs)

    def __draw_all(self):
        self.__screen.fill(self.BACKGROUND_COLOR)
        self.__board.draw(self.__screen)
        self.__draw_top_bar()

        pygame.display.flip()

    def __draw_top_bar(self):
        self.__update_face()
        self.__face.draw(self.__screen)

        self.__flagCounter.set_value(self.__board.get_flagsLeft())
        self.__flagCounter.update_display()
        self.__flagCounter.draw(self.__screen)

        if self.__board.get_status() == GameState.running:
            time = (pygame.time.get_ticks() - self.__board.get_startTime()) / 1000
            if time > 999:
                time = 999
            self.__timer.set_value(time)
        self.__timer.update_display()
        self.__timer.draw(self.__screen)

    def __update_face(self):
        if self.__board.get_status() == GameState.waiting or self.__board.get_status() == GameState.running:
            self.__face.update_surface(self.__icons['face_happy'])
        elif self.__board.get_status() == GameState.lost:
            self.__face.update_surface(self.__icons['face_death'])
        elif self.__board.get_status() == GameState.won:
            self.__face.update_surface(self.__icons['face_cool'])

    def load_icons(self):
        icons = {}
        for fileName in os.listdir("assets"):
            if not fileName.endswith(".png"):
                continue
            icon = pygame.image.load("assets/" + fileName)
            if not fileName.startswith("timer_"):
                icon = pygame.transform.scale(icon, self.__tileSize)
            elif fileName.startswith("face_"):
                icon = pygame.transform.scale(icon, self.__faceSize)
            else:
                icon = pygame.transform.scale(icon, self.__counterSize)
            icons[fileName.split('.')[0]] = icon
        return icons

    def get_icons(self):
        return self.__icons

    def get_timer(self):
        return self.__timer

    def get_tile_icon(self, tile):
        name = ''
        if self.__board.get_status() == GameState.running or self.__board.get_status() == GameState.waiting:
            if tile.is_clicked():
                name = "mine_boom" if tile.is_bomb() else str(tile.get_bombsAroundNo())
            else:
                name = "flagged_tile" if tile.is_flagged() else "blanc_tile"
        elif self.__board.get_status() == GameState.lost:
            if tile.is_clicked():
                name = "mine_boom" if tile.is_bomb() else str(tile.get_bombsAroundNo())
            elif tile.is_flagged():
                name = "not_mine" if tile.is_flagged() and not tile.is_bomb() else "flagged_tile"
            else:
                name = "mine" if tile.is_bomb() else "blanc_tile"
        elif self.__board.get_status() == GameState.won:
            if tile.is_bomb():
                name = "flagged_tile"
            else:
                name = str(tile.get_bombsAroundNo())
        return self.__icons[name]

    def __process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                break

            if event.type == pygame.MOUSEBUTTONUP:
                self.__board.handle_mouse_up(event.button)
                self.__face.handle_mouse_up(event.button)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.__board.handle_mouse_down(event.button)
            self.__board.check_if_won()


def run():
    pygame.init()
    pygame.display.set_caption("Saper")
    pygame.display.set_icon(load_image('logo.png'))
    pygame.mouse.set_visible(True)
    game = Game(10, 10, 5)
    game.start_game_loop()
    pygame.quit()
