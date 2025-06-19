import pygame
from core.config import config

class MenuHandler:
    def __init__(self, game):
        self.game = game

    def show_main_menu(self):
        self.game.game_state_manager.change_state("main_menu", self.game.main_menu)
        self.game.sound_manager.play_music("Dark_fantasm.mp3")

    def show_settings(self):
        self.game.game_state_manager.change_state("settings_menu", self.game.settings_menu)

    def show_language(self):
        self.game.game_state_manager.change_state("language_menu", self.game.language_menu)

    def show_music_settings(self):
        self.game.game_state_manager.change_state("music_settings_menu", self.game.music_settings_menu)

    def change_language(self, lang: str):
        if config.current_language == lang:
            return
        current_mouse_pos = pygame.mouse.get_pos()
        config.set_language(lang)
        if config.DEBUG_MODE:
            print(f"Язык изменен на: {lang}")
        if hasattr(self.game.main_menu, 'update_textures'):
            self.game.main_menu.update_textures()
        if hasattr(self.game.settings_menu, 'update_textures'):
            self.game.settings_menu.update_textures()
        if hasattr(self.game.language_menu, 'update_textures'):
            self.game.language_menu.update_textures()
        if hasattr(self.game.music_settings_menu, 'update_textures'):
            self.game.music_settings_menu.update_textures()
        self.show_settings()
        if self.game.game_state_manager.current_menu:
            self.game.game_state_manager.current_menu.draw(self.game.screen, current_mouse_pos)
            pygame.display.flip()

    def start_game(self, state: str):
        if state == "new_game":
            self.game.waiting_for_first_update = True
            self.game.wait_for_key_release = False
            self.game.game_state_manager.change_state(state, None)
            self.game.sound_manager.play_music("Central Hall.mp3")
        else:
            self.game.game_state_manager.change_state(state) 