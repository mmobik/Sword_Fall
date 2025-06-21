"""
Интерфейс для отображения характеристик игрока.
Следует принципам SOLID и обеспечивает отделение UI от логики.
"""

import pygame
from typing import Optional, Tuple
from level.player_stats import StatObserver, PlayerStats
from core.config import config


class PlayerUI(StatObserver):
    """Интерфейс для отображения характеристик игрока."""
    
    def __init__(self, screen: pygame.Surface, player_stats: PlayerStats):
        self.screen = screen
        self.player_stats = player_stats
        
        # Подписываемся на изменения характеристик
        self.player_stats.add_observer(self)
        
        if config.DEBUG_MODE:
            print(f"[UI DEBUG] UI создан и подписан на изменения характеристик")
        
        # Настройки UI
        self.ui_padding = 20
        self.bar_height = 25
        self.bar_width = 200
        self.text_color = config.COLORS["WHITE"]
        self.background_color = (0, 0, 0, 128)  # Полупрозрачный черный
        
        # Цвета полосок
        self.health_colors = {
            "background": (50, 50, 50),
            "border": (100, 100, 100),
            "fill": (255, 50, 50),  # Красный
            "low_health": (255, 0, 0)  # Ярко-красный для низкого здоровья
        }
        
        self.stamina_colors = {
            "background": (50, 50, 50),
            "border": (100, 100, 100),
            "fill": (50, 150, 255),  # Синий
            "exhausted": (100, 100, 100)  # Серый для истощения
        }
        
        self.exp_colors = {
            "background": (50, 50, 50),
            "border": (100, 100, 100),
            "fill": (255, 215, 0)  # Золотой
        }
        
        # Шрифты
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 28)
        
        # Анимация изменений
        self.animation_duration = 0.5
        self.animation_timers = {}
        self.old_values = {}
        
        # Позиции элементов UI
        self.ui_positions = {
            "health": (self.ui_padding, self.ui_padding),
            "stamina": (self.ui_padding, self.ui_padding + self.bar_height + 10),
            "experience": (self.ui_padding, self.ui_padding + (self.bar_height + 10) * 2)
        }
    
    def on_stat_changed(self, stat_name: str, old_value: float, new_value: float):
        """Вызывается при изменении характеристики."""
        if config.DEBUG_MODE:
            print(f"[UI DEBUG] Изменение характеристики: {stat_name} {old_value:.1f} -> {new_value:.1f} (разница: {new_value - old_value:.1f})")
        
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
    
    def draw(self):
        """Отрисовывает интерфейс игрока."""
        # Отладочная информация только в режиме отладки
        if hasattr(self.player_stats, 'health') and config.DEBUG_MODE:
            print(f"[UI DEBUG] Отрисовка UI: HP={self.player_stats.health.current_value}/{self.player_stats.health.max_value}, SP={self.player_stats.stamina.current_value}/{self.player_stats.stamina.max_value}")
        
        self._draw_health_bar()
        self._draw_stamina_bar()
        self._draw_experience_bar()
        self._draw_level_info()
    
    def _draw_health_bar(self):
        """Отрисовывает полоску здоровья."""
        x, y = self.ui_positions["health"]
        health_stat = self.player_stats.health
        
        # Определяем цвет заполнения
        health_percent = health_stat.get_health_percentage()
        if health_percent < 0.3:
            fill_color = self.health_colors["low_health"]
        else:
            fill_color = self.health_colors["fill"]
        
        self._draw_stat_bar(
            x, y, 
            health_stat.current_value, 
            health_stat.max_value,
            fill_color,
            self.health_colors["background"],
            self.health_colors["border"],
            f"HP: {health_stat.get_display_value()}"
        )
    
    def _draw_stamina_bar(self):
        """Отрисовывает полоску выносливости."""
        x, y = self.ui_positions["stamina"]
        stamina_stat = self.player_stats.stamina
        
        # Определяем цвет заполнения
        if stamina_stat.is_exhausted:
            fill_color = self.stamina_colors["exhausted"]
        else:
            fill_color = self.stamina_colors["fill"]
        
        self._draw_stat_bar(
            x, y,
            stamina_stat.current_value,
            stamina_stat.max_value,
            fill_color,
            self.stamina_colors["background"],
            self.stamina_colors["border"],
            f"SP: {stamina_stat.get_display_value()}"
        )
    
    def _draw_experience_bar(self):
        """Отрисовывает полоску опыта."""
        x, y = self.ui_positions["experience"]
        exp_stat = self.player_stats.experience
        
        self._draw_stat_bar(
            x, y,
            exp_stat.current_value,
            exp_stat.experience_to_next,
            self.exp_colors["fill"],
            self.exp_colors["background"],
            self.exp_colors["border"],
            f"XP: {int(exp_stat.current_value)}/{int(exp_stat.experience_to_next)}"
        )
    
    def _draw_level_info(self):
        """Отрисовывает информацию об уровне."""
        x, y = self.ui_positions["experience"]
        exp_stat = self.player_stats.experience
        
        level_text = f"Level {exp_stat.level}"
        level_surface = self.font_medium.render(level_text, True, self.text_color)
        
        # Позиция справа от полоски опыта
        level_x = x + self.bar_width + 10
        level_y = y + (self.bar_height - level_surface.get_height()) // 2
        
        self.screen.blit(level_surface, (level_x, level_y))
    
    def _draw_stat_bar(self, x: int, y: int, current: float, maximum: float, 
                      fill_color: Tuple[int, int, int], bg_color: Tuple[int, int, int], 
                      border_color: Tuple[int, int, int], label: str):
        """Отрисовывает полоску характеристики."""
        # Фон
        bg_rect = pygame.Rect(x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(self.screen, bg_color, bg_rect)
        
        # Заполнение
        if maximum > 0:
            fill_width = int((current / maximum) * self.bar_width)
            fill_rect = pygame.Rect(x, y, fill_width, self.bar_height)
            pygame.draw.rect(self.screen, fill_color, fill_rect)
        
        # Граница
        pygame.draw.rect(self.screen, border_color, bg_rect, 2)
        
        # Текст
        text_surface = self.font_small.render(label, True, self.text_color)
        text_x = x + 5
        text_y = y + (self.bar_height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_damage_indicator(self, damage: float, position: Tuple[int, int]):
        """Отрисовывает индикатор урона."""
        if damage <= 0:
            return
        
        # Создаем поверхность для текста
        damage_text = f"-{int(damage)}"
        text_surface = self.font_medium.render(damage_text, True, (255, 0, 0))
        
        # Позиция над игроком
        text_x = position[0] - text_surface.get_width() // 2
        text_y = position[1] - 50
        
        # Отрисовываем с тенью для лучшей видимости
        shadow_surface = self.font_medium.render(damage_text, True, (0, 0, 0))
        self.screen.blit(shadow_surface, (text_x + 1, text_y + 1))
        self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_heal_indicator(self, heal: float, position: Tuple[int, int]):
        """Отрисовывает индикатор лечения."""
        if heal <= 0:
            return
        
        # Создаем поверхность для текста
        heal_text = f"+{int(heal)}"
        text_surface = self.font_medium.render(heal_text, True, (0, 255, 0))
        
        # Позиция над игроком
        text_x = position[0] - text_surface.get_width() // 2
        text_y = position[1] - 50
        
        # Отрисовываем с тенью для лучшей видимости
        shadow_surface = self.font_medium.render(heal_text, True, (0, 0, 0))
        self.screen.blit(shadow_surface, (text_x + 1, text_y + 1))
        self.screen.blit(text_surface, (text_x, text_y))
    
    def draw_death_screen(self):
        """Отрисовывает экран смерти."""
        if not self.player_stats.is_alive():
            # Полупрозрачный фон
            overlay = pygame.Surface(self.screen.get_size())
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Текст смерти
            death_text = "YOU DIED"
            text_surface = self.font_large.render(death_text, True, (255, 0, 0))
            text_x = (self.screen.get_width() - text_surface.get_width()) // 2
            text_y = (self.screen.get_height() - text_surface.get_height()) // 2
            
            self.screen.blit(text_surface, (text_x, text_y))
            
            # Инструкция
            instruction_text = "Press R to respawn"
            instruction_surface = self.font_medium.render(instruction_text, True, self.text_color)
            instruction_x = (self.screen.get_width() - instruction_surface.get_width()) // 2
            instruction_y = text_y + text_surface.get_height() + 20
            
            self.screen.blit(instruction_surface, (instruction_x, instruction_y)) 