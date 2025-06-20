"""
Модуль утилит.

Содержит вспомогательные функции для работы с изображениями
и другими ресурсами игры.
"""

import pygame


def load_image(path: str) -> pygame.Surface | None:
    """
    Загружает изображение из указанного пути.
    
    Args:
        path: Путь к файлу изображения.
        
    Returns:
        Загруженная поверхность pygame или None в случае ошибки.
    """
    from core.pathutils import resource_path
    full_path = resource_path(path)
    try:
        return pygame.image.load(full_path).convert_alpha()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Ошибка загрузки изображения: {full_path}, {e}")
        return None
