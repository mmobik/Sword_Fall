"""
Модуль камеры.

Содержит класс Camera для управления камерой, которая следует за игроком
и обеспечивает правильное отображение игрового мира.
"""

import pygame
from core.config import config


class Camera:
    """
    Класс для управления камерой, которая следует за игроком.
    
    Обеспечивает плавное следование камеры за целью с учетом границ уровня
    и центрирование на виртуальном экране.
    """

    def __init__(self, level_width: int, level_height: int):
        """
        Инициализация камеры.

        Args:
            level_width: Ширина уровня в пикселях.
            level_height: Высота уровня в пикселях.
        """
        self.offset = pygame.math.Vector2()
        self.level_rect = pygame.Rect(0, 0, level_width, level_height)

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Применяет смещение камеры к объекту.
        
        Args:
            rect: Прямоугольник объекта для преобразования.
            
        Returns:
            Преобразованный прямоугольник с учетом смещения камеры.
        """
        return rect.move(-self.offset.x, -self.offset.y)

    def update(self, target) -> None:
        """
        Обновляет позицию камеры, следуя за целью.
        
        Args:
            target: Объект, за которым следует камера (обычно игрок).
        """
        # Центрируем камеру на хитбоксе игрока
        target_x = target.hitbox.centerx - config.VIRTUAL_WIDTH // 2
        target_y = target.hitbox.centery - config.VIRTUAL_HEIGHT // 2

        # Жёсткие границы для камеры
        self.offset.x = max(0, min(target_x, 
                                  self.level_rect.width - config.VIRTUAL_WIDTH))
        self.offset.y = max(0, min(target_y, 
                                  self.level_rect.height - config.VIRTUAL_HEIGHT))

        # Фикс для маленьких уровней
        if self.level_rect.width < config.VIRTUAL_WIDTH:
            self.offset.x = (self.level_rect.width - config.VIRTUAL_WIDTH) // 2
        if self.level_rect.height < config.VIRTUAL_HEIGHT:
            self.offset.y = (self.level_rect.height - config.VIRTUAL_HEIGHT) // 2
