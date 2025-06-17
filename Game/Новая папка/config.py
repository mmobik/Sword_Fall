"""
Конфигурационные параметры игры.
Все настройки доступны через глобальный экземпляр config.
"""

import pygame
from typing import Dict, Tuple, Union, List


class GameConfig:
    def __init__(self):
        # === Языковые настройки ===
        self.current_language = "english"
        # === Уровни ===
        self.LEVELS = {
            "first": {
                "background": "assets/images/game/backgrounds/level/first_level.png",
                "map": "assets/images/game/backgrounds/level/second_level.tmx"
            },
            "second": {
                "background": "assets/images/game/backgrounds/level/second_level.png",
                "map": "assets/images/game/backgrounds/level/second_level.tmx"
            }
        }

        # === Настройки экрана ===
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.GAME_NAME = "SwordFall"
        self.FPS = 144
        self.TARGET_FPS = 60
        self.SCREEN_SIZE = (self.WIDTH, self.HEIGHT)

        # === Настройки интерфейса ===
        self.BUTTON_SPACING = 125
        self.MENU_BUTTON_X = self.WIDTH // 3
        self.SETTINGS_BUTTON_X = self.WIDTH // 2 - 200
        self.SETTINGS_BUTTON_Y_START = self.HEIGHT // 2 - 200
        self.BACK_BUTTON_X = self.WIDTH // 2 - 200
        self.BACK_BUTTON_Y = self.HEIGHT - 300
        self.FADE_DURATION = 0.5  # Длительность перехода между меню

        # === Пути к игровым ресурсам ===
        self.ASSETS = {
            "ICON": "assets/images/icons/icon_1.jpg",
            "BACKGROUND": "assets/images/game/backgrounds/locations/bedroom.jpeg",
            "IDLE_SHEET": "assets/sprites/Idle.png",
            "RUN_SHEET": "assets/sprites/Run.png",
            "SOUNDTRACK": "assets/sounds/soundtracks/Dark_fantasm.mp3"
        }

        # === Цветовая палитра ===
        self.COLORS = {
            "DARK_BLUE": (0, 33, 55),
            "BLUE": (46, 68, 116),
            "WHITE": (255, 255, 255),
            "BLACK": (0, 0, 0),
            "RED": (255, 0, 0),
            "GREEN": (0, 255, 0)
        }

        # === Параметры анимации ===
        self.FRAME_SIZE = (128, 64)  # Ширина, высота кадра
        self.DEFAULT_ANIMATION_SPEED = 0.15  # Скорость смены кадров
        self.NO_ANIMATION = float('inf')  # Значение для отключения анимации

        self.ANIMATION_FRAMES = {
            "IDLE": [
                (0, 0), (128, 0), (0, 64), (128, 64),
                (0, 128), (128, 128), (0, 192), (128, 192)
            ],
            "RUN": [
                (0, 0), (128, 0), (0, 64), (128, 64),
                (0, 128), (128, 128), (0, 192), (128, 192)
            ]
        }

        # === Параметры уровня ===
        self.DEFAULT_LEVEL_WIDTH = self.WIDTH * 4
        self.DEFAULT_LEVEL_HEIGHT = self.HEIGHT * 4
        self.TILE_SIZE = 100  # Размер клетки уровня

        # === Параметры игрока ===
        self.PLAYER_SPEED = 300
        self.PLAYER_START_X = self.DEFAULT_LEVEL_WIDTH // 2
        self.PLAYER_START_Y = self.DEFAULT_LEVEL_HEIGHT // 2
        self.PLAYER_HITBOX_OFFSET = (-30, -20)  # Смещение хитбокса

        # === Изображения для меню ===
        self.MENU_IMAGES = {
            # Главное меню
            "MAIN_BG": "assets/images/menu/main/backgrounds/dark_prince.jpg",
            "MAIN_BG_RUS": "assets/images/menu/main/backgrounds/dark_prince.jpg",

            # Кнопки главного меню (EN)
            "START_BTN": {
                "before": "assets/images/menu/main/eng/start/before.jpg",
                "after": "assets/images/menu/main/eng/start/after.jpg"
            },
            "SETTINGS_BTN": {
                "before": "assets/images/menu/main/eng/settings/before.jpg",
                "after": "assets/images/menu/main/eng/settings/after.jpg"
            },
            "EXIT_BTN": {
                "before": "assets/images/menu/main/eng/exit/before.jpg",
                "after": "assets/images/menu/main/eng/exit/after.jpg"
            },

            # Кнопки главного меню (RU)
            "START_BTN_RUS": {
                "before": "assets/images/menu/main/rus/start/before.jpg",
                "after": "assets/images/menu/main/rus/start/after.jpg"
            },
            "SETTINGS_BTN_RUS": {
                "before": "assets/images/menu/main/rus/settings/before.jpg",
                "after": "assets/images/menu/main/rus/settings/after.jpg"
            },
            "EXIT_BTN_RUS": {
                "before": "assets/images/menu/main/rus/exit/before.jpg",
                "after": "assets/images/menu/main/rus/exit/after.jpg"
            },

            # Меню настроек (EN)
            "GAME_SETTINGS_BTN": {
                "before": "assets/images/menu/settings/eng/settings/before.jpg",
                "after": "assets/images/menu/settings/eng/settings/after.jpg"
            },
            "GRAPHICS_SETTINGS_BTN": {
                "before": "assets/images/menu/settings/eng/graphics/before.jpg",
                "after": "assets/images/menu/settings/eng/graphics/after.jpg"
            },
            "LANGUAGE_SETTINGS_BTN": {
                "before": "assets/images/menu/settings/eng/language/before.jpg",
                "after": "assets/images/menu/settings/eng/language/after.jpg"
            },
            "BACK_BTN": {
                "before": "assets/images/menu/settings/eng/back/before.jpg",
                "after": "assets/images/menu/settings/eng/back/after.jpg"
            },

            # Меню настроек (RU)
            "GAME_SETTINGS_BTN_RUS": {
                "before": "assets/images/menu/settings/rus/settings/before.jpg",
                "after": "assets/images/menu/settings/rus/settings/after.jpg"
            },
            "GRAPHICS_SETTINGS_BTN_RUS": {
                "before": "assets/images/menu/settings/rus/graphics/before.jpg",
                "after": "assets/images/menu/settings/rus/graphics/after.jpg"
            },
            "LANGUAGE_SETTINGS_BTN_RUS": {
                "before": "assets/images/menu/settings/rus/language/before.jpg",
                "after": "assets/images/menu/settings/rus/language/after.jpg"
            },
            "BACK_BTN_RUS": {
                "before": "assets/images/menu/settings/rus/back/before.jpg",
                "after": "assets/images/menu/settings/rus/back/after.jpg"
            },

            # Меню языка (EN)
            "ENGLISH_BTN": {
                "before": "assets/images/menu/settings/eng/eng/before.jpg",
                "after": "assets/images/menu/settings/eng/eng/after.jpg"
            },
            "RUSSIAN_BTN": {
                "before": "assets/images/menu/settings/rus/rus/before.jpg",
                "after": "assets/images/menu/settings/rus/rus/after.jpg"
            },
            "LANG_BACK_BTN": {
                "before": "assets/images/menu/settings/eng/back/before.jpg",
                "after": "assets/images/menu/settings/eng/back/after.jpg"
            },

            # Меню языка (RU)
            "ENGLISH_BTN_RUS": {
                "before": "assets/images/menu/settings/eng/eng/before.jpg",
                "after": "assets/images/menu/settings/eng/eng/after.jpg"
            },
            "RUSSIAN_BTN_RUS": {
                "before": "assets/images/menu/settings/rus/rus/before.jpg",
                "after": "assets/images/menu/settings/rus/rus/after.jpg"
            },
            "LANG_BACK_BTN_RUS": {
                "before": "assets/images/menu/settings/rus/back/before.jpg",
                "after": "assets/images/menu/settings/rus/back/after.jpg"
            },

            # Фон меню настроек
            "SETTINGS_BG": "assets/images/menu/settings/backgrounds/dark_prince.jpg",
            "LANGUAGE_BG": "assets/images/menu/settings/backgrounds/dark_prince.jpg"
        }

        # === Локализация ===
        self.LANGUAGE_TEXT = {
            "english": {
                "start": "Start Game",
                "settings": "Settings",
                "exit": "Exit",
                "game_settings": "Game Settings",
                "graphics_settings": "Graphics",
                "language_settings": "Language",
                "back": "Back",
                "english": "English",
                "russian": "Russian",
                # Add more English text keys as needed
            },
            "russian": {
                "start": "Начать игру",
                "settings": "Настройки",
                "exit": "Выход",
                "game_settings": "Настройки игры",
                "graphics_settings": "Графика",
                "language_settings": "Язык",
                "back": "Назад",
                "english": "Английский",
                "russian": "Русский",
                # Add more Russian text keys as needed
            }
        }

    def set_language(self, lang: str) -> None:
        """Устанавливает текущий язык интерфейса (english/russian)"""
        if lang in ["english", "russian"]:
            self.current_language = lang

    def get_text(self, key: str) -> str:
        """Возвращает локализованный текст по ключу"""
        return self.LANGUAGE_TEXT[self.current_language].get(key, key)

    def get_image(self, key: str, state: str = None) -> Union[str, Dict[str, str], None]:
        """
        Возвращает путь к изображению с учетом языка
        :param key: Ключ изображения
        :param state: Состояние ('before', 'after' для кнопок)
        :return: Путь к изображению или None если не найдено
        """
        # Пробуем получить русскую версию, если язык русский
        if self.current_language == "russian":
            rus_key = f"{key}_RUS"
            if rus_key in self.MENU_IMAGES:
                key = rus_key

        path = self.MENU_IMAGES.get(key)
        if not path:
            return None

        if isinstance(path, dict) and state:
            return path.get(state)
        return path

    def get_image_path(self, key: str, state: str = None) -> Union[str, None]:
        """Алиас для get_image (совместимость)"""
        return self.get_image(key, state)


# Глобальный экземпляр конфигурации
config = GameConfig()
