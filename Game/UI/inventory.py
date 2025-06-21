"""
Простая система инвентаря для отображения изображения inventory.png.
"""

import pygame
import os
from typing import Optional
from level.player_stats import PlayerStats
from core.config import config


class Inventory:
    """Простой класс инвентаря для отображения изображения."""
    
    def __init__(self, screen: pygame.Surface, player_stats: PlayerStats, initial_open: bool = False):
        self.screen = screen
        self.player_stats = player_stats
        
        # Загружаем изображение инвентаря
        self.inventory_image = self._load_inventory_image()
        
        # Настройки позиционирования
        self.inventory_x = 50
        self.inventory_y = 50
        
        # Состояние видимости инвентаря
        self.inventory_open = initial_open
        
        if config.DEBUG_MODE:
            print(f"[INVENTORY DEBUG] Создан новый инвентарь, состояние: {self.inventory_open}")
            if hasattr(self.player_stats, 'game'):
                print(f"[INVENTORY DEBUG] Глобальное состояние: {getattr(self.player_stats.game, 'inventory_open_state', 'N/A')}")
    
    def _load_inventory_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение inventory.png."""
        try:
            # Путь к изображению
            image_path = "assets/images/game/playerData/inventory.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                if config.DEBUG_MODE:
                    print(f"[INVENTORY DEBUG] Изображение inventory загружено: {image.get_size()}")
                return image
            else:
                print(f"[INVENTORY ERROR] Файл не найден: {image_path}")
                return None
        except Exception as e:
            print(f"[INVENTORY ERROR] Ошибка загрузки inventory: {e}")
            return None
    
    def toggle_inventory(self):
        """Переключает состояние инвентаря (открыт/закрыт)."""
        old_state = self.inventory_open
        self.inventory_open = not self.inventory_open
        if config.DEBUG_MODE:
            print(f"[INVENTORY DEBUG] Инвентарь переключен: {old_state} -> {self.inventory_open}")
            print(f"[INVENTORY DEBUG] Вызов из: {self.__class__.__name__}")
    
    def handle_click(self, mouse_pos):
        """Обрабатывает клик мыши в инвентаре."""
        # В новой реализации пока ничего не обрабатываем
        pass
    
    def draw(self):
        """Отрисовывает изображение инвентаря."""
        if self.inventory_image and self.inventory_open:
            self.screen.blit(self.inventory_image, (self.inventory_x, self.inventory_y)) 