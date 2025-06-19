"""
Модуль обработчика меню.

Содержит класс MenuHandler для управления переходами между различными
меню игры и изменениями языка интерфейса.
"""

import pygame
from core.config import config


class MenuHandler:
    """
    Класс для обработки меню игры.
    
    Управляет переходами между различными меню, изменением языка
    и запуском игрового процесса.
    """

    def __init__(self, game):
        """
        Инициализация обработчика меню.
        
        Args:
            game: Ссылка на основной объект игры.
        """
        self.game = game

    def show_main_menu(self):
        """Показывает главное меню."""
        self.game.game_state_manager.change_state("main_menu", self.game.main_menu)
        self.game.sound_manager.play_music("Dark_fantasm.mp3")

    def show_settings(self):
        """Показывает меню настроек."""
        self.game.game_state_manager.change_state("settings_menu",
                                                  self.game.settings_menu)

    def show_language(self):
        """Показывает меню выбора языка."""
        self.game.game_state_manager.change_state("language_menu",
                                                  self.game.language_menu)

    def show_music_settings(self):
        """Показывает меню настроек музыки."""
        self.game.game_state_manager.change_state("music_settings_menu",
                                                  self.game.music_settings_menu)

    def change_language(self, lang: str):
        """
        Изменяет язык интерфейса.
        
        Args:
            lang: Новый язык интерфейса.
        """
        if config.current_language == lang:
            return

        current_mouse_pos = pygame.mouse.get_pos()
        config.set_language(lang)

        if config.DEBUG_MODE:
            print(f"Язык изменен на: {lang}")

        # Обновляем текстуры всех меню
        for menu_name in ['main_menu', 'settings_menu', 'language_menu',
                          'music_settings_menu']:
            menu = getattr(self.game, menu_name, None)
            if menu and hasattr(menu, 'update_textures'):
                menu.update_textures()

        self.show_settings()

        if self.game.game_state_manager.current_menu:
            self.game.game_state_manager.current_menu.draw(
                self.game.screen, current_mouse_pos)
            pygame.display.flip()

    def start_game(self, state: str):
        """
        Запускает игру с указанным состоянием.
        
        Args:
            state: Состояние для запуска игры.
        """
        if state == "new_game":
            self.game.waiting_for_first_update = True
            self.game.wait_for_key_release = False
            self.game.game_state_manager.change_state(state, None)
            self.game.sound_manager.play_music("Central Hall.mp3")
        else:
            self.game.game_state_manager.change_state(state)
