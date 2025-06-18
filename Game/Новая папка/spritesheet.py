import pygame
from core.config import config
import os


class SpriteSheet:
    def __init__(self, filename: str, width: int = 128, height: int = 64) -> None:
        self.width = width
        self.height = height
        self.sheet = None  # Важно инициализировать атрибут

        try:
            # Проверяем существование файла
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Файл не найден: {filename}")

            self.sheet = pygame.image.load(filename).convert_alpha()
            if config.DEBUG_MODE:
                print(f"✅ Спрайт загружен: {filename}")

        except Exception as e:
            if config.DEBUG_MODE:
                print(f"❌ Ошибка загрузки спрайта: {e}")
            # Создаём красный квадрат вместо спрайта
            self.sheet = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.sheet, (255, 0, 0), (0, 0, width, height))
            pygame.draw.line(self.sheet, (0, 0, 0), (0, 0), (width, height), 2)
            pygame.draw.line(self.sheet, (0, 0, 0), (width, 0), (0, height), 2)

    def get_image(self, x, y, width, height):
        if self.sheet is None:
            return pygame.Surface((width, height), pygame.SRCALPHA)

        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        return image
