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
    LOGO_SIZE = (25, 25)

    TOP_BAR_HEIGHT = 50
    TOOLBAR_HEIGHT = 50
    MARGIN_SIZE = 25

    LEADERBOARD_ENTRY_LIMIT = 10
    NAME_INPUT_LEN_LIMIT = 10

    BIGGER_FONT_SIZE = 12
    SMALLER_FONT_SIZE = 10
    FONT_COLOR = pygame.Color(255, 0, 0)

    BACKGROUND_COLOR = pygame.Color(150, 150, 150)

    def __init__(self, difficulty):
        self.__difficulty = None
        self.__rows = 10
        self.__cols = 10
        self.__bombs = 5
        self.__set_difficulty(difficulty)

        self.__leaderboardContent = {'BEGINNER': [], 'INTERMEDIATE': [], 'ADVANCED': []}
        self.__optionsOpen = False

        self.__tileSize = self.TILE_EDGE_LEN, self.TILE_EDGE_LEN
        self.__counterSize = self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT
        self.__faceSize = self.FACE_EDGE_LEN, self.FACE_EDGE_LEN

        self.__icons = self.__load_icons()
        self.__biggerFont = load_font('Lato-Black.ttf', self.BIGGER_FONT_SIZE)
        self.__smallerFont = load_font('Lato-Black.ttf', self.SMALLER_FONT_SIZE)

        self.__board = Board((self.__rows, self.__cols), self.__bombs, self.TILE_EDGE_LEN, self)

        self.__screen = None

        self.__face = None
        self.__flagElement = None
        self.__flagCounter = None
        self.__timerElement = None
        self.__timer = None

        self.__leaderboardButton = None
        self.__difficultyButton = None
        self.__difficultyBox = None

        self.__leaderboard = None
        self.__returnInfo = None

        self.__nameInput = None
        self.__timeInfo = None
        self.__bravoInfo = None

        self.__running = None
        self.__mode = WindowMode.game

        self.__init_screen()

    def __init_screen(self):
        boardAreaWidth = self.__cols * self.TILE_EDGE_LEN
        boardAreaHeight = self.__rows * self.TILE_EDGE_LEN
        windowWidth = 2 * self.MARGIN_SIZE + boardAreaWidth
        windowHeight = 2 * self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT + boardAreaHeight

        self.__screen = pygame.display.set_mode((windowWidth, windowHeight))
        self.__screen.fill(self.BACKGROUND_COLOR)

        self.__boardAreaRect = pygame.Rect(self.MARGIN_SIZE,
                                           self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT,
                                           boardAreaWidth, boardAreaHeight)

        self.__board.get_rect().size = (self.__cols * self.TILE_EDGE_LEN, self.__rows * self.TILE_EDGE_LEN)
        self.__board.get_rect().center = self.__boardAreaRect.center

        self.__face = ImageButton(self.__icons["face_happy"], self.__board.reset)
        self.__face.replace_rect(
            pygame.Rect((windowWidth / 2 - self.FACE_EDGE_LEN / 2,
                         self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT / 2 - self.FACE_EDGE_LEN / 2),
                        self.__faceSize))

        self.__init_counters(windowWidth)
        self.__init_toolbar()
        self.__init_leaderboard(windowWidth)
        self.__init_entry()

    def __init_entry(self):
        self.__nameInput = InputFrame(self.__biggerFont, self.FONT_COLOR, "Enter name (max. 10 characters)",
                                      self.NAME_INPUT_LEN_LIMIT, self.__handle_name_entry)
        self.__bravoInfo = Element(
            self.__biggerFont.render("Congratulations, your score is among best!", True, self.FONT_COLOR))

        self.__bravoInfo.get_rect().top = (self.MARGIN_SIZE + 1.4 * self.BIGGER_FONT_SIZE)
        self.__bravoInfo.get_rect().centerx = self.__screen.get_rect().centerx

        self.__nameInput.get_rect().top = (self.__bravoInfo.get_rect().bottom + self.__bravoInfo.get_rect().height)
        self.__nameInput.get_rect().centerx = self.__screen.get_rect().centerx

    def __init_counters(self, windowWidth):
        self.__flagCounter = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__flagCounter.replace_rect(pygame.Rect(
            (self.MARGIN_SIZE + 5,
             self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5),
            (3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)))
        self.__flagCounter.set_value(self.__board.get_flagsLeft())

        self.__timer = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__timer.replace_rect(pygame.Rect(
            (windowWidth - self.MARGIN_SIZE - 3 * self.TIMER_DIG_WIDTH - 5,
             self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5),
            (3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)))

    def __init_leaderboard(self, windowWidth):
        self.__leaderboard = Leaderboard(self.__biggerFont, self.__smallerFont,  self.FONT_COLOR, self.__icons['logo'],
                                         self.LEADERBOARD_ENTRY_LIMIT, windowWidth * 0.95, self.__leaderboardContent)
        self.__leaderboard.get_rect().top = self.MARGIN_SIZE
        self.__leaderboard.get_rect().centerx = self.__screen.get_rect().centerx

        self.__returnInfo = Element(self.__biggerFont.render("Press ESC to continue", True, self.FONT_COLOR))
        self.__returnInfo.get_rect().top = self.__leaderboard.get_rect().bottom + 20
        self.__returnInfo.get_rect().centerx = self.__screen.get_rect().centerx

    def __init_toolbar(self):
        self.__difficultyButton = TextButton(self.__biggerFont, self.FONT_COLOR,
                                             "Difficulty settings", self.__toggle_difficulty_settings)
        self.__difficultyButton.replace_rect(pygame.Rect((self.MARGIN_SIZE + 5,
                                                          self.MARGIN_SIZE - self.BIGGER_FONT_SIZE / 2),
                                                         self.__difficultyButton.get_rect().size))

        self.__leaderboardButton = TextButton(self.__biggerFont, self.FONT_COLOR,
                                              "Leaderboard", self.__show_leaderboard)
        self.__leaderboardButton.replace_rect(
            pygame.Rect((self.MARGIN_SIZE + 5,
                         self.__difficultyButton.get_rect().bottom + self.BIGGER_FONT_SIZE / 2),
                        self.__leaderboardButton.get_rect().size))

        self.__difficultyBox = CheckBoxSelector(
            (self.__difficultyButton.get_rect().right + 1, self.MARGIN_SIZE - self.SMALLER_FONT_SIZE / 2),
            self.__smallerFont, self.FONT_COLOR, ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'], self.change_difficulty,
            self.__difficulty)

    def __reset_game(self):
        self.__board.reset((self.__rows, self.__cols), self.__bombs)

    def __show_leaderboard(self):
        self.__mode = WindowMode.leaderboard

    def __toggle_difficulty_settings(self):
        self.__optionsOpen = not self.__optionsOpen

    def __handle_name_entry(self, name):
        if not name:
            return
        self.__leaderboard.update(self.__difficultyBox.get_selected(), name, self.__timer.get_value())
        self.__show_leaderboard()

    def __draw_all(self):
        self.__screen.fill(self.BACKGROUND_COLOR)

        if self.__mode == WindowMode.leaderboard:
            self.__leaderboard.draw(self.__screen)
            self.__returnInfo.draw(self.__screen)
            pygame.display.flip()
            return

        elif self.__mode == WindowMode.entry:
            self.__timeInfo.draw(self.__screen)
            self.__bravoInfo.draw(self.__screen)
            self.__nameInput.draw(self.__screen)
            pygame.display.flip()
            return

        self.__board.draw(self.__screen)
        self.__draw_top_bar()
        self.__draw_toolbar()

        pygame.display.flip()

    def __draw_toolbar(self):
        self.__leaderboardButton.draw(self.__screen)
        self.__difficultyButton.draw(self.__screen)
        if self.__optionsOpen:
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
            elif fileName.startswith('logo'):
                icon = pygame.transform.smoothscale(icon, self.LOGO_SIZE)
            else:
                icon = pygame.transform.scale(icon, self.__tileSize)
            icons[fileName.split('.')[0]] = icon
        return icons

    def __process_events(self):
        if self.__mode == WindowMode.leaderboard:
            self.__process_events_leaderboard()
        elif self.__mode == WindowMode.entry:
            self.__process_events_entry()
        else:
            self.__process_events_game()

    def __process_events_entry(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                break

            elif event.type == pygame.KEYDOWN:
                self.__nameInput.handle_key_down(event)

    def __process_events_leaderboard(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__mode = WindowMode.game

    def __process_events_game(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                break

            if event.type == pygame.MOUSEBUTTONUP:
                self.__board.handle_mouse_up(event.button)
                self.__face.handle_mouse_up(event.button)
                self.__leaderboardButton.handle_mouse_up(event.button)
                self.__difficultyButton.handle_mouse_up(event.button)
                if self.__optionsOpen:
                    self.__difficultyBox.handle_mouse_up(event.button)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.__board.handle_mouse_down(event.button)

    def __set_difficulty(self, difficulty):
        self.__difficulty = difficulty
        if difficulty == "BEGINNER":
            self.__rows = 9
            self.__cols = 9
            self.__bombs = 10
        elif difficulty == 'INTERMEDIATE':
            self.__rows = 16
            self.__cols = 16
            self.__bombs = 40
        elif difficulty == 'ADVANCED':
            self.__rows = 16
            self.__cols = 30
            self.__bombs = 99

    def handle_victory(self):
        if self.__leaderboard.needs_update(self.__difficultyBox.get_selected(), self.__timer.get_value()):
            self.__timeInfo = Element(
                self.__biggerFont.render("You've achieved victory in {} seconds".format(self.__timer.get_value()), True,
                                         self.FONT_COLOR))
            self.__timeInfo.get_rect().top = self.MARGIN_SIZE
            self.__timeInfo.get_rect().centerx = self.__screen.get_rect().centerx
            self.__nameInput.reset_input()

            self.__mode = WindowMode.entry

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
    game = Game("BEGINNER")
    game.start_game_loop()
    pygame.quit()


if __name__ == '__main__':
    run()
