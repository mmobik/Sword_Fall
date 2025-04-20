import pygame
from Game.core import config


class SpriteSheet:
    """
    Класс для работы со спрайт-листами (sheet).
    """

    def __init__(self, filename: str, width: int = 128, height: int = 64) -> None:
        """
        Инициализация SpriteSheet.

        Args:
            filename (str): Путь к файлу спрайт-листа.
        """
        self.download = 1
        self.width = width
        self.height = height
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()  # Загрузка спрайт-листа

        # Заглушка если спрайт не загрузилс
        except FileNotFoundError:
            self.download = 0
            self.sheet = pygame.Surface((self.width, self.height),  pygame.SRCALPHA)
            pygame.draw.rect(self.sheet, config.GAME_COLORS["WHITE"], (0, 0, self.width, self.height), 1)

    def get_image(self, x, y, width, height):
        """
        Вырезает кадр анимации из спрайт-листа.

        Args:
            x (int): X координата кадра.
            y (int): Y координата кадра.
            width (int): Ширина кадра.
            height (int): Высота кадра.

        Returns:
            pygame.Surface: Изображение кадра.
        """
        image = pygame.Surface((width, height), pygame.SRCALPHA)  # Создание поверхности
        image.blit(self.sheet, (0, 0), (x, y, width, height))  # Вырезание кадра
        return image
