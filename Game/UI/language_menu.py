import pygame
from .menu import Menu
from .button import Button
from Game.core import load_image
from Game.core import WIDTH, HEIGHT
from Game.core import BACK_BUTTON_X, BACK_BUTTON_Y


class LanguageMenu(Menu):
    def __init__(self, sound_manager, back_callback, language_callback):
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self.language_callback = language_callback

        # Позиции кнопок (центрируем по горизонтали)
        button_width = 586
        button_height = 86
        button_x = (WIDTH - button_width) // 2

        # Кнопка английского языка
        self.add_button(Button(
            load_image("Images/Settings_menu/eng_language_before.jpg"),
            load_image("Images/Settings_menu/eng_language_after.jpg"),
            (button_x, HEIGHT // 2 - 100),
            lambda: self.select_language("english")
        ))

        # Кнопка русского языка
        self.add_button(Button(
            load_image("Images/Settings_menu/rus_language_before.jpg"),
            load_image("Images/Settings_menu/rus_language_after.jpg"),
            (button_x, HEIGHT // 2 + 50),
            lambda: self.select_language("russian")
        ))

        # Кнопка назад
        self.add_button(Button(
            load_image("Images/Settings_menu/Settings_back_before.jpg"),
            load_image("Images/Settings_menu/Settings_back_after.jpg"),
            (BACK_BUTTON_X, BACK_BUTTON_Y),
            self.back_callback
        ))

    def select_language(self, lang):
        self.language_callback(lang)
        self.back_callback()

    def draw(self, surface, mouse_pos):
        surface.blit(load_image("Images/Main_menu/Backgrounds/Settings_Background.jpg"), (0, 0))
        super().draw(surface, mouse_pos)
