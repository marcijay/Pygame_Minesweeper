import json
import os
import pygame
import re

SPECIAL_CHARACTER_REGEX = re.compile('[@_!#$%^&*()<>?/\\|}{~:\[\]]')


def create_background(rows, cols, tileSize, bgColor, lineColor):
    """Creates and returns surface of given color,
     visually divided into rectangles according to provided number of rows and columns"""
    field = pygame.Surface((cols * tileSize, rows * tileSize))
    field.fill(bgColor)

    for i in range(rows):
        pygame.draw.line(field, lineColor, (0, i * tileSize), (cols * tileSize, i * tileSize))

    for j in range(cols):
        pygame.draw.line(field, lineColor, (j * tileSize, 0), (j * tileSize, rows * tileSize))

    return field


def draw_frame(width, height, lineColor, backgroundColor=None):
    """Creates and returns frame (pygame.Surface) of given size optionally filled with solid color"""
    frame = pygame.Surface((width, height), pygame.SRCALPHA)
    if backgroundColor is not None:
        frame.fill(backgroundColor)
    pygame.draw.line(frame, lineColor, (0, 0), (width, 0))
    pygame.draw.line(frame, lineColor, (0, 0), (0, height))
    pygame.draw.line(frame, lineColor, (width - 1, 0), (width - 1, height))
    pygame.draw.line(frame, lineColor, (0, height - 1), (width, height - 1))

    return frame


def draw_checked_box(side, color):
    """Creates and returns square (pygame.Surface) with drawn cross of given size"""
    box = draw_frame(side, side, color)
    shift = 0.3 * side
    pygame.draw.line(box, color, (shift, shift), (side - shift, side - shift))
    pygame.draw.line(box, color, (side - shift, shift), (shift, side - shift))

    return box


def check_entry_key(unicode):
    """Checks if passed unicode sign is appropriate"""
    return SPECIAL_CHARACTER_REGEX.search(unicode) or unicode.isalnum()


def unload_game_data(dataFilePath):
    """Creates and returns dictionary based on contents of file ot given path"""
    try:
        with open(dataFilePath) as file:
            data = json.load(file)
    except (IOError, json.JSONDecodeError):
        data = {}

    return data


def load_sounds():
    """Creates and returns dictionary based on contents of directory ot given path"""
    sounds = {}
    for fileName in os.listdir("assets/sounds"):
        if not fileName.endswith(".wav"):
            continue
        sound = pygame.mixer.Sound("assets/sounds/" + fileName)
        sounds[fileName.split('.')[0]] = sound
    return sounds
