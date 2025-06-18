import pygame
import os
import json
from core.config import config


class SoundManager:
    def __init__(self):
        # Инициализация громкости
        self.music_volume = 0.5
        self.sound_volume = 0.7
        
        # Загружаем сохраненные настройки
        self.load_settings()

        # Проверяем инициализацию микшера
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # Загружаем звуки с проверкой существования файлов
        self.sounds = {
            'button_click': self._load_sound("button.mp3"),
            # Убираем StartGame.mp3, так как его нет в ваших файлах
        }
        self.current_music = None

    def load_settings(self):
        """Загружает настройки звука из файла"""
        try:
            if os.path.exists("sound_settings.json"):
                with open("sound_settings.json", "r") as f:
                    settings = json.load(f)
                    self.music_volume = settings.get("music_volume", 0.5)
                    self.sound_volume = settings.get("sound_volume", 0.7)
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка загрузки настроек звука: {e}")

    def save_settings(self):
        """Сохраняет настройки звука в файл"""
        try:
            settings = {
                "music_volume": self.music_volume,
                "sound_volume": self.sound_volume
            }
            with open("sound_settings.json", "w") as f:
                json.dump(settings, f)
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка сохранения настроек звука: {e}")

    def _load_sound(self, filename: str) -> pygame.mixer.Sound:
        """Загружает звуковой файл из папки assets/sounds/game_sounds/"""
        # Формируем правильный путь
        full_path = os.path.join("assets", "sounds", "game_sounds", filename)

        try:
            sound = pygame.mixer.Sound(full_path)
            sound.set_volume(self.sound_volume)
            return sound
        except pygame.error as e:
            if config.DEBUG_MODE:
                print(f"[SoundManager] Ошибка загрузки звука {full_path}: {e}")
            # Создаем пустой звук, чтобы избежать ошибок
            silent_sound = pygame.mixer.Sound(buffer=bytearray(0))
            silent_sound.set_volume(0)
            return silent_sound

    def play_music(self, music_name: str, loop: bool = True) -> None:
        """Воспроизводит музыку из assets/sounds/soundtracks/"""
        # Формируем полный путь к музыке
        full_path = os.path.join("assets", "sounds", "soundtracks", music_name)

        try:
            if self.current_music != full_path:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = full_path
        except pygame.error as e:
            if config.DEBUG_MODE:
                print(f"[SoundManager] Ошибка загрузки музыки {full_path}: {e}")
            self.current_music = None

    def play_sound(self, sound_name: str) -> None:
        """Воспроизводит заранее загруженный звук"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def stop_music(self) -> None:
        """Останавливает музыку"""
        pygame.mixer.music.stop()
        self.current_music = None

    def set_music_volume(self, volume: float) -> None:
        """Устанавливает громкость музыки (0.0-1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        # Сохраняем настройки при изменении
        self.save_settings()

    def set_sound_volume(self, volume: float) -> None:
        """Устанавливает громкость звуков (0.0-1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
        # Сохраняем настройки при изменении
        self.save_settings()
