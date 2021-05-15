import pygame


class Game:
    def __init__(self, board, windowSize):
        self.board = board
        self.windowSize = windowSize

    def run(self):
        pygame.init()
        window = pygame.display.set_mode(self.windowSize)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            pygame.display.flip()
        pygame.quit()
