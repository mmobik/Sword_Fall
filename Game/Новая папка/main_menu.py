import pygame
from core.config import config
from core.utils import load_image
from .menu import Menu
from .button import Button
import sys

from .menu import Menu
from .button import Button
from core.config import config
from core.utils import load_image


class MainMenu(Menu):
    def __init__(self, sound_manager, settings_callback, game_callback):
        super().__init__(sound_manager)
        self.settings_callback = settings_callback
        self.game_callback = game_callback
        self._bg_key = "MAIN_BG_RUS" if config.current_language == "russian" else "MAIN_BG"
        self._static_surface = None  # Кэш статичной части
        self._create_buttons()
        self._pre_render_static()  # Предварительный рендеринг

    def _create_buttons(self):
        """Создание кнопок главного меню"""
        self.buttons = []

        buttons_data = [
            ("START_BTN", config.HEIGHT // 2 - config.BUTTON_SPACING, self.start_new_game),
            ("SETTINGS_BTN", config.HEIGHT // 2, self.open_settings_menu),
            ("EXIT_BTN", config.HEIGHT // 2 + config.BUTTON_SPACING, self.exit_game)
        ]

        for btn_key, y_pos, action in buttons_data:
            btn = Button(
                load_image(config.get_image(btn_key, "before")),
                load_image(config.get_image(btn_key, "after")),
                (config.MENU_BUTTON_X, y_pos),
                action,
                self.sound_manager
            )
            self.add_button(btn)

    def update_textures(self):
        """Обновление текстур при смене языка"""
        # Проверяем, действительно ли изменился язык
        if self._last_language != config.current_language:
            self._last_language = config.current_language
            self._bg_key = "MAIN_BG_RUS" if config.current_language == "russian" else "MAIN_BG"
            self._static_surface = None  # Сбрасываем кэш только при реальной смене языка
            self._create_buttons()
            self._pre_render_static()

    def draw(self, surface, mouse_pos=None):
        """Оптимизированная отрисовка главного меню"""
        # Проверяем, нужно ли обновить кэш
        if self._static_surface is None:
            self._pre_render_static()
        
        # Если мышь не двигалась и язык не менялся - рисуем кэшированную версию
        if mouse_pos == self._last_mouse_pos and self._last_language == config.current_language:
            surface.blit(self._static_surface, (0, 0))
            # Но все равно рисуем hover-эффекты если есть
            if mouse_pos:
                for button in self.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.draw(surface, mouse_pos)
            return

        self._last_mouse_pos = mouse_pos

        # Рисуем статичную часть
        surface.blit(self._static_surface, (0, 0))

        # Поверх рисуем все кнопки с учетом hover-эффектов
        for button in self.buttons:
            button.draw(surface, mouse_pos)

    def _pre_render_static(self):
        """Создаем кэш статичной части меню"""
        self._static_surface = pygame.Surface(config.SCREEN_SIZE)

        # Загружаем и рисуем фон
        try:
            bg = load_image(config.MENU_IMAGES[self._bg_key])
            if bg is not None:
                self._static_surface.blit(bg, (0, 0))
            else:
                self._static_surface.fill((40, 40, 60))  # Фон по умолчанию
        except:
            self._static_surface.fill((40, 40, 60))  # Фон по умолчанию

        # Рисуем все кнопки в их обычном состоянии
        for button in self.buttons:
            button.draw(self._static_surface, None)  # None - без hover-эффекта

    def start_new_game(self):
        """Обработчик начала игры"""
        if self.sound_manager:
            self.sound_manager.play_music("house.mp3")
        self.game_callback("new_game")

    def open_settings_menu(self):
        """Обработчик открытия настроек"""
        self.settings_callback()

    def exit_game(self):
        """Обработчик выхода из игры"""
        pygame.quit()
        sys.exit()
