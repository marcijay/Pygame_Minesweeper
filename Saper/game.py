import pygame
import os


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
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def draw(self):
        leftCorner = (0, 0)
        for row in range(self.__board.get_size()[0]):
            for col in range(self.__board.get_size()[1]):
                temp = self.__icons['logo']
                self.__window.blit(temp, leftCorner)
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
