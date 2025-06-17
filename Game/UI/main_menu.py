import pygame
from Game.core.config import config
from Game.core.utils import load_image
from .menu import Menu
from .button import Button
import sys

from .menu import Menu
from .button import Button
from Game.core.config import config
from Game.core.utils import load_image


class MainMenu(Menu):
    def __init__(self, sound_manager, settings_callback, game_callback):
        super().__init__(sound_manager)
        self.settings_callback = settings_callback
        self.game_callback = game_callback
        self._bg_key = "MAIN_BG_RUS" if config.current_language == "russian" else "MAIN_BG"
        self._create_buttons()

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
        self._bg_key = "MAIN_BG_RUS" if config.current_language == "russian" else "MAIN_BG"
        super().update_textures()
        self._create_buttons()

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
