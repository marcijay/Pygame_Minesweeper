import pygame


class Element:
    def __init__(self, surface):
        self._surface = surface
        self._rect = surface.get_rect()

    def update_surface(self, newSurface):
        self._surface = newSurface

    def replace_rect(self, newRect):
        self._rect = newRect

    def draw(self, other_surface):
        other_surface.blit(self._surface, self._rect)


class Counter(Element):
    def __init__(self, surface, values, owner):
        super().__init__(surface)
        self.__values = values
        self.__owner = owner

    def update_display(self):
        for i, number in enumerate(self.__values):
            self._surface.blit(self.__owner.get_icons()['timer_{}'.format(str(number))],
                               (0 + (self.__owner.TIMER_DIG_WIDTH * i), 0))

    def increment(self):
        if self.__values[2] < 9:
            self.__values[2] += 1
        elif self.__values[1] < 9:
            self.__values[1] += 1
            self.__values[2] = 0
        elif self.__values[0] < 9:
            self.__values[0] += 1
            self.__values[1] = 0
            self.__values[2] = 0

    def decrement(self):
        if self.__values[2] > 0:
            self.__values[2] -= 1
        elif self.__values[1] > 0:
            self.__values[1] -= 1
            self.__values[2] = 9
        elif self.__values[0] > 0:
            self.__values[0] -= 1
            self.__values[1] = 9
            self.__values[2] = 9

    def get_value(self):
        total_val = self.__values[0] * 100
        total_val += self.__values[1] * 10
        total_val += self.__values[2]
        return total_val

    def set_value(self, aim):
        while aim > self.get_value():
            self.increment()
        while self.get_value() > aim:
            self.decrement()


class ImageButton(Element):
    def __init__(self, surface, action):
        super().__init__(surface)
        self.__action = action

    def handle_mouse_up(self, button):
        if button != 1:
            return

        if self._rect.collidepoint(*pygame.mouse.get_pos()):
            self.__action()
