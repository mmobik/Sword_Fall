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
        self.background = None  # Для хранения скриншота фона
        
        if config.DEBUG_MODE:
            print(f"[INVENTORY DEBUG] Создан новый инвентарь, состояние: {self.inventory_open}")
            if hasattr(self.player_stats, 'game'):
                print(f"[INVENTORY DEBUG] Глобальное состояние: {getattr(self.player_stats.game, 'inventory_open_state', 'N/A')}")
    
    def _load_inventory_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение inventory.png."""
        try:
            # Путь к изображению
            image_path = "Game/assets/images/game/playerData/inventory.png"
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
        if self.inventory_open:
            # Сохраняем скриншот виртуального экрана
            game = getattr(self.player_stats, 'game', None)
            if game and hasattr(game, 'virtual_screen'):
                self.background = game.virtual_screen.copy()
            else:
                self.background = None
            # Остановить звук шагов у игрока, если он существует
            if game and hasattr(game, 'player') and game.player:
                player = game.player
                if hasattr(player, '_steps_channel') and player._steps_channel:
                    player._steps_channel.stop()
                    player._steps_channel = None
                player._was_walking = False
                player.is_walking = False
        else:
            self.background = None
        if config.DEBUG_MODE:
            print(f"[INVENTORY DEBUG] Инвентарь переключен: {old_state} -> {self.inventory_open}")
            print(f"[INVENTORY DEBUG] Вызов из: {self.__class__.__name__}")
    
    def handle_click(self, mouse_pos):
        """Обрабатывает клик мыши в инвентаре."""
        # В новой реализации пока ничего не обрабатываем
        pass
    
    def handle_event(self, event, mouse_pos=None):
        """Обрабатывает события для инвентаря (заглушка для совместимости)."""
        if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_i):
            game = getattr(self.player_stats, 'game', None)
            current_menu = getattr(getattr(game, 'game_state_manager', None), 'current_menu', None)
            self.toggle_inventory()
            # Сразу меняем состояние игры
            if hasattr(self.player_stats, 'game') and self.player_stats.game is not None:
                game = self.player_stats.game
                if not self.inventory_open:
                    game.game_state_manager.change_state("new_game", None)
                    game.game_state_manager.current_menu = None
                    if hasattr(game, 'player_ui') and game.player_ui:
                        game.player_ui.just_closed_inventory = True
                    if hasattr(game, 'talk_button') and hasattr(game.talk_button, 'force_show'):
                        game.talk_button.force_show()
            return
    
    def draw(self, screen, mouse_pos=None):
        """Отрисовывает изображение инвентаря (совместимо с системой меню)."""
        if self.inventory_open:
            # Рисуем фон-скриншот, если есть
            if self.background:
                # Масштабируем фон до размера экрана, если нужно
                if self.background.get_size() != screen.get_size():
                    bg = pygame.transform.scale(self.background, screen.get_size())
                else:
                    bg = self.background
                screen.blit(bg, (0, 0))
                # Затемнение
                overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
            # Рисуем сам инвентарь
            if self.inventory_image:
                screen.blit(self.inventory_image, (self.inventory_x, self.inventory_y))
    
    def update(self, dt):
        """Обновляет состояние инвентаря (заглушка для совместимости)."""
        pass 