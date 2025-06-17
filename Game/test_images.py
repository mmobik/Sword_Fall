#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки изображений
"""

import pygame
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

from core.config import config
from core.utils import load_image

def test_image_loading():
    """Тестирует загрузку изображений"""
    pygame.init()
    
    print("Тестирование загрузки изображений...")
    
    # Тестируем загрузку фонов
    print("\n=== Тестирование фонов ===")
    bg_keys = ["MAIN_BG", "MAIN_BG_RUS", "SETTINGS_BG", "LANGUAGE_BG"]
    for key in bg_keys:
        path = config.MENU_IMAGES.get(key)
        if path:
            print(f"{key}: {path}")
            img = load_image(path)
            if img:
                print(f"  ✓ Загружено успешно: {img.get_size()}")
            else:
                print(f"  ✗ Ошибка загрузки")
        else:
            print(f"{key}: Путь не найден")
    
    # Тестируем загрузку кнопок
    print("\n=== Тестирование кнопок ===")
    button_keys = ["START_BTN", "SETTINGS_BTN", "EXIT_BTN", "LANGUAGE_SETTINGS_BTN", "BACK_BTN"]
    
    for key in button_keys:
        print(f"\n{key}:")
        # Английская версия
        config.current_language = "english"
        before_path = config.get_image(key, "before")
        after_path = config.get_image(key, "after")
        
        if before_path:
            before_img = load_image(before_path)
            if before_img:
                print(f"  EN before: ✓ {before_img.get_size()}")
            else:
                print(f"  EN before: ✗ Ошибка загрузки")
        else:
            print(f"  EN before: Путь не найден")
            
        if after_path:
            after_img = load_image(after_path)
            if after_img:
                print(f"  EN after: ✓ {after_img.get_size()}")
            else:
                print(f"  EN after: ✗ Ошибка загрузки")
        else:
            print(f"  EN after: Путь не найден")
        
        # Русская версия
        config.current_language = "russian"
        before_path_rus = config.get_image(key, "before")
        after_path_rus = config.get_image(key, "after")
        
        if before_path_rus:
            before_img_rus = load_image(before_path_rus)
            if before_img_rus:
                print(f"  RU before: ✓ {before_img_rus.get_size()}")
            else:
                print(f"  RU before: ✗ Ошибка загрузки")
        else:
            print(f"  RU before: Путь не найден")
            
        if after_path_rus:
            after_img_rus = load_image(after_path_rus)
            if after_img_rus:
                print(f"  RU after: ✓ {after_img_rus.get_size()}")
            else:
                print(f"  RU after: ✗ Ошибка загрузки")
        else:
            print(f"  RU after: Путь не найден")
    
    pygame.quit()
    print("\nТестирование завершено!")

if __name__ == "__main__":
    test_image_loading() 