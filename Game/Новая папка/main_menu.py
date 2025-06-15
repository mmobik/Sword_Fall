import pygame
import sys
from .menu import Menu
from .button import Button
from Game.core import load_image
from Game.core import HEIGHT, BUTTON_SPACING, MENU_BUTTON_X


class MainMenu(Menu):
    def __init__(self, sound_manager, settings_menu_callback, game_callback):
        super().__init__(sound_manager)
        self.settings_menu_callback = settings_menu_callback
        self.game_callback = game_callback
        self.add_button(Button(load_image("Images/Main_menu/Buttons/Start/Start_before.jpg"),
                               load_image("Images/Main_menu/Buttons/Start/Start_after.jpg"),
                               (MENU_BUTTON_X, HEIGHT // 2 - BUTTON_SPACING),
                               self.start_new_game))
        self.add_button(Button(load_image("Images/Main_menu/Buttons/Settings/Settings_before.jpg"),
                               load_image("Images/Main_menu/Buttons/Settings/Settings_after.jpg"),
                               (MENU_BUTTON_X, HEIGHT // 2),
                               self.open_settings_menu))
        self.add_button(Button(load_image("Images/Main_menu/Buttons/Exit/Exit_before.jpg"),
                               load_image("Images/Main_menu/Buttons/Exit/Exit_after.jpg"),
                               (MENU_BUTTON_X, HEIGHT // 2 + BUTTON_SPACING),
                               self.exit_game))

    def start_new_game(self):
        self.game_callback("new_game")

    def open_settings_menu(self):
        self.settings_menu_callback()

    def exit_game(self):
        pygame.quit()
        sys.exit()

    def draw(self, surface, mouse_pos):
        surface.blit(load_image("Images/Main_menu/Backgrounds/Background.jpg"), (0, 0))
        super().draw(surface, mouse_pos)
