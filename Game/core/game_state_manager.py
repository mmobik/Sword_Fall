"""
Модуль управления состоянием игры.

Содержит класс GameStateManager для управления различными состояниями игры,
включая переходы между меню и игровым процессом с анимациями.
"""

import sys
import time
import pygame
from core.config import config


class GameStateManager:
    """
    Класс для управления состоянием игры.
    
    Обеспечивает переходы между различными состояниями игры,
    управление меню и анимации переходов.
    """

    def __init__(self, sound_manager):
        """
        Инициализация менеджера состояний.
        
        Args:
            sound_manager: Менеджер звука для воспроизведения эффектов.
        """
        self.game_state = "main_menu"
        self.current_menu = None
        self.sound_manager = sound_manager
        self.fade_surface = pygame.Surface(config.SCREEN_SIZE, pygame.SRCALPHA)
        self.should_process_menu = True  # Новый флаг

    def change_state(self, new_state: str, menu=None) -> None:
        """
        Изменяет состояние игры.
        
        Args:
            new_state: Новое состояние игры.
            menu: Меню для отображения в новом состоянии.
        """
        if new_state == "new_game":
            self.animate_transition(menu, config.FADE_DURATION)
            self.should_process_menu = False  # Отключаем обработку меню
        else:
            self.should_process_menu = True  # Включаем обработку меню
        self.game_state = new_state
        self.current_menu = menu

    def get_state(self) -> str:
        """
        Получает текущее состояние игры.
        
        Returns:
            Текущее состояние игры.
        """
        return self.game_state

    def animate_transition(self, menu, duration: float = config.FADE_DURATION) -> None:
        """
        Анимирует переход между состояниями.
        
        Args:
            menu: Меню для отображения во время перехода.
            duration: Длительность анимации в секундах.
        """
        # Фаза затемнения
        alpha = 0
        start_time = time.time()

        while alpha < 255:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            time_elapsed = time.time() - start_time
            alpha = min(255, int(255 * time_elapsed / duration))
            self.fade_surface.fill((0, 0, 0, alpha))

            if menu:
                menu.draw(pygame.display.get_surface(), pygame.mouse.get_pos())

            pygame.display.get_surface().blit(self.fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.Clock().tick(config.TARGET_FPS)

        # Фаза осветления
        alpha = 255
        start_time = time.time()

        while alpha > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            time_elapsed = time.time() - start_time
            alpha = max(0, 255 - int(255 * time_elapsed / duration))
            self.fade_surface.fill((0, 0, 0, alpha))
            pygame.display.get_surface().blit(self.fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.Clock().tick(config.TARGET_FPS)
