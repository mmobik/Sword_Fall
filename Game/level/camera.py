import pygame
from core.config import config


class Camera:
    """
    Класс для управления камерой, которая следует за игроком.
    """

    def __init__(self, level_width, level_height):
        """
        Инициализация камеры.

        Args:
            level_width (int): Ширина уровня.
            level_height (int): Высота уровня.
        """
        self.offset = pygame.math.Vector2()
        self.level_rect = pygame.Rect(0, 0, level_width, level_height)

    def apply(self, rect):
        """Применяет смещение камеры к объекту"""
        return rect.move(-self.offset.x, -self.offset.y)

    def update(self, target):
        """Обновляет позицию камеры, следуя за целью"""
        # Центрируем камеру на хитбоксе игрока
        print(f"До камеры: target={target.hitbox.center}, offset={self.offset}")
        target_x = target.hitbox.centerx - config.VIRTUAL_WIDTH // 2
        target_y = target.hitbox.centery - config.VIRTUAL_HEIGHT // 2

        # Жёсткие границы для камеры
        self.offset.x = max(0, min(target_x, self.level_rect.width - config.VIRTUAL_WIDTH))
        self.offset.y = max(0, min(target_y, self.level_rect.height - config.VIRTUAL_HEIGHT))
        print(f"После камеры: offset={self.offset}")

        # Фикс для маленьких уровней
        if self.level_rect.width < config.VIRTUAL_WIDTH:
            self.offset.x = (self.level_rect.width - config.VIRTUAL_WIDTH) // 2
        if self.level_rect.height < config.VIRTUAL_HEIGHT:
            self.offset.y = (self.level_rect.height - config.VIRTUAL_HEIGHT) // 2
