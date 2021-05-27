import os
from time import sleep
from board import Board
from utilities import load_image, load_font
from ui import *
from state import *


class Game:
    TILE_EDGE_LEN = 30
    FACE_EDGE_LEN = 35
    TIMER_DIG_HEIGHT = 40
    TIMER_DIG_WIDTH = 20
    TOP_BAR_HEIGHT = 50
    BOTTOM_BAR_HEIGHT = 40
    MARGIN_SIZE = 20
    FONT_SIZE = 10
    FONT_COLOR = pygame.Color(255, 0, 0)
    BACKGROUND_COLOR = pygame.Color(150, 150, 150)

    def __init__(self, difficulty):
        self.__difficulty = None
        self.__rows = 10
        self.__cols = 10
        self.__bombs = 5
        self.__set_difficulty(difficulty)

        self.__tileSize = self.TILE_EDGE_LEN, self.TILE_EDGE_LEN
        self.__counterSize = self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT
        self.__faceSize = self.FACE_EDGE_LEN, self.FACE_EDGE_LEN

        self.__icons = self.__load_icons()
        self.__font = load_font('Lato-Black.ttf', self.FONT_SIZE)

        self.__board = Board((self.__rows, self.__cols), self.__bombs, self.TILE_EDGE_LEN, self)

        self.__screen = None
        self.__screenRect = None
        self.__boardRect = None

        self.__face = None
        self.__flagElement = None
        self.__flagCounter = None
        self.__timerElement = None
        self.__timer = None

        self.__difficultyBox = None

        self.__init_screen()

        self.__running = None
        self.__mode = WindowState.game

    def __init_screen(self):
        boardAreaWidth = self.__cols * self.TILE_EDGE_LEN
        boardAreaHeight = self.__rows * self.TILE_EDGE_LEN
        window_width = 2 * self.MARGIN_SIZE + boardAreaWidth
        window_height = 2 * self.MARGIN_SIZE + self.TOP_BAR_HEIGHT + self.BOTTOM_BAR_HEIGHT + boardAreaHeight

        self.__boardAreaRect = pygame.Rect(self.MARGIN_SIZE, self.MARGIN_SIZE + self.TOP_BAR_HEIGHT,
                                           boardAreaWidth, boardAreaHeight)

        self.__board.get_rect().size = (self.__cols * self.TILE_EDGE_LEN, self.__rows * self.TILE_EDGE_LEN)
        self.__board.get_rect().center = self.__boardAreaRect.center

        self.__face = ImageButton(self.__icons["face_happy"], self.__board.reset)
        self.__face.replace_rect(pygame.Rect((window_width / 2 - self.FACE_EDGE_LEN / 2,
                                              self.MARGIN_SIZE + self.TOP_BAR_HEIGHT / 2 - self.FACE_EDGE_LEN / 2),
                                             self.__faceSize))

        self.__flagCounter = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__flagCounter.replace_rect(pygame.Rect(
            (self.MARGIN_SIZE + 5, self.MARGIN_SIZE + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5),
            (3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)))
        self.__flagCounter.set_value(self.__board.get_flagsLeft())

        self.__timer = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__timer.replace_rect(pygame.Rect(
            (window_width - self.MARGIN_SIZE - 3 * self.TIMER_DIG_WIDTH - 5,
             self.MARGIN_SIZE + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5),
            (3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)))

        self.__difficultyBox = CheckBoxSelector((self.MARGIN_SIZE + 5, window_height - self.BOTTOM_BAR_HEIGHT - self.FONT_SIZE), self.__font, self.FONT_COLOR, ['Beginner', 'Intermediate', 'Advanced'], self.change_difficulty, self.__difficulty)

        self.__screen = pygame.display.set_mode((window_width, window_height))
        self.__screenRect = self.__screen.get_rect()
        self.__screen.fill(self.BACKGROUND_COLOR)

    def __reset_game(self):
        self.__board.reset((self.__rows, self.__cols), self.__bombs)

    def __draw_all(self):
        self.__screen.fill(self.BACKGROUND_COLOR)
        self.__board.draw(self.__screen)
        self.__draw_top_bar()
        self.__draw_bottom_bar()

        pygame.display.flip()

    def __draw_bottom_bar(self):
        self.__difficultyBox.draw(self.__screen)

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

    def __load_icons(self):
        icons = {}
        for fileName in os.listdir("assets"):
            if not fileName.endswith(".png"):
                continue
            icon = pygame.image.load("assets/" + fileName)
            if fileName.startswith("timer_"):
                icon = pygame.transform.smoothscale(icon, self.__counterSize)
            elif fileName.startswith("face_"):
                icon = pygame.transform.smoothscale(icon, self.__faceSize)
            else:
                icon = pygame.transform.scale(icon, self.__tileSize)
            icons[fileName.split('.')[0]] = icon
        return icons

    def __process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                break

            if event.type == pygame.MOUSEBUTTONUP:
                self.__board.handle_mouse_up(event.button)
                self.__face.handle_mouse_up(event.button)
                self.__difficultyBox.handle_mouse_up(event.button)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.__board.handle_mouse_down(event.button)
            self.__board.check_if_won()

    def __set_difficulty(self, difficulty):
        self.__difficulty = difficulty
        if difficulty == "Beginner":
            self.__rows = 9
            self.__cols = 9
            self.__bombs = 10
        elif difficulty == 'Intermediate':
            self.__rows = 16
            self.__cols = 16
            self.__bombs = 40
        elif difficulty == 'Advanced':
            self.__rows = 16
            self.__cols = 30
            self.__bombs = 99

    def change_difficulty(self, difficulty):
        self.__set_difficulty(difficulty)
        self.__init_screen()
        self.__reset_game()

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


def run():
    pygame.init()
    pygame.display.set_caption("Saper")
    pygame.display.set_icon(load_image('logo.png'))
    pygame.mouse.set_visible(True)
    game = Game("Beginner")
    game.start_game_loop()
    pygame.quit()


if __name__ == '__main__':
    run()
