import pygame
import os


def load_image(path):
    full_path = path
    try:
        return pygame.image.load(full_path).convert_alpha()
    except (pygame.error, FileNotFoundError) as e:
        if config.DEBUG_MODE:
            print(f"Ошибка загрузки изображения: {full_path}, {e}")
        return None
