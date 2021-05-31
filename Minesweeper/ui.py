import pygame
from utilities import draw_frame, draw_checked_box, check_entry_key


class Element:
    """Base class to represent graphical element, contains surface and rectangle"""
    def __init__(self, surface):
        self._surface = surface
        self._rect = surface.get_rect()

    def update_surface(self, newSurface):
        self._surface = newSurface

    def get_rect(self):
        return self._rect

    def draw(self, otherSurface):
        otherSurface.blit(self._surface, self._rect)


class Counter(Element):
    """Class to  represent counter"""
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
        value = self.__values[0] * 100
        value += self.__values[1] * 10
        value += self.__values[2]
        return value

    def set_value(self, aim):
        while aim > self.get_value():
            self.increment()
        while self.get_value() > aim:
            self.decrement()


class ImageButton(Element):
    """Class to implement button witch image covering surface"""
    def __init__(self, surface, action, owner):
        self.__action = action
        self.__owner = owner
        super().__init__(surface)

    def handle_mouse_up(self, button):
        """Handles event of mouse button being pressed down"""
        if button != 1:  # LMB
            return

        if self._rect.collidepoint(*pygame.mouse.get_pos()):
            if self.__owner.is_sound_on():
                self.__owner.get_sounds()['sound_button'].play()
            self.__action()


class TextButton(Element):
    """Class to implement button witch given text in frame covering surface"""
    def __init__(self, font, color, text, action, owner):
        self.__action = action
        self.__owner = owner
        text = font.render(text, True, color)
        margin = 1.5 * font.size("_")[0]
        surface = draw_frame(text.get_width() + margin, 1.2 * text.get_height(), color, pygame.Color(0, 0, 0))

        super().__init__(surface)

        rect = text.get_rect(center=self._rect.center)
        self._surface.blit(text, rect)

    def handle_mouse_up(self, button):
        """Handles event of mouse button being pressed down"""
        if button != 1:  # LMB
            return

        if self._rect.collidepoint(*pygame.mouse.get_pos()):
            if self.__owner.is_sound_on():
                self.__owner.get_sounds()['sound_button'].play()
            self.__action()


class CheckBoxSelector(Element):
    """Class to implement selector allowing to select one option from all available"""
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
        namesWidths = [1.5 * boxEdgeLen + name.get_width() for name in optionNames]
        width = max(namesWidths)
        height = boxEdgeLen * (2 * len(optionNames) - 2)

        super().__init__(pygame.Surface((width, height), pygame.SRCALPHA))
        self._rect = pygame.Rect(pos, (width, height))

        self.__boxesRects = []
        self.__namesRects = []
        optionRects = []
        y = 0
        for optionName, nameWidth in zip(optionNames, namesWidths):
            boxRect = self.__uncheckedBox.get_rect(y=y)
            optionRect = optionName.get_rect(x=boxRect.right + 0.5 * boxRect.width, centery=boxRect.centery)
            nameRect = pygame.Rect(0, y, nameWidth, boxEdgeLen)
            self.__boxesRects.append(boxRect)
            self.__namesRects.append(nameRect)
            optionRects.append(optionRect)
            y += 1.5 * boxEdgeLen

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
        """Handles event of mouse button being pressed down"""
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


