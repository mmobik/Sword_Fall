from .menu import Menu
from .button import Button
from Game.core import load_image
from Game.core import BUTTON_SPACING, SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START, BACK_BUTTON_X, BACK_BUTTON_Y


class SettingsMenu(Menu):
    def __init__(self, sound_manager, main_menu_callback):
        super().__init__(sound_manager)
        self.main_menu_callback = main_menu_callback
        self.add_button(Button(load_image("Images/Settings_menu/Settings_game_before.jpg"),
                               load_image("Images/Settings_menu/Settings_game_after.jpg"),
                               (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START),
                               self.settings_game_menu))
        self.add_button(Button(load_image("Images/Settings_menu/Settings_graphics_before.jpg"),
                               load_image("Images/Settings_menu/Settings_graphics_after.jpg"),
                               (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START + BUTTON_SPACING),
                               self.settings_graphics_menu))
        self.add_button(Button(load_image("Images/Settings_menu/Settings_language_before.jpg"),
                               load_image("Images/Settings_menu/Settings_language_after.jpg"),
                               (SETTINGS_BUTTON_X, SETTINGS_BUTTON_Y_START + 2 * BUTTON_SPACING),
                               self.settings_language_menu))
        self.add_button(Button(load_image("Images/Settings_menu/Settings_back_before.jpg"),
                               load_image("Images/Settings_menu/Settings_back_after.jpg"),
                               (BACK_BUTTON_X, BACK_BUTTON_Y),
                               self.open_main_menu))

    def settings_game_menu(self):
        print("Game settings menu")

    def settings_graphics_menu(self):
        print("Graphics settings menu")

    def settings_language_menu(self):
        print("Language settings menu")

    def open_main_menu(self):
        self.main_menu_callback()

    def draw(self, surface, mouse_pos):
        surface.blit(load_image("Images/Main_menu/Backgrounds/Settings_Background.jpg"), (0, 0))
        super().draw(surface, mouse_pos)
