import pygame
import os
from time import sleep


class Game:
    def __init__(self, board, windowSize):
        self.__board = board
        self.__windowSize = windowSize
        self.__tileSize = self.__windowSize[0] // self.__board.get_size()[1], \
                          self.__windowSize[1] // self.__board.get_size()[0]
        self.__window = None
        self.__icons = self.load_icons()

    def run(self):
        pygame.init()
        self.__window = pygame.display.set_mode(self.__windowSize)
        pygame.display.set_caption("Saper")
        pygame.display.set_icon(self.__icons["logo"])
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
        pygame.quit()

    def draw(self):
        leftCorner = (0, 0)
        for row in range(self.__board.get_size()[0]):
            for col in range(self.__board.get_size()[1]):
                tile = self.__board.get_tile((row, col))
                icon = self.get_icon(tile)
                self.__window.blit(icon, leftCorner)
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
