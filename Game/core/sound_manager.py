import pygame
import os
from core.config import config


class SoundManager:
    def __init__(self):
        # Инициализация громкости
        self.music_volume = 0.5
        self.sound_volume = 0.7

        # Проверяем инициализацию микшера
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # Загружаем звуки с проверкой существования файлов
        self.sounds = {
            'button_click': self._load_sound("button.mp3"),
            # Убираем StartGame.mp3, так как его нет в ваших файлах
        }
        self.current_music = None

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

    def set_sound_volume(self, volume: float) -> None:
        """Устанавливает громкость звуков (0.0-1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
