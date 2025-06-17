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
        """
        Переводит координаты объекта в координаты камеры.

        Args:
            rect (pygame.Rect): Объект, чьи координаты нужно преобразовать.

        Returns:
            pygame.Rect: Преобразованный Rect.
        """
        return rect.move(-self.offset.x, -self.offset.y)

    def update(self, target):
        """
        Центрирует камеру на цели с учетом границ уровня.

        Args:
            target (Player): Объект, за которым следует камера.
        """
        #  Смещение относительно координат экрана
        target_x = target.rect.centerx - config.WIDTH // 2
        target_y = target.rect.centery - config.HEIGHT // 2

        # Ограничиваем камеру границами уровня
        self.offset.x = max(0, min(target_x, self.level_rect.width - config.WIDTH))
        self.offset.y = max(0, min(target_y, self.level_rect.height - config.HEIGHT))
