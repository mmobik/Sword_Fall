"""
Тест для проверки сохранения настроек звука.
"""

import json
import os
from core.sound_manager import SoundManager
from core.config import config

def test_sound_settings():
    """Тестирует сохранение и загрузку настроек звука."""
    print("=== Тест настроек звука ===")
    
    # Создаем временный SoundManager
    sound_manager = SoundManager()
    
    # Проверяем текущие настройки
    print(f"Начальные настройки:")
    print(f"  music_volume: {sound_manager.music_volume}")
    print(f"  sound_volume: {sound_manager.sound_volume}")
    print(f"  music_volumes: {sound_manager.music_volumes}")
    
    # Изменяем настройки
    print("\nИзменяем настройки...")
    sound_manager.set_music_volume(0.8)
    sound_manager.set_sound_volume(0.6)
    sound_manager.set_track_volume("dark_fantasm", 0.7)
    sound_manager.set_track_volume("central_hall", 0.9)
    
    print(f"Новые настройки:")
    print(f"  music_volume: {sound_manager.music_volume}")
    print(f"  sound_volume: {sound_manager.sound_volume}")
    print(f"  music_volumes: {sound_manager.music_volumes}")
    
    # Проверяем, что файл создался
    settings_file = "userdata/sound_settings.json"
    if os.path.exists(settings_file):
        print(f"\nФайл настроек создан: {settings_file}")
        
        # Читаем файл и проверяем содержимое
        with open(settings_file, 'r') as f:
            saved_settings = json.load(f)
        
        print(f"Сохраненные настройки:")
        print(f"  music_volume: {saved_settings.get('music_volume')}")
        print(f"  sound_volume: {saved_settings.get('sound_volume')}")
        print(f"  music_volumes: {saved_settings.get('music_volumes')}")
        
        # Проверяем соответствие
        if (saved_settings.get('music_volume') == sound_manager.music_volume and
            saved_settings.get('sound_volume') == sound_manager.sound_volume and
            saved_settings.get('music_volumes') == sound_manager.music_volumes):
            print("✅ Настройки сохранены корректно!")
        else:
            print("❌ Ошибка: настройки не соответствуют сохраненным!")
    else:
        print(f"❌ Ошибка: файл настроек не создан!")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_sound_settings() 