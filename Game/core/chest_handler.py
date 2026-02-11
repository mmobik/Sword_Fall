"""
Модуль обработчика сундуков.

Содержит класс ChestInteractionHandler для обработки взаимодействия
с сундуками на карте и отображения интерфейса сундука (по языку).
"""

import os
from typing import Optional
import pygame
from core.config import config
from core.pathutils import resource_path


class ChestInteractionHandler:
    """
    Обработчик интерактивных сундуков.

    При взаимодействии (E у объекта с interactive_type=chest) открывает
    панель сундука: chest_rus.png или chest_eng.png в зависимости от языка.
    Закрытие: ESC или клик вне панели (опционально).
    """

    def __init__(self, game):
        self.game = game
        self._chest_image = None  # кэш загруженного изображения по текущему языку
        self._current_lang = None  # язык, для которого загружен _chest_image

    def _get_chest_image_path(self) -> str:
        """Путь к изображению интерфейса сундука по текущему языку."""
        if config.current_language == "russian":
            return config.CHEST_PANEL["IMAGE_PATH_RUS"]
        return config.CHEST_PANEL["IMAGE_PATH_ENG"]

    def _load_chest_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение сундука по текущему языку (с кэшем)."""
        lang = config.current_language
        if self._chest_image is not None and self._current_lang == lang:
            return self._chest_image

        path = self._get_chest_image_path()
        path = resource_path(path)
        if not os.path.exists(path):
            if config.DEBUG_MODE:
                print(f"[CHEST] Файл не найден: {path}")
            return None

        try:
            self._chest_image = pygame.image.load(path).convert_alpha()
            self._current_lang = lang
            return self._chest_image
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"[CHEST] Ошибка загрузки {path}: {e}")
            return None

    def invalidate_cache(self):
        """Сбросить кэш изображения (вызвать при смене языка)."""
        self._chest_image = None
        self._current_lang = None

    def interact(self, obj):
        """
        Обрабатывает взаимодействие с сундуком.

        Args:
            obj: Объект сундука из карты (interactive=True, interactive_type=chest).
        """
        player = getattr(self.game, "player", None)
        if player:
            steps_channel = getattr(player, "_steps_channel", None)
            if steps_channel:
                steps_channel.stop()
                setattr(player, "_steps_channel", None)
            player.is_walking = False

        img = self._load_chest_image()
        if img is None:
            if config.DEBUG_MODE:
                print("[CHEST] Не удалось загрузить изображение сундука")
            return

        self.game.chest_panel_img = img
        self.game.show_chest = True
        self.game.active_chest_obj = obj
        if config.DEBUG_MODE:
            print("[CHEST] Открыт интерфейс сундука")

    def close(self):
        """Закрывает интерфейс сундука."""
        self.game.show_chest = False
        self.game.chest_panel_img = None
        self.game.active_chest_obj = None
        self.game.active_npc_obj = None  # убрать подсветку E у сундука
        if config.DEBUG_MODE:
            print("[CHEST] Сундук закрыт")
