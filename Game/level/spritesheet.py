import pygame
from core.config import config


class SpriteSheet:
    """
    Класс для работы со спрайт-листами (sheet).
    """

    def __init__(self, filename: str, width: int = 128, height: int = 64) -> None:
        self.download = 1
        self.width = width
        self.height = height
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()  # Загрузка спрайт-листа
        except FileNotFoundError:
            self.download = 0
            self.sheet = pygame.Surface((self.width, self.height),  pygame.SRCALPHA)
            pygame.draw.rect(self.sheet, config.GAME_COLORS["WHITE"], (0, 0, self.width, self.height), 1)

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)  # Создание поверхности
        image.blit(self.sheet, (0, 0), (x, y, width, height))  # Вырезание кадра
        return image
