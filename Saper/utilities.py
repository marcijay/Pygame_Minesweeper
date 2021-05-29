import json
import pygame
import re

ENTRY_UNICODE_REGEX = re.compile('[@_!#$%^&*()<>?/\\|}{~:\[\]]')


def create_background(rows, cols, tileSize, bgColor, lineColor):
    field = pygame.Surface((cols * tileSize, rows * tileSize))
    field.fill(bgColor)

    for i in range(rows):
        pygame.draw.line(field, lineColor, (0, i * tileSize), (cols * tileSize, i * tileSize))

    for j in range(cols):
        pygame.draw.line(field, lineColor, (j * tileSize, 0), (j * tileSize, rows * tileSize))

    return field


def draw_frame(width, height, lineColor, backgroundColor=None):
    frame = pygame.Surface((width, height), pygame.SRCALPHA)
    if backgroundColor is not None:
        frame.fill(backgroundColor)
    pygame.draw.line(frame, lineColor, (0, 0), (width, 0))
    pygame.draw.line(frame, lineColor, (0, 0), (0, height))
    pygame.draw.line(frame, lineColor, (width - 1, 0), (width - 1, height))
    pygame.draw.line(frame, lineColor, (0, height - 1), (width, height - 1))

    return frame


def draw_checked_box(side, color):
    box = draw_frame(side, side, color)
    shift = 0.3 * side
    pygame.draw.line(box, color, (shift, shift), (side - shift, side - shift))
    pygame.draw.line(box, color, (side - shift, shift), (shift, side - shift))

    return box


def check_entry_key(unicode):
    return ENTRY_UNICODE_REGEX.search(unicode) or unicode.isalnum()


def unload_game_data(dataFilePath):
    try:
        with open(dataFilePath) as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError):
        data = {}

    return data
