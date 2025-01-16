from Game.ui.menu import Menu
from Game.ui.button import Button
from Game.utils import load_image
from Game.config import WIDTH, HEIGHT, BUTTON_SPACING, SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START, BACK_BUTTON_X, BACK_BUTTON_Y


class SettingsMenu(Menu):
    def __init__(self, sound_manager, main_menu_callback):
        super().__init__(sound_manager)
        self.main_menu_callback = main_menu_callback
        self.add_button(Button(load_image("Settings_menu/Buttons/settings_game_before.jpg"),
                               load_image("Settings_menu/Buttons/settings_game_after.jpg"),
                               (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START),
                               self.settings_game_menu))
        self.add_button(Button(load_image("Settings_menu/Buttons/settings_graphics_before.jpg"),
                               load_image("Settings_menu/Buttons/settings_graphics_after.jpg"),
                               (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START + BUTTON_SPACING),
                               self.settings_graphics_menu))
        self.add_button(Button(load_image("Settings_menu/Buttons/settings_language_before.jpg"),
                               load_image("Settings_menu/Buttons/settings_language_after.jpg"),
                               (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START + 2 * BUTTON_SPACING),
                               self.settings_language_menu))
        self.add_button(Button(load_image("Settings_menu/Buttons/settings_back_before.jpg"),
                               load_image("Settings_menu/Buttons/settings_back_after.jpg"),
                               (BACK_BUTTON_X, BACK_BUTTON_Y),
                               self.open_main_menu))

    @staticmethod
    def settings_game_menu():
        print("Game settings menu")

    @staticmethod
    def settings_graphics_menu():
        print("Graphics settings menu")

    @staticmethod
    def settings_language_menu():
        print("Language settings menu")

    def open_main_menu(self):
        self.main_menu_callback()

    def draw(self, surface, mouse_pos):
        surface.blit(load_image("Settings_menu/Backgrounds/Settings_Background.jpg"), (0, 0))
        super().draw(surface, mouse_pos)
