import pygame
import os


def load_image(path):
    full_path = os.path.join("assets", path)
    try:
        return pygame.image.load(full_path).convert_alpha()
    except pygame.error as e:
        print(f"Ошибка загрузки изображения: {full_path}, {e}")
        return None
