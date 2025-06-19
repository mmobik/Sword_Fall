"""
Модуль утилит.

Содержит вспомогательные функции для работы с изображениями
и другими ресурсами игры.
"""

import pygame
from core.config import config


def load_image(path: str) -> pygame.Surface | None:
    """
    Загружает изображение из указанного пути.
    
    Args:
        path: Путь к файлу изображения.
        
    Returns:
        Загруженная поверхность pygame или None в случае ошибки.
    """
    full_path = path
    try:
        return pygame.image.load(full_path).convert_alpha()
    except (pygame.error, FileNotFoundError) as e:
        if config.DEBUG_MODE:
            print(f"Ошибка загрузки изображения: {full_path}, {e}")
        return None
