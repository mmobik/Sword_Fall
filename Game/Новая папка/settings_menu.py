from Game.core.config import config
from Game.core.utils import load_image
from .menu import Menu
from .button import Button


class SettingsMenu(Menu):
    def __init__(self, sound_manager, back_callback, language_callback):
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self.language_callback = language_callback

        self.add_button(Button(
            load_image(config.get_image("GAME_SETTINGS_BTN", "before")),
            load_image(config.get_image("GAME_SETTINGS_BTN", "after")),
            (config.SETTINGS_BUTTON_X, config.SETTINGS_BUTTON_Y_START),
            self.settings_game_menu
        ))

        self.add_button(Button(
            load_image(config.get_image("GRAPHICS_SETTINGS_BTN", "before")),
            load_image(config.get_image("GRAPHICS_SETTINGS_BTN", "after")),
            (config.SETTINGS_BUTTON_X, config.SETTINGS_BUTTON_Y_START + config.BUTTON_SPACING),
            self.settings_graphics_menu
        ))

        self.add_button(Button(
            load_image(config.get_image("LANGUAGE_SETTINGS_BTN", "before")),
            load_image(config.get_image("LANGUAGE_SETTINGS_BTN", "after")),
            (config.SETTINGS_BUTTON_X, config.SETTINGS_BUTTON_Y_START + 2 * config.BUTTON_SPACING),
            self.open_language_menu
        ))

        self.add_button(Button(
            load_image(config.get_image("BACK_BTN", "before")),
            load_image(config.get_image("BACK_BTN", "after")),
            (config.BACK_BUTTON_X, config.BACK_BUTTON_Y),
            self.back_callback
        ))

    def draw(self, surface, mouse_pos):
        surface.blit(load_image(config.MENU_IMAGES["SETTINGS_BG"]), (0, 0))
        super().draw(surface, mouse_pos)

    def settings_game_menu(self):
        """Обработчик кнопки настроек игры"""
        print("Game settings menu opened")
        # Здесь будет логика открытия меню настроек игры

    def settings_graphics_menu(self):
        """Обработчик кнопки графических настроек"""
        print("Graphics settings menu opened")
        # Здесь будет логика открытия графических настроек

    def open_language_menu(self):
        """Обработчик кнопки языковых настроек"""
        print("Opening language menu")
        self.language_callback()  # Переходим в меню языка
