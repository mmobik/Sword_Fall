from .menu import Menu
from .button import Button
from Game.core import load_image
from Game.core import BUTTON_SPACING, SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START, BACK_BUTTON_X, BACK_BUTTON_Y


class SettingsMenu(Menu):
    def __init__(self, sound_manager, back_callback, language_callback):
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self.language_callback = language_callback

        self.add_button(Button(
            load_image("Images/Settings_menu/Settings_game_before.jpg"),
            load_image("Images/Settings_menu/Settings_game_after.jpg"),
            (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START),
            self.settings_game_menu
        ))

        self.add_button(Button(
            load_image("Images/Settings_menu/Settings_graphics_before.jpg"),
            load_image("Images/Settings_menu/Settings_graphics_after.jpg"),
            (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START + BUTTON_SPACING),
            self.settings_graphics_menu
        ))

        self.add_button(Button(
            load_image("Images/Settings_menu/Settings_language_before.jpg"),
            load_image("Images/Settings_menu/Settings_language_after.jpg"),
            (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START + 2 * BUTTON_SPACING),
            self.open_language_menu
        ))

        self.add_button(Button(
            load_image("Images/Settings_menu/Settings_back_before.jpg"),
            load_image("Images/Settings_menu/Settings_back_after.jpg"),
            (BACK_BUTTON_X, BACK_BUTTON_Y),
            self.back_callback
        ))

    def settings_game_menu(self):
        print("Game settings menu")

    def settings_graphics_menu(self):
        print("Graphics settings menu")

    def open_language_menu(self):
        self.language_callback()

    def draw(self, surface, mouse_pos):
        surface.blit(load_image("Images/Main_menu/Backgrounds/Settings_Background.jpg"), (0, 0))
        super().draw(surface, mouse_pos)