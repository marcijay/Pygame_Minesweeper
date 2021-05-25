import pygame


class Element:
    def __init__(self, surface, rect):
        self._surface = surface
        self._rect = rect

    def update_surface(self, newSurface):
        self._surface = newSurface

    def draw(self, other_surface):
        other_surface.blit(self._surface, self._rect)


class ImageButton(Element):
    def __init__(self, surface, rect, action):
        super().__init__(surface, rect)
        self.__action = action

    def handle_mouse_up(self, button):
        if button != 1:
            return

        if self._rect.collidepoint(*pygame.mouse.get_pos()):
            self.__action()
