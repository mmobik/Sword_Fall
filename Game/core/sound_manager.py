"""
Модуль управления звуком.

Содержит класс SoundManager для управления музыкой, звуковыми эффектами
и настройками громкости с поддержкой сохранения настроек.
"""

import pygame
import os
import json
from core.config import config
from core.pathutils import resource_path


class SoundManager:
    """
    Класс для управления звуком в игре.
    
    Обеспечивает загрузку и воспроизведение музыки и звуковых эффектов,
    управление громкостью и сохранение настроек пользователя.
    """

    def __init__(self):
        """Инициализация менеджера звука."""
        # Ссылка на объект Game для доступа к глобальному состоянию
        self.game = None
        
        # Инициализация громкости
        self.music_volume = 0.5
        self.sound_volume = 0.7
        self.music_volumes = {}  # индивидуальные громкости для треков
        
        # Загружаем сохраненные настройки
        self.load_settings()

        # Проверяем инициализацию микшера
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # Загружаем звуки с проверкой существования файлов
        self.sounds = {
            'button_click': self._load_sound("Button.mp3"),
            'steps': self._load_sound("steps.mp3"),  # Добавлен звук шагов
        }
        self.current_music = None
        
        # Синхронизируем громкость шага с музыкой при инициализации
        steps = self.sounds.get('steps')
        if steps:
            steps.set_volume(self.music_volumes.get('central_hall', 1.0))

    def load_settings(self):
        """Загружает настройки звука из файла."""
        try:
            dir_path = "userdata"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            sound_path = os.path.join(dir_path, "sound_settings.json")
            
            if os.path.exists(sound_path):
                with open(sound_path, "r") as f:
                    settings = json.load(f)
                    self.music_volume = settings.get("music_volume", 0.5)
                    self.sound_volume = settings.get("sound_volume", 0.7)
                    self.music_volumes = settings.get("music_volumes", {})
            
            # Явно применяем громкость музыки и звуков после загрузки настроек
            pygame.mixer.music.set_volume(self.music_volume)
            for name, sound in self.sounds.items():
                if name == 'steps':
                    sound.set_volume(self.music_volume)
                else:
                    sound.set_volume(self.sound_volume)
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка загрузки настроек звука: {e}")

    def save_settings(self):
        """Сохраняет настройки звука в файл."""
        try:
            dir_path = "userdata"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            sound_path = os.path.join(dir_path, "sound_settings.json")
            settings = {
                "music_volume": self.music_volume,
                "sound_volume": self.sound_volume,
                "music_volumes": self.music_volumes
            }
            with open(sound_path, "w") as f:
                json.dump(settings, f)
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка сохранения настроек звука: {e}")

    def _load_sound(self, filename: str) -> pygame.mixer.Sound:
        """
        Загружает звуковой файл из папки assets/sounds/game_sounds/.
        
        Args:
            filename: Имя звукового файла.
            
        Returns:
            Загруженный звук или пустой звук в случае ошибки.
        """
        # Формируем правильный путь
        full_path = resource_path(os.path.join("Game", "assets", "sounds", "game_sounds", filename))

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
        """
        Воспроизводит музыку из assets/sounds/soundtracks/.
        
        Args:
            music_name: Имя музыкального файла.
            loop: Зацикливать ли музыку.
        """
        # Формируем полный путь к музыке
        full_path = resource_path(os.path.join("Game", "assets", "sounds", "soundtracks", music_name))
        
        # Определяем индивидуальную громкость для этого трека
        key = os.path.splitext(music_name)[0].lower()
        volume = self.music_volumes.get(key, self.music_volume)
        
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
        """
        Воспроизводит заранее загруженный звук.
        
        Args:
            sound_name: Имя звука для воспроизведения.
        """
        if sound_name in self.sounds:
            # Для шага используем общую громкость музыки
            if sound_name == 'steps':
                self.sounds['steps'].set_volume(self.music_volume)
                if self.music_volume == 0:
                    return  # Не проигрывать шаги при нулевой громкости
            self.sounds[sound_name].play()

    def stop_music(self) -> None:
        """Останавливает музыку."""
        pygame.mixer.music.stop()
        self.current_music = None

    def set_music_volume(self, volume: float) -> None:
        """
        Устанавливает громкость музыки (0.0-1.0) и синхронизирует с шагами.
        
        Args:
            volume: Уровень громкости от 0.0 до 1.0.
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        
        # Синхронизируем громкость шагов с общей громкостью музыки
        steps = self.sounds.get('steps')
        if steps:
            steps.set_volume(self.music_volume)
        
        # Сохраняем настройки при изменении
        self.save_settings()

    def set_sound_volume(self, volume: float) -> None:
        """
        Устанавливает громкость звуков (0.0-1.0) и синхронизирует с музыкой.
        
        Args:
            volume: Уровень громкости от 0.0 до 1.0.
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        
        for name, sound in self.sounds.items():
            # steps всегда равен громкости музыки
            if name == 'steps':
                sound.set_volume(self.music_volume)
            else:
                sound.set_volume(self.sound_volume)
                
        # Сохраняем настройки при изменении
        self.save_settings()

    def set_track_volume(self, track_type: str, value: float) -> None:
        """
        Устанавливает громкость для конкретного трека.
        
        Args:
            track_type: Тип трека (например, 'central_hall').
            value: Уровень громкости от 0.0 до 1.0.
        """
        # Приводим к нижнему регистру для ключа
        key = track_type.lower()
        self.music_volumes[key] = value
        
        # Если сейчас играет этот трек — применяем громкость
        if self.current_music:
            current_base = os.path.splitext(
                os.path.basename(self.current_music))[0].lower()
            if current_base == key:
                pygame.mixer.music.set_volume(value)
                self.music_volume = value
                
        # Звук ходьбы всегда синхронизирован с общей громкостью музыки
        # Никаких дополнительных действий не требуется
        
        self.save_settings()

    def get_track_volume(self, track_type: str) -> float:
        """
        Получает громкость для конкретного трека.
        
        Args:
            track_type: Тип трека.
            
        Returns:
            Уровень громкости трека.
        """
        key = track_type.lower()
        return self.music_volumes.get(key, 1.0)
