import pygame
from utilities import draw_frame, draw_checked_box


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
        if button != 1:  # LMB
            return

        if self._rect.collidepoint(*pygame.mouse.get_pos()):
            self.__action()


class CheckBoxSelector(Element):
    def __init__(self, pos, font, fontColor, options, action, initialValue):
        boxEdgeLen = font.get_height()
        self.__uncheckedBox = draw_frame(boxEdgeLen, boxEdgeLen, fontColor)
        self.__checkedBox = draw_checked_box(boxEdgeLen, fontColor)
        self.__options = options
        self.__action = action
        self.__selected = 0
        for i, option in enumerate(self.__options):
            if option == initialValue:
                self.__selected = i
                break

        optionNames = [font.render(option, True, fontColor) for option in options]
        namesWidths = [2 * boxEdgeLen + name.get_width() for name in optionNames]
        width = sum(namesWidths)
        height = boxEdgeLen

        super().__init__(pygame.Surface((width, height), pygame.SRCALPHA))
        self._rect = pygame.Rect(pos, (width, height))

        self.__boxesRects = []
        self.__namesRects = []
        optionRects = []
        x = 0

        for optionName, nameWidth in zip(optionNames, namesWidths):
            boxRect = self.__uncheckedBox.get_rect(x=x)
            optionRect = optionName.get_rect(x=boxRect.right + 0.5 * boxRect.width, centery=boxRect.centery)
            nameRect = pygame.Rect(x, 0, nameWidth, boxEdgeLen)
            self.__boxesRects.append(boxRect)
            self.__namesRects.append(nameRect)
            optionRects.append(optionRect)
            x = nameRect.right

        self.__checkBoxesSurface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.__checkBoxesSurface.fill((0, 0, 0))
        for optionRect, optionName in zip(optionRects, optionNames):
            self.__checkBoxesSurface.blit(optionName, optionRect)
        self.__update_display()

    def __update_display(self):
        self._surface.fill((0, 0, 0))
        self._surface.blit(self.__checkBoxesSurface, (0, 0))
        for i, rect in enumerate(self.__boxesRects):
            if i == self.__selected:
                self._surface.blit(self.__checkedBox, rect)
            else:
                self._surface.blit(self.__uncheckedBox, rect)

    def handle_mouse_up(self, button):
        if button != 1:  # LMB
            return

        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0] - self._rect.left
        y = mouse_pos[1] - self._rect.top
        previous = self.__selected
        for i, (button_rect, item_rect) in enumerate(zip(self.__boxesRects, self.__namesRects)):
            if item_rect.collidepoint(x, y):
                if i != self.__selected:
                    self.__action(self.__options[i])
                self.__selected = i
                break

        if self.__selected != previous:
            self.__update_display()

    def get_selected(self):
        return self.__options[self.__selected]
