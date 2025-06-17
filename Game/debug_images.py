#!/usr/bin/env python3
"""
Простой скрипт для отладки изображений
"""

import pygame
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

from core.config import config

def debug_images():
    """Отладочная информация об изображениях"""
    print("=== Отладка изображений ===")
    
    # Проверяем текущий язык
    print(f"Текущий язык: {config.current_language}")
    
    # Проверяем пути к фонам
    print("\n--- Фоны ---")
    for key in ["MAIN_BG", "MAIN_BG_RUS", "SETTINGS_BG"]:
        path = config.MENU_IMAGES.get(key)
        print(f"{key}: {path}")
        if path and os.path.exists(path):
            print(f"  ✓ Файл существует")
        else:
            print(f"  ✗ Файл не найден")
    
    # Проверяем пути к кнопкам
    print("\n--- Кнопки ---")
    test_buttons = ["START_BTN", "SETTINGS_BTN", "LANGUAGE_SETTINGS_BTN"]
    
    for lang in ["english", "russian"]:
        print(f"\nЯзык: {lang}")
        config.current_language = lang
        
        for btn_key in test_buttons:
            before_path = config.get_image(btn_key, "before")
            after_path = config.get_image(btn_key, "after")
            
            print(f"  {btn_key}:")
            print(f"    before: {before_path}")
            if isinstance(before_path, str) and os.path.exists(before_path):
                print(f"      ✓ Существует")
            else:
                print(f"      ✗ Не найден")
                
            print(f"    after: {after_path}")
            if isinstance(after_path, str) and os.path.exists(after_path):
                print(f"      ✓ Существует")
            else:
                print(f"      ✗ Не найден")

if __name__ == "__main__":
    debug_images() 