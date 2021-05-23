import pygame
import os
from time import sleep
from board import Board

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
    TILE_EDGE_LEN = 20
    TOP_BAR_HEIGHT = 50
    MARGIN_SIZE = 20
    MAX_BOARD_SIZE = 50
    MIN_BOARD_SIZE = 10
    BACKGROUND_COLOR = pygame.Color(180, 180, 180)

    def __init__(self, rows, cols, bombs):
        display_info = pygame.display.Info()
        self.__max_cols = (int(0.95 * display_info.current_w) - 3 * self.MARGIN_SIZE) // self.TILE_EDGE_LEN
        self.__max_rows = (int(0.95 * display_info.current_h) - 3 * self.MARGIN_SIZE) // self.TILE_EDGE_LEN
        self.__rows = rows
        self.__cols = cols
        self.__bombs = bombs

        tile_nums_icons = []
        for i in range(0, 9):
            tile_nums_icons.append(load_image('{}.png'.format(str(i)), self.TILE_EDGE_LEN))
        blanc_tile_icon = load_image('blanc_tile.png', self.TILE_EDGE_LEN)
        mine_icon = load_image('mine.png', self.TILE_EDGE_LEN)
        boom_icon = load_image('mine_boom.png', self.TILE_EDGE_LEN)
        flagged_tile_icon = load_image('flagged_tile.png', self.TILE_EDGE_LEN)

        self.__board = Board((self.__rows, self.__cols), self.__bombs, self.TILE_EDGE_LEN)
        self.__screen = None
        self.__screen_Rect = None
        self.__board_Rect = None
        self.__top_bar_Rect = None
        self.__board_area_Rect = None
        self.__init_screen()

        self.__tileSize = self.TILE_EDGE_LEN, self.TILE_EDGE_LEN
        self.__icons = self.load_icons()

    def __init_screen(self):
        board_area_width = max(self.__cols, self.MIN_BOARD_SIZE) * self.TILE_EDGE_LEN
        board_area_height = max(self.__rows, self.MIN_BOARD_SIZE) * self.TILE_EDGE_LEN
        window_width = 3 * self.MARGIN_SIZE + board_area_width
        window_height = 3 * self.MARGIN_SIZE + self.TOP_BAR_HEIGHT + board_area_height

        self.__board_area_Rect = pygame.Rect(2 * self.MARGIN_SIZE, 2 * self.MARGIN_SIZE + self.TOP_BAR_HEIGHT,
                                             board_area_width, board_area_height)

        self.__board.rect.size = (self.__cols * self.TILE_EDGE_LEN, self.__rows * self.TILE_EDGE_LEN)
        self.__board.rect.center = self.__board_area_Rect.center

        self.__top_bar_Rect = pygame.Rect(2 * self.MARGIN_SIZE, self.MARGIN_SIZE, board_area_width, self.TOP_BAR_HEIGHT)

        self.__screen = pygame.display.set_mode((window_width, window_height))
        self.__screen_Rect = self.__screen.get_rect()
        self.__screen.fill(self.BACKGROUND_COLOR)

    def start_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
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
                running = False

    def draw(self):
        leftCorner = (0, 0)
        for row in range(self.__board.get_size()[0]):
            for col in range(self.__board.get_size()[1]):
                tile = self.__board.get_tile((row, col))
                icon = self.get_icon(tile)
                self.__screen.blit(icon, leftCorner)
                leftCorner = leftCorner[0] + self.__tileSize[0], leftCorner[1]
            leftCorner = 0, leftCorner[1] + self.__tileSize[1]

    def load_icons(self):
        icons = {}
        for fileName in os.listdir("assets"):
            if not fileName.endswith(".png"):
                continue
            icon = pygame.image.load("assets/" + fileName)
            icon = pygame.transform.scale(icon, self.__tileSize)
            icons[fileName.split('.')[0]] = icon
        return icons

    def get_icon(self, tile):
        if tile.is_clicked():
            name = "mine_boom" if tile.is_bomb() else str(tile.get_bombsAroundNo())
        else:
            name = "flagged_tile" if tile.is_flagged() else "blanc_tile"
        return self.__icons[name]

    def handle_click(self, position, isRMB):
        if self.__board.get_lost():
            return
        index = position[1] // self.__tileSize[1], position[0] // self.__tileSize[0]
        tile = self.__board.get_tile(index)
        self.__board.handle_click(tile, isRMB)


def run():
    pygame.init()
    pygame.display.set_caption("Saper")
    pygame.display.set_icon(load_image('logo.png'))
    pygame.mouse.set_visible(True)
    game = Game(10, 10, 5)
    game.start_loop()
    pygame.quit()
