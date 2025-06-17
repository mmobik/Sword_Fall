import pygame
from Game.core.config import config
from Game.core.utils import load_image
import sys
from .menu import Menu
from .button import Button


class MainMenu(Menu):
    def __init__(self, sound_manager, settings_callback, game_callback):
        super().__init__(sound_manager)
        self.settings_callback = settings_callback
        self.game_callback = game_callback

        self.add_button(Button(
            load_image(config.get_image("START_BTN", "before")),
            load_image(config.get_image("START_BTN", "after")),
            (config.MENU_BUTTON_X, config.HEIGHT // 2 - config.BUTTON_SPACING),
            self.start_new_game
        ))

        self.add_button(Button(
            load_image(config.get_image("SETTINGS_BTN", "before")),
            load_image(config.get_image("SETTINGS_BTN", "after")),
            (config.MENU_BUTTON_X, config.HEIGHT // 2),
            self.open_settings_menu
        ))

        self.add_button(Button(
            load_image(config.get_image("EXIT_BTN", "before")),
            load_image(config.get_image("EXIT_BTN", "after")),
            (config.MENU_BUTTON_X, config.HEIGHT // 2 + config.BUTTON_SPACING),
            self.exit_game
        ))

    def draw(self, surface, mouse_pos):
        bg_key = "MAIN_BG_RUS" if config.current_language == "russian" else "MAIN_BG"
        surface.blit(load_image(config.MENU_IMAGES[bg_key]), (0, 0))
        super().draw(surface, mouse_pos)

    def start_new_game(self):
        self.sound_manager.play_music("house.mp3")  # Используем существующий трек
        self.game_callback("new_game")

    def open_settings_menu(self):
        self.settings_callback()

    def exit_game(self):
        pygame.quit()
        sys.exit()
