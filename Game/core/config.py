"""
Конфигурационные параметры игры.
Все настройки доступны через глобальный экземпляр config.
"""

from typing import Dict, Union
import json
import os
import pygame


class GameConfig:
    def __init__(self):
        # Языковые настройки
        self.current_language = "english"
        self._load_language_setting()

        # Настройки экрана
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.GAME_NAME = "SwordFall"
        self.FPS = 144
        self.TARGET_FPS = 60
        self.SCREEN_SIZE = (self.WIDTH, self.HEIGHT)
        self.VIRTUAL_WIDTH = 960
        self.VIRTUAL_HEIGHT = 540

        # Настройки интерфейса
        self.BUTTON_SPACING = 125
        self._image_cache = {}
        self.MENU_BUTTON_X = self.WIDTH // 3
        self.SETTINGS_BUTTON_X = self.WIDTH // 2 - 200
        self.SETTINGS_BUTTON_Y_START = self.HEIGHT // 2 - 200
        self.BACK_BUTTON_X = self.WIDTH // 2 - 200
        self.BACK_BUTTON_Y = self.HEIGHT - 300
        self.FADE_DURATION = 0.5

        # Пути к игровым ресурсам
        self.ASSETS = {
            "ICON": "assets/images/icons/icon_1.jpg",
            "SOUNDTRACK": "assets/sounds/soundtracks/Dark_fantasm.mp3"
        }

        # Настройки кнопки диалога
        self.DIALOGUE_BUTTON = {
            "IMAGE_PATH": "assets/images/game/dialogue/talk_v3.png",
            "OFFSET_Y": 50,  # Отступ от игрока по Y
            "FALLBACK_Y": 120  # Отступ снизу экрана для fallback
        }

        # Настройки панели диалога
        self.DIALOGUE_PANEL = {
            "IMAGE_PATH": "assets/images/game/dialogue/panel_v3.png",
            "POSITION": "bottom",  # bottom, center, top
            "OFFSET_Y": 20,  # Отступ снизу экрана
            "TEXT_OFFSET_X": 30,  # Отступ текста от края панели по X
            "TEXT_OFFSET_Y": 50,  # Отступ текста от края панели по Y
            "FONT_SIZE": 24,
            "FONT_COLOR": (255, 255, 255),  # Белый цвет текста
            "SHOW_DURATION": 3.0  # Время показа диалога в секундах
        }

        # Изображения NPC для диалогов
        self.NPC_IMAGES = {
            "GUARD": "assets/images/game/The guard_4.png",
            "KING": "assets/images/game/King.png"
        }

        # Цветовая палитра
        self.COLORS = {
            "DARK_BLUE": (0, 33, 55),
            "BLUE": (46, 68, 116),
            "WHITE": (255, 255, 255),
            "BLACK": (0, 0, 0),
            "RED": (255, 0, 0),
            "GREEN": (0, 255, 0)
        }
        self.GAME_COLORS = {
            "DARK_BLUE": (0, 33, 55),
            "BLUE": (46, 68, 116),
            "WHITE": (255, 255, 255)
        }

        # Параметры анимации
        self.FRAME_SIZE = (128, 64)
        self.NO_ANIMATION = float('inf')

        # Параметры игрового уровня
        self.TILE_SIZE = 100
        self.LEVEL_MAP_PATH = "assets/Tiles/Royal_one.tmx"

        # Параметры игрока
        self.PLAYER_SPEED = 180

        # Параметры хитбокса игрока
        self.PLAYER_HITBOX = {
            "WIDTH": 15,
            "HEIGHT": 10,
            "X_OFFSET": 1,
            "Y_OFFSET": 2
        }

        # Состояния игрока
        self.PLAYER_STATES = {
            # Idle-анимации (стоит на месте)
            "idle_front": {
                "sprite_sheet": "assets/sprites/player/armed/idle_front.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.17,
                "flip": False
            },
            "idle_right": {
                "sprite_sheet": "assets/sprites/player/armed/idle_right.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.17,
                "flip": False
            },
            "idle_left": {
                "sprite_sheet": "assets/sprites/player/armed/idle_left.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.17,
                "flip": False
            },
            "idle_back": {
                "sprite_sheet": "assets/sprites/player/unarmed/idle_back.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.17,
                "flip": False
            },

            # Run-анимации (движение)
            "run_right": {
                "sprite_sheet": "assets/sprites/player/armed/run_down.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.13,
                "flip": False
            },
            "run_left": {
                "sprite_sheet": "assets/sprites/player/armed/run_down.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.13,
                "flip": True
            },
            "run_up": {
                "sprite_sheet": "assets/sprites/player/unarmed/run_up.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.13,
                "flip": False
            },
            "run_down": {
                "sprite_sheet": "assets/sprites/player/unarmed/run_down.png",
                "frames": [(0, 0), (128, 0), (0, 64), (128, 64), (0, 128), (128, 128), (0, 192), (128, 192)],
                "animation_speed": 0.13,
                "flip": False
            }
        }

        # Коллизии и дебаг
        self.COLLISION_SETTINGS = {
            "COLLISION_LAYER_NAME": "CollisionLayer",
            "DEFAULT_COLLISION": True
        }

        self.DEBUG_MODE = False
        self.DEBUG_COLORS = {
            "COLLISION": (255, 0, 0),  # Красный - объекты коллизий
            "HITBOX": (0, 255, 0),  # Зеленый - хитбокс игрока
        }
        self.BG_COLOR = (0, 125, 200)  # Голубой

        # Изображения для меню
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
            "MUSIC_SETTINGS_BTN": {
                "before": "assets/images/menu/settings/eng/music/before.jpg",
                "after": "assets/images/menu/settings/eng/music/after.jpg"
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
            "MUSIC_SETTINGS_BTN_RUS": {
                "before": "assets/images/menu/settings/rus/music/before.jpg",
                "after": "assets/images/menu/settings/rus/music/after.jpg"
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

        # Локализация
        self.LANGUAGE_TEXT = {
            "english": {
                "start": "Start Game",
                "settings": "Settings",
                "exit": "Exit",
                "game_settings": "Game Settings",
                "graphics_settings": "Graphics",
                "language_settings": "Language",
                "music_settings": "Music",
                "back": "Back",
                "english": "English",
                "russian": "Russian",
            },
            "russian": {
                "start": "Начать игру",
                "settings": "Настройки",
                "exit": "Выход",
                "game_settings": "Настройки игры",
                "graphics_settings": "Графика",
                "language_settings": "Язык",
                "music_settings": "Музыка",
                "back": "Назад",
                "english": "Английский",
                "russian": "Русский",
            }
        }

    def set_language(self, lang: str) -> None:
        """Устанавливает текущий язык интерфейса (english/russian) и сохраняет его"""
        if lang in ["english", "russian"]:
            self.current_language = lang
            self._save_language_setting()

    def _load_language_setting(self):
        try:
            dir_path = "userdata"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            config_path = os.path.join(dir_path, "config_settings.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    settings = json.load(f)
                    lang = settings.get("language")
                    if lang in ["english", "russian"]:
                        self.current_language = lang
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            if self.DEBUG_MODE:
                print(f"Ошибка загрузки настроек языка: {e}")
            pass

    def _save_language_setting(self):
        try:
            dir_path = "userdata"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            config_path = os.path.join(dir_path, "config_settings.json")
            settings = {}
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    settings = json.load(f)
            settings["language"] = self.current_language
            with open(config_path, "w") as f:
                json.dump(settings, f)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            if self.DEBUG_MODE:
                print(f"Ошибка сохранения настроек языка: {e}")
            pass

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

        if isinstance(path, dict):
            if state is not None:
                return path.get(state)
            else:
                return None
        if isinstance(path, str):
            return path
        return None

    def get_image_path(self, key: str, state: str = None) -> Union[str, None]:
        """Алиас для get_image (совместимость)"""
        result = self.get_image(key, state) if state is not None else self.get_image(key)
        return result if isinstance(result, str) else None

    def get_image_cached(self, key, state=None):
        cache_key = f"{key}_{state}"
        if cache_key not in self._image_cache:
            img = self.get_image(key, state) if state is not None else self.get_image(key)
            if isinstance(img, str):
                self._image_cache[cache_key] = img
        return self._image_cache.get(cache_key)

    def set_debug_mode(self, value: bool):
        self.DEBUG_MODE = value

    def load_npc_image(self, npc_type: str) -> Union[pygame.Surface, None]:
        """Безопасная загрузка изображения NPC с обработкой ошибок"""
        try:
            if npc_type.upper() in self.NPC_IMAGES:
                return pygame.image.load(self.NPC_IMAGES[npc_type.upper()]).convert_alpha()
            else:
                if self.DEBUG_MODE:
                    print(f"NPC image not found in config: {npc_type}")
                return None
        except Exception as e:
            if self.DEBUG_MODE:
                print(f"Failed to load NPC image {npc_type}: {e}")
            return None


# Глобальный экземпляр конфигурации
config = GameConfig()