class Leaderboard(Element):
    """Class to represent leaderboard"""
    def __init__(self, titleFont, entryFont, fontColor, backgroundColor, icon, entryLimit, width, data):
        self.__font = titleFont
        self.__entryFont = entryFont
        self.__fontColor = fontColor
        self.__backgroundColor = backgroundColor
        self.__icon = icon
        self.__entryLimit = entryLimit
        self.__data = data

        textHeight = titleFont.get_height()

        self.__laneWidth = width // 3
        self.__xGap = 2 * titleFont.size("|")[0]
        self.__yGap = 0.5 * textHeight

        self.__width = 3 * self.__laneWidth
        self.__height = ((4 + self.__entryLimit) * self.__yGap + (2 + self.__entryLimit) * textHeight)

        super().__init__(pygame.Surface((self.__width, self.__height), pygame.SRCALPHA))
        self._rect = self._surface.get_rect()

        self.__title = titleFont.render("LEADERBOARD", True, fontColor)
        self.__beginnerHeader = titleFont.render("BEGINNER", True, fontColor)
        self.__intermediateHeader = titleFont.render("INTERMEDIATE", True, fontColor)
        self.__advancedHeader = titleFont.render("ADVANCED", True, fontColor)
        self.__entryStartHeight = (2 * self.__yGap + 3 * textHeight)

        self.fill_lanes()

    def __draw_lanes(self):
        """Draws empty leaderboard"""
        self._surface.fill(self.__backgroundColor)

        titleTop = self.__yGap
        difficultiesTop = titleTop + 2 * self.__font.get_height()

        frameLeft = 0
        frameTop = 0
        frameTitleSeparatorHeight = 2 * self.__yGap + self.__font.get_height()

        pygame.draw.line(self._surface, self.__fontColor, (frameLeft, frameTop), (self.__width, frameTop), 2)
        pygame.draw.line(self._surface, self.__fontColor, (frameLeft, frameTop), (frameLeft, self.__height), 2)
        pygame.draw.line(self._surface, self.__fontColor, (self.__width - 2, frameTop),
                         (self.__width - 2, self.__height), 2)
        pygame.draw.line(self._surface, self.__fontColor, (frameLeft, self.__height - 2),
                         (self.__width, self.__height - 2), 2)

        pygame.draw.line(self._surface, self.__fontColor, (frameLeft, frameTitleSeparatorHeight),
                         (self.__width, frameTitleSeparatorHeight))
        pygame.draw.line(self._surface, self.__fontColor, (self.__laneWidth, frameTitleSeparatorHeight),
                         (self.__laneWidth, self.__height))
        pygame.draw.line(self._surface, self.__fontColor, (2 * self.__laneWidth, frameTitleSeparatorHeight),
                         (2 * self.__laneWidth, self.__height))

        titleRect = self.__title.get_rect(top=self.__yGap, centerx=0.5 * self.__width)
        firstLaneHeaderRect = self.__beginnerHeader.get_rect(top=difficultiesTop, centerx=0.5 * self.__laneWidth)
        secondLaneHeaderRect = self.__intermediateHeader.get_rect(top=difficultiesTop, centerx=1.5 * self.__laneWidth)
        thirdLaneHeaderRect = self.__advancedHeader.get_rect(top=difficultiesTop, centerx=2.5 * self.__laneWidth)

        leftIconRect = self.__icon.get_rect(top=5, centerx=titleRect.left - 20)
        rightIconRect = self.__icon.get_rect(top=5, centerx=titleRect.right + 20)

        self._surface.blit(self.__title, titleRect)
        self._surface.blit(self.__beginnerHeader, firstLaneHeaderRect)
        self._surface.blit(self.__intermediateHeader, secondLaneHeaderRect)
        self._surface.blit(self.__advancedHeader, thirdLaneHeaderRect)
        self._surface.blit(self.__icon, leftIconRect)
        self._surface.blit(self.__icon, rightIconRect)

    def fill_lanes(self):
        """Populates leaderboard with contents of data dictionary"""
        self.__draw_lanes()
        xName = self.__xGap
        xTime = self.__laneWidth - self.__xGap
        for difficulty in ['BEGINNER', 'INTERMEDIATE', 'ADVANCED']:
            y = self.__entryStartHeight
            for name, time in self.__data[difficulty]:
                drawnName = self.__entryFont.render(name, True, self.__fontColor)
                drawnTime = self.__entryFont.render(str(time), True, self.__fontColor)
                timeWidth = self.__entryFont.size(str(time))[0]
                self._surface.blit(drawnName, (xName, y))
                self._surface.blit(drawnTime, (xTime - timeWidth, y))
                y += self.__entryFont.get_height() + self.__yGap

            xName += self.__laneWidth
            xTime += self.__laneWidth

    def needs_update(self, difficulty, time):
        """Checks if time passed as argument is good enough
            to be put in provided difficulty category in data dictionary"""
        data = self.__data[difficulty]
        if len(data) < self.__entryLimit:
            return True

        return data[-1][1] > time

    def update(self, difficulty, name, time):
        """Places new entry = (name, time) into provided difficulty category in data dictionary"""
        data = self.__data[difficulty]
        i = 0
        while i < len(data) and time >= data[i][1]:
            i += 1
        data.insert(i, (name, time))

        if len(data) > self.__entryLimit:
            data.pop()

        self.fill_lanes()

    def get_data(self):
        return self.__data

    def set_data(self, newData):
        self.__data = newData


