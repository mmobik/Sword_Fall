#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы меню
"""

import pygame
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

from core.config import config
from core.sound_manager import SoundManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu

def test_menu_system():
    """Тестирует систему меню"""
    pygame.init()
    pygame.mixer.init()
    
    # Создаем экран
    screen = pygame.display.set_mode(config.SCREEN_SIZE)
    pygame.display.set_caption("Menu Test")
    
    # Создаем менеджер звуков
    sound_manager = SoundManager()
    
    # Создаем меню
    current_menu = "main"
    main_menu = MainMenu(sound_manager, lambda: set_menu("settings"), lambda x: print(f"Game: {x}"))
    settings_menu = SettingsMenu(sound_manager, lambda: set_menu("main"), lambda: set_menu("language"))
    language_menu = LanguageMenu(sound_manager, lambda: set_menu("settings"), lambda lang: change_language(lang))
    
    def set_menu(menu_name):
        nonlocal current_menu
        current_menu = menu_name
        print(f"Переключение на меню: {menu_name}")
    
    def change_language(lang):
        print(f"Смена языка на: {lang}")
        config.set_language(lang)
        # Обновляем текстуры
        main_menu.update_textures()
        settings_menu.update_textures()
        language_menu.update_textures()
        set_menu("settings")
    
    # Главный цикл
    clock = pygame.time.Clock()
    running = True
    
    print("Тест меню запущен!")
    print("Управление:")
    print("- Нажмите на кнопки для навигации")
    print("- Смените язык в языковом меню")
    print("- ESC для выхода")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Передаем события текущему меню
            mouse_pos = pygame.mouse.get_pos()
            if current_menu == "main":
                main_menu.handle_event(event, mouse_pos)
            elif current_menu == "settings":
                settings_menu.handle_event(event, mouse_pos)
            elif current_menu == "language":
                language_menu.handle_event(event, mouse_pos)
        
        # Отрисовка
        screen.fill((0, 0, 0))
        
        # Рисуем текущее меню
        mouse_pos = pygame.mouse.get_pos()
        if current_menu == "main":
            main_menu.draw(screen, mouse_pos)
        elif current_menu == "settings":
            settings_menu.draw(screen, mouse_pos)
        elif current_menu == "language":
            language_menu.draw(screen, mouse_pos)
        
        pygame.display.flip()
    
    pygame.quit()
    print("Тест завершен!")

if __name__ == "__main__":
    test_menu_system() 