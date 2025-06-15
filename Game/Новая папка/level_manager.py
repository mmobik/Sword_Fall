import pygame
from Game.core import config


# Инициализация уровня
def create_level():
    try:
        background = pygame.image.load(config.ASSETS["BACKGROUND"]).convert()
        level_width, level_height = background.get_size()

    # Если фон не загрузился, создаем простой уровень
    except FileNotFoundError:
        level_width, level_height = config.DEFAULT_LEVEL_WIDTH, config.DEFAULT_LEVEL_HEIGHT
        background = pygame.Surface((level_width, level_height))
        background.fill(config.GAME_COLORS["DARK_BLUE"])

        # Рисуем простой узор для ориентира
        for x in range(0, level_width, 100):
            for y in range(0, level_height, 100):
                pygame.draw.rect(background, config.GAME_COLORS["BLUE"], (x, y, 100, 100), 1)

    return level_width, level_height, background
