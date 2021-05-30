import json
import os
from time import sleep
from board import Board
from utilities import unload_game_data, load_sounds
from ui import *
from state import *


class Game:
    TILE_EDGE_LEN = 30
    FACE_EDGE_LEN = 35
    TIMER_DIG_HEIGHT = 40
    TIMER_DIG_WIDTH = 20
    SOUND_BUTTON_EDGE_LEN = 35
    LOGO_SIZE = (25, 25)
    WARNING_ICON_SIZE = (40, 40)

    TOP_BAR_HEIGHT = 50
    TOOLBAR_HEIGHT = 50
    MARGIN_SIZE = 25

    LEADERBOARD_ENTRY_LIMIT = 10
    NAME_INPUT_LEN_LIMIT = 10
    NAME_INPUT_DELAY = 1

    BIGGER_FONT_SIZE = 12
    SMALLER_FONT_SIZE = 9
    FONT_COLOR = pygame.Color(255, 0, 0)
    ON_BACKGROUND_TEXT_COLOR = pygame.Color(255, 255, 255)

    BACKGROUND_COLOR = pygame.Color(150, 150, 150)

    FRAME_RATE = 30

    DATAFILE_PATH = 'assets/gameData.json'

    def __init__(self):
        self.__difficulty = 'BEGINNER'
        self.__rows = 10
        self.__cols = 10
        self.__bombs = 5
        self.__set_difficulty(self.__difficulty)

        self.__leaderboardContent = {'BEGINNER': [], 'INTERMEDIATE': [], 'ADVANCED': []}
        self.__optionsOpen = False
        self.__soundOn = True

        data = unload_game_data(self.DATAFILE_PATH)
        self.__read_data(data)

        self.__tileSize = self.TILE_EDGE_LEN, self.TILE_EDGE_LEN
        self.__counterSize = self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT
        self.__faceSize = self.FACE_EDGE_LEN, self.FACE_EDGE_LEN
        self.__soundButtonSize = self.SOUND_BUTTON_EDGE_LEN, self.SOUND_BUTTON_EDGE_LEN

        self.__icons = self.__load_icons()
        self.__biggerFont = pygame.font.Font('assets/Lato-Black.ttf', self.BIGGER_FONT_SIZE)
        self.__smallerFont = pygame.font.Font('assets/Lato-Black.ttf', self.SMALLER_FONT_SIZE)

        self.__sounds = load_sounds()

        self.__board = Board((self.__rows, self.__cols), self.__bombs, self.TILE_EDGE_LEN, self)

        self.__screen = None
        self.__backgroundPicture = None

        self.__face = None
        self.__flagElement = None
        self.__flagCounter = None
        self.__timerElement = None
        self.__timer = None

        self.__leaderboardButton = None
        self.__difficultyButton = None
        self.__difficultyBox = None
        self.__soundButton = None

        self.__leaderboard = None
        self.__returnButton = None
        self.__clearButton = None

        self.__warningPopup = None
        self.__confirmButton = None
        self.__abortButton = None

        self.__nameInput = None
        self.__timeInfo = None
        self.__bravoInfo = None

        self.__running = None
        self.__mode = WindowMode.game

        self.__init_screen()

    def __read_data(self, data):
        if 'LEADERS' in data:
            self.__leaderboardContent = data["LEADERS"]
        if 'OPTIONS' in data:
            self.__optionsOpen = data['OPTIONS']
        if 'SOUND' in data:
            self.__soundOn = data['SOUND']
        if 'DIFFICULTY' in data:
            self.__set_difficulty(data['DIFFICULTY'])

    def __init_screen(self):
        boardAreaWidth = self.__cols * self.TILE_EDGE_LEN
        boardAreaHeight = self.__rows * self.TILE_EDGE_LEN
        windowWidth = 2 * self.MARGIN_SIZE + boardAreaWidth
        windowHeight = 2 * self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT + boardAreaHeight

        self.__screen = pygame.display.set_mode((windowWidth, windowHeight))

        self.__backgroundPicture = pygame.image.load('assets/background.jpg')
        self.__backgroundPicture = pygame.transform.smoothscale(self.__backgroundPicture, (windowWidth, windowHeight))

        self.__boardAreaRect = pygame.Rect(self.MARGIN_SIZE,
                                           self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT,
                                           boardAreaWidth, boardAreaHeight)

        self.__board.get_rect().size = (self.__cols * self.TILE_EDGE_LEN, self.__rows * self.TILE_EDGE_LEN)
        self.__board.get_rect().center = self.__boardAreaRect.center

        self.__face = ImageButton(self.__icons["face_happy"], self.__board.reset, self)
        self.__face.get_rect().centerx = self.__screen.get_rect().centerx
        self.__face.get_rect().centery = self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT / 2

        self.__init_counters(windowWidth)
        self.__init_toolbar(windowWidth)
        self.__init_leaderboard(windowWidth)
        self.__init_entry()
        self.__init_delete_data_screen()

    def __init_delete_data_screen(self):
        self.__abortButton = TextButton(self.__biggerFont, self.FONT_COLOR, "No", self.__show_leaderboard, self)
        self.__confirmButton = TextButton(self.__biggerFont, self.FONT_COLOR, "Yes", self.__delete_leaderboard_data,
                                          self)
        self.__warningPopup = Popup(self.__biggerFont, self.FONT_COLOR, self.BACKGROUND_COLOR,
                                    "All leaderboard entries will be deleted!\nDo you want to proceed?",
                                    self.__icons['warning'], self.__confirmButton, self.__abortButton)
        self.__warningPopup.get_rect().center = self.__screen.get_rect().center
        self.__abortButton.get_rect().left = self.__screen.get_rect().centerx + 45
        self.__abortButton.get_rect().top = self.__screen.get_rect().centery + self.BIGGER_FONT_SIZE
        self.__confirmButton.get_rect().left = self.__screen.get_rect().centerx - 15
        self.__confirmButton.get_rect().top = self.__screen.get_rect().centery + self.BIGGER_FONT_SIZE

    def __init_entry(self):
        self.__nameInput = InputFrame(self.__biggerFont, self.FONT_COLOR, self.BACKGROUND_COLOR,
                                      "Enter name (max. 10 characters)",
                                      self.NAME_INPUT_LEN_LIMIT, self.__handle_name_entry)
        self.__bravoInfo = Element(
            self.__biggerFont.render("Congratulations, your score is among best!", True, self.ON_BACKGROUND_TEXT_COLOR))

        self.__bravoInfo.get_rect().top = (self.MARGIN_SIZE + 1.4 * self.BIGGER_FONT_SIZE)
        self.__bravoInfo.get_rect().centerx = self.__screen.get_rect().centerx

        self.__nameInput.get_rect().top = (self.__bravoInfo.get_rect().bottom + self.__bravoInfo.get_rect().height)
        self.__nameInput.get_rect().centerx = self.__screen.get_rect().centerx

    def __init_counters(self, windowWidth):
        self.__flagCounter = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__flagCounter.get_rect().left = self.MARGIN_SIZE + 5
        self.__flagCounter.get_rect().top = \
            self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5
        self.__flagCounter.set_value(self.__board.get_flagsLeft())

        self.__timer = Counter(pygame.Surface((3 * self.TIMER_DIG_WIDTH, self.TIMER_DIG_HEIGHT)), [0, 0, 0], self)
        self.__timer.get_rect().left = windowWidth - self.MARGIN_SIZE - 3 * self.TIMER_DIG_WIDTH - 5
        self.__timer.get_rect().top = \
            self.MARGIN_SIZE + self.TOOLBAR_HEIGHT + self.TOP_BAR_HEIGHT / 2 - self.TIMER_DIG_HEIGHT / 2 - 5

    def __init_leaderboard(self, windowWidth):
        self.__leaderboard = Leaderboard(self.__biggerFont, self.__smallerFont,
                                         self.FONT_COLOR, self.BACKGROUND_COLOR, self.__icons['logo'],
                                         self.LEADERBOARD_ENTRY_LIMIT, windowWidth * 0.95,
                                         self.__leaderboardContent)
        self.__leaderboard.get_rect().top = self.MARGIN_SIZE
        self.__leaderboard.get_rect().centerx = self.__screen.get_rect().centerx

        self.__returnButton = TextButton(self.__biggerFont, self.FONT_COLOR, "Press to continue",
                                         self.__return_to_game, self)
        self.__returnButton.get_rect().top = self.__leaderboard.get_rect().bottom + 20
        self.__returnButton.get_rect().right = self.__screen.get_rect().centerx - 10

        self.__clearButton = TextButton(self.__biggerFont, self.FONT_COLOR, "Clear leaderboard",
                                        self.__warn_before_deleting_data, self)
        self.__clearButton.get_rect().top = self.__leaderboard.get_rect().bottom + 20
        self.__clearButton.get_rect().left = self.__screen.get_rect().centerx + 10

    def __init_toolbar(self, windowWidth):
        self.__difficultyButton = TextButton(self.__biggerFont, self.FONT_COLOR,
                                             "Difficulty settings", self.__toggle_difficulty_settings, self)
        self.__difficultyButton.get_rect().left = self.MARGIN_SIZE + 5
        self.__difficultyButton.get_rect().top = self.MARGIN_SIZE - self.BIGGER_FONT_SIZE / 2

        self.__leaderboardButton = TextButton(self.__biggerFont, self.FONT_COLOR,
                                              "Leaderboard", self.__show_leaderboard, self)
        self.__leaderboardButton.get_rect().left = self.MARGIN_SIZE + 5
        self.__leaderboardButton.get_rect().top = self.__difficultyButton.get_rect().bottom + self.BIGGER_FONT_SIZE / 2

        self.__difficultyBox = CheckBoxSelector(
            (self.__difficultyButton.get_rect().right + 1, self.MARGIN_SIZE - self.BIGGER_FONT_SIZE / 2),
            self.__smallerFont, self.FONT_COLOR, ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'], self.change_difficulty,
            self.__difficulty)

        self.__soundButton = ImageButton(self.__icons['sound_on'] if self.__soundOn else self.__icons['sound_off'],
                                         self.__toggle_sound, self)
        self.__soundButton.get_rect().right = windowWidth - self.MARGIN_SIZE - 10
        self.__soundButton.get_rect().top = self.MARGIN_SIZE + 2

    def __reset_game(self):
        self.__board.reset((self.__rows, self.__cols), self.__bombs)

    def __show_leaderboard(self):
        self.__mode = WindowMode.leaderboard

    def __warn_before_deleting_data(self):
        entryCount = 0
        for key in self.__leaderboard.get_data().keys():
            entryCount += len(self.__leaderboard.get_data()[key])
        if entryCount > 0:
            self.__mode = WindowMode.delete

    def __delete_leaderboard_data(self):
        if self.__soundOn:
            self.__sounds['sound_cutting'].play()

        self.__leaderboardContent = {'BEGINNER': [], 'INTERMEDIATE': [], 'ADVANCED': []}
        self.__leaderboard.set_data({'BEGINNER': [], 'INTERMEDIATE': [], 'ADVANCED': []})
        self.__leaderboard.fill_lanes()
        self.__show_leaderboard()

    def __return_to_game(self):
        self.__mode = WindowMode.game

    def __toggle_difficulty_settings(self):
        self.__optionsOpen = not self.__optionsOpen

    def __toggle_sound(self):
        self.__soundOn = not self.__soundOn
        self.__update_sound_button()

    def __update_sound_button(self):
        if self.__soundOn:
            self.__soundButton.update_surface(self.__icons['sound_on'])
        else:
            self.__soundButton.update_surface(self.__icons['sound_off'])

    def __handle_name_entry(self, name):
        if not name:
            return
        self.__leaderboard.update(self.__difficultyBox.get_selected(), name, self.__timer.get_value())
        self.__show_leaderboard()

    def __draw_all(self):
        self.__screen.blit(self.__backgroundPicture, self.__screen.get_rect())

        if self.__mode == WindowMode.leaderboard:
            self.__leaderboard.draw(self.__screen)
            self.__returnButton.draw(self.__screen)
            self.__clearButton.draw(self.__screen)
            pygame.display.flip()
            return

        elif self.__mode == WindowMode.entry:
            self.__timeInfo.draw(self.__screen)
            self.__bravoInfo.draw(self.__screen)
            self.__nameInput.draw(self.__screen)
            pygame.display.flip()
            return

        elif self.__mode == WindowMode.delete:
            self.__warningPopup.draw(self.__screen)
            self.__confirmButton.draw(self.__screen)
            self.__abortButton.draw(self.__screen)
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
        self.__soundButton.draw(self.__screen)

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
            elif fileName.startswith("sound_"):
                icon = pygame.transform.smoothscale(icon, self.__soundButtonSize)
            elif fileName.startswith("warning"):
                icon = pygame.transform.smoothscale(icon, self.WARNING_ICON_SIZE)
            else:
                icon = pygame.transform.scale(icon, self.__tileSize)
            icons[fileName.split('.')[0]] = icon
        return icons

    def __process_events(self):
        if self.__mode == WindowMode.leaderboard:
            self.__process_events_leaderboard()
        elif self.__mode == WindowMode.entry:
            self.__process_events_entry()
        elif self.__mode == WindowMode.delete:
            self.__process_events_delete_data()
        else:
            self.__process_events_game()

    def __process_events_delete_data(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__mode = WindowMode.leaderboard
                elif event.key == pygame.K_RETURN:
                    self.__delete_leaderboard_data()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.__warningPopup.handle_mouse_up(event.button)

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

            elif event.type == pygame.MOUSEBUTTONUP:
                self.__returnButton.handle_mouse_up(event.button)
                self.__clearButton.handle_mouse_up(event.button)

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
                self.__soundButton.handle_mouse_up(event.button)

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
        if self.__soundOn:
            self.__sounds['sound_win'].play()
        if self.__leaderboard.needs_update(self.__difficultyBox.get_selected(), self.__timer.get_value()):
            self.__timeInfo = Element(
                self.__biggerFont.render("You've achieved victory in {} seconds".format(self.__timer.get_value()), True,
                                         self.ON_BACKGROUND_TEXT_COLOR))
            self.__timeInfo.get_rect().top = self.MARGIN_SIZE
            self.__timeInfo.get_rect().centerx = self.__screen.get_rect().centerx
            self.__nameInput.reset_input()

            sleep(self.NAME_INPUT_DELAY)
            self.__mode = WindowMode.entry

    def change_difficulty(self, difficulty):
        self.__set_difficulty(difficulty)
        self.__init_screen()
        self.__reset_game()

    def start_game_loop(self):
        clock = pygame.time.Clock()
        self.__running = True
        while self.__running:
            clock.tick(self.FRAME_RATE)
            self.__process_events()
            self.__draw_all()

    def get_icons(self):
        return self.__icons

    def get_sounds(self):
        return self.__sounds

    def get_timer(self):
        return self.__timer

    def is_sound_on(self):
        return self.__soundOn

    def get_tile_icon(self, tile):
        name = ''
        if self.__board.get_status() == GameState.running or self.__board.get_status() == GameState.waiting:
            if tile.is_clicked():
                name = "mine_boom" if tile.is_mine() else str(tile.get_minesAroundNo())
            else:
                name = "flagged_tile" if tile.is_flagged() else "blanc_tile"
        elif self.__board.get_status() == GameState.lost:
            if tile.is_clicked():
                name = "mine_boom" if tile.is_mine() else str(tile.get_minesAroundNo())
            elif tile.is_flagged():
                name = "not_mine" if tile.is_flagged() and not tile.is_mine() else "flagged_tile"
            else:
                name = "mine" if tile.is_mine() else "blanc_tile"
        elif self.__board.get_status() == GameState.won:
            if tile.is_mine():
                name = "flagged_tile"
            else:
                name = str(tile.get_minesAroundNo())
        return self.__icons[name]

    def save_data(self, dataFilePath):
        state = {
            "DIFFICULTY": self.__difficultyBox.get_selected(),
            "OPTIONS": self.__optionsOpen,
            "SOUND": self.__soundOn,
            "LEADERS": self.__leaderboard.get_data()
        }
        with open(dataFilePath, "w") as file:
            json.dump(state, file)


def run():
    try:
        pygame.init()
        pygame.display.set_caption("Minesweeper")
        pygame.display.set_icon(pygame.image.load('assets/logo.png'))
        pygame.mouse.set_visible(True)
        game = Game()
        game.start_game_loop()
        game.save_data(game.DATAFILE_PATH)
    except pygame.error as err:
        print(f"An error occurred: {err.args}")
    finally:
        pygame.quit()


if __name__ == '__main__':
    run()