class InputFrame(Element):
    """Class to create frame with place for user to input data from keyboard"""
    def __init__(self, font, fontColor, backgroundColor, message, charactersLimit, action):
        self.__font = font
        self.__fontColor = fontColor
        self.__backgroundColor = backgroundColor
        self.__drawnMessage = font.render(message, True, fontColor)
        self.__charactersLimit = charactersLimit
        self.__action = action
        self.__input = ""

        yGap = 0.5 * font.get_height()
        xGap = font.size("_")[0]
        width = self.__drawnMessage.get_width() + 2 * xGap
        height = 3 * yGap + 2 * font.get_height()

        super().__init__(draw_frame(width, height, fontColor))

        self.__drawnMessageRect = self.__drawnMessage.get_rect(x=xGap, y=yGap)
        self._rect = self._surface.get_rect()

        self.__valueTop = 2 * yGap + font.get_height()
        self.__prepare()

    def __prepare(self):
        """Prepares frame to be drawn"""
        self._surface = draw_frame(self._surface.get_size()[0], self._surface.get_size()[1],
                                   self.__fontColor, self.__backgroundColor)
        self._surface.blit(self.__drawnMessage, self.__drawnMessageRect)
        drawnInput = self.__font.render(self.__input + "_", True, self.__fontColor)
        rect = drawnInput.get_rect(top=self.__valueTop, centerx=0.5 * self._surface.get_width())
        self._surface.blit(drawnInput, rect)

    def handle_key_down(self, event):
        """Handles event of keyboard key being pressed down"""
        key = event.key
        if key == pygame.K_BACKSPACE:
            if self.__input:
                self.__input = self.__input[:-1]
                self.__prepare()
        elif key == pygame.K_RETURN:
            self.__action(self.__input)
        else:
            if len(self.__input) == self.__charactersLimit:
                return

            unicode = event.unicode
            if check_entry_key(unicode):
                self.__input += unicode
                self.__prepare()

    def reset_input(self):
        self.__input = ''
        self.__prepare()


class Popup(Element):
    """Class to represent popup window with provided icon, text message and two option buttons"""
    def __init__(self, font, fontColor, backgroundColor, message, icon, buttonConfirm, buttonDeny):
        self.__font = font
        self.__fontColor = fontColor
        self.__backgroundColor = backgroundColor
        self.__icon = icon
        self.__buttonConfirm = buttonConfirm
        self.__buttonDeny = buttonDeny

        self.__xGap = 2 * font.size("|")[0]
        self.__yGap = 0.5 * font.get_height()

        lines = message.split('\n')
        self.__renderedLines = []

        for line in lines:
            self.__renderedLines.append(font.render(line, True, fontColor))

        self.__width = max(map(lambda l: l.get_width(), self.__renderedLines)) + icon.get_width() + 3 * self.__xGap
        self.__height = max(icon.get_height(), len(lines) * (font.get_height() + self.__yGap)) + 3 * self.__yGap \
            + self.__buttonConfirm.get_rect().height

        super().__init__(pygame.Surface((self.__width, self.__height), pygame.SRCALPHA))
        self._rect = self._surface.get_rect()

        self.__prepare()

    def __prepare(self):
        """Prepares popup to be drawn"""
        self._surface = draw_frame(self._surface.get_size()[0], self._surface.get_size()[1],
                                   self.__fontColor, self.__backgroundColor)

        iconRect = self.__icon.get_rect(centery=self._surface.get_height() / 2, left=self.__xGap)
        linesRects = []
        y = self.__yGap
        for line in self.__renderedLines:
            linesRects.append(line.get_rect(
                top=y, centerx=(self._rect.width - iconRect.width) / 2 + iconRect.width + self.__yGap))
            y += line.get_height() + self.__yGap

        self._surface.blit(self.__icon, iconRect)

        for i in range(len(self.__renderedLines)):
            self._surface.blit(self.__renderedLines[i], linesRects[i])

    def handle_mouse_up(self, button):
        """Handles event of mouse button being pressed down"""
        if button != 1:  # LMB
            return

        self.__buttonConfirm.handle_mouse_up(button)
        self.__buttonDeny.handle_mouse_up(button)
