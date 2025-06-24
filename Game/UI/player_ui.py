"""
Интерфейс для отображения характеристик игрока.
Следует принципам SOLID и обеспечивает отделение UI от логики.
"""

import pygame
import os
from typing import Optional, Tuple
from level.player_stats import StatObserver, PlayerStats
from core.config import config
from UI.inventory import Inventory


class PlayerUI(StatObserver):
    """Интерфейс для отображения характеристик игрока."""
    
    def __init__(self, screen: pygame.Surface, player_stats: PlayerStats):
        self.screen = screen
        self.player_stats = player_stats
        self.just_closed_inventory = False
        
        # Подписываемся на изменения характеристик
        self.player_stats.add_observer(self)
        
        if config.DEBUG_MODE:
            print(f"[UI DEBUG] UI создан и подписан на изменения характеристик")
        
        # Загружаем изображение game_bar
        self.game_bar_image = self._load_game_bar_image()
        
        # Загружаем изображение belt
        self.belt_image = self._load_belt_image()
        
        # Создаем инвентарь с восстановлением состояния
        initial_open = False
        if hasattr(player_stats, 'game') and player_stats.game is not None and hasattr(player_stats.game, 'inventory_open_state'):
            initial_open = player_stats.game.inventory_open_state
            if config.DEBUG_MODE:
                print(f"[UI DEBUG] Получено состояние из game: {initial_open}")
        else:
            if config.DEBUG_MODE:
                print(f"[UI DEBUG] game не найден в player_stats, используем False")
        self.inventory = Inventory(screen, player_stats, initial_open=initial_open)
        
        # Настройки UI
        self.ui_padding = 20
        self.game_bar_x = 20  # Сдвигаем правее
        self.game_bar_y = 20
        
        # Позиция belt (внизу экрана)
        self.belt_y = config.VIRTUAL_HEIGHT - 100  # Отступ снизу
        
        # Анимации для изменений характеристик
        self.animation_duration = 1.0  # секунды
        self.animation_timers = {}
        self.old_values = {}
        
        # Кэшируем проверки для оптимизации
        self._has_health = hasattr(player_stats, 'health')
        self._has_stamina = hasattr(player_stats, 'stamina')
        
        # Шрифты и цвета
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 28)
        self.text_color = config.COLORS["WHITE"]
    
    def _load_game_bar_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение game_bar.png."""
        try:
            # Путь к изображению
            image_path = "assets/images/game/playerData/game_bar.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                if config.DEBUG_MODE:
                    print(f"[UI DEBUG] Изображение game_bar загружено: {image.get_size()}")
                return image
            else:
                print(f"[UI ERROR] Файл не найден: {image_path}")
                return None
        except Exception as e:
            print(f"[UI ERROR] Ошибка загрузки game_bar: {e}")
            return None
    
    def _load_belt_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение belt.png."""
        try:
            # Путь к изображению
            image_path = "assets/images/game/playerData/belt.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                if config.DEBUG_MODE:
                    print(f"[UI DEBUG] Изображение belt загружено: {image.get_size()}")
                return image
            else:
                print(f"[UI ERROR] Файл не найден: {image_path}")
                return None
        except Exception as e:
            print(f"[UI ERROR] Ошибка загрузки belt: {e}")
            return None
    
    def on_stat_changed(self, stat_name: str, old_value: float, new_value: float):
        """Вызывается при изменении характеристики."""
        self.old_values[stat_name] = old_value
        self.animation_timers[stat_name] = self.animation_duration
    
    def update(self, dt: float):
        """Обновляет анимации UI."""
        # Обновляем таймеры анимации
        for stat_name in list(self.animation_timers.keys()):
            self.animation_timers[stat_name] -= dt
            if self.animation_timers[stat_name] <= 0:
                del self.animation_timers[stat_name]
                if stat_name in self.old_values:
                    del self.old_values[stat_name]
    
    def handle_event(self, event):
        """Обрабатывает события для UI."""
        if self.just_closed_inventory:
            self.just_closed_inventory = False
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.inventory.toggle_inventory()
                if hasattr(self.player_stats, 'game') and self.player_stats.game is not None:
                    game = self.player_stats.game
                    if self.inventory.inventory_open:
                        game.game_state_manager.change_state("inventory_menu", self.inventory)
                    else:
                        game.game_state_manager.change_state("new_game", None)
                return
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левый клик
                # Обрабатываем клик в инвентаре
                self.inventory.handle_click(event.pos)
    
    def draw(self):
        """Отрисовывает интерфейс игрока."""
        # Отладочная информация только в режиме отладки
        if self._has_health and config.DEBUG_MODE:
            print(f"[UI DEBUG] Отрисовка UI: HP={self.player_stats.health.current_value}/{self.player_stats.health.max_value}, SP={self.player_stats.stamina.current_value}/{self.player_stats.stamina.max_value}")
        
        # Отрисовываем только изображение game_bar
        if self.game_bar_image:
            self.screen.blit(self.game_bar_image, (self.game_bar_x, self.game_bar_y))
        
        # Отрисовываем изображение belt
        if self.belt_image:
            self.screen.blit(self.belt_image, (self.game_bar_x, self.belt_y))
        
        # Отрисовываем инвентарь
        self.inventory.draw(self.screen)
    
    def draw_damage_indicator(self, damage: float, position: Tuple[int, int]):
        """Отрисовывает индикатор урона."""
        if damage <= 0:
            return
        
        # Создаем поверхность для текста
        damage_text = f"-{int(damage)}"
        text_surface = self.font_large.render(damage_text, True, (255, 0, 0))
        
        # Позиция текста
        text_x = position[0] - text_surface.get_width() // 2
        text_y = position[1] - text_surface.get_height() // 2
        
        # Отрисовываем текст
        self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_heal_indicator(self, heal: float, position: Tuple[int, int]):
        """Отрисовывает индикатор лечения."""
        if heal <= 0:
            return
        
        # Создаем поверхность для текста
        heal_text = f"+{int(heal)}"
        text_surface = self.font_large.render(heal_text, True, (0, 255, 0))
        
        # Позиция текста
        text_x = position[0] - text_surface.get_width() // 2
        text_y = position[1] - text_surface.get_height() // 2
        
        # Отрисовываем текст
        self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_death_screen(self):
        """Отрисовывает экран смерти."""
        # Создаем полупрозрачную поверхность
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Текст смерти
        death_text = "YOU DIED"
        text_surface = self.font_large.render(death_text, True, (255, 0, 0))
        
        # Центрируем текст
        text_x = (self.screen.get_width() - text_surface.get_width()) // 2
        text_y = (self.screen.get_height() - text_surface.get_height()) // 2
        
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Инструкция
        instruction_text = "Press R to respawn"
        instruction_surface = self.font_medium.render(instruction_text, True, self.text_color)
        
        instruction_x = (self.screen.get_width() - instruction_surface.get_width()) // 2
        instruction_y = text_y + text_surface.get_height() + 20
        
        self.screen.blit(instruction_surface, (instruction_x, instruction_y)) 