import pygame
import os
from Game.core import config


def create_level():
    try:
        # Полный путь к фоновому изображению
        bg_path = os.path.join("assets", "images", "game", "backgrounds", "level", "first_level.png")
        background = pygame.image.load(bg_path).convert()
        level_width, level_height = background.get_size()

    except FileNotFoundError as e:
        print(f"Ошибка загрузки фона: {e}")
        level_width, level_height = config.DEFAULT_LEVEL_WIDTH, config.DEFAULT_LEVEL_HEIGHT
        background = pygame.Surface((level_width, level_height))
        background.fill(config.GAME_COLORS["DARK_BLUE"])

        # Сетка для отладки
        for x in range(0, level_width, 100):
            for y in range(0, level_height, 100):
                pygame.draw.rect(background, config.GAME_COLORS["BLUE"], (x, y, 100, 100), 1)

    return level_width, level_height, background