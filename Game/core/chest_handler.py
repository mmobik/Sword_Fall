"""
Модуль обработчика сундуков.

Содержит класс ChestInteractionHandler для обработки взаимодействия
с сундуками на карте, анимации открытия/закрытия и отображения интерфейса.
"""

import os
from typing import Optional
import pygame
from core.config import config
from core.pathutils import resource_path


class ChestInteractionHandler:
    """
    Обработчик интерактивных сундуков.

    При взаимодействии (E у объекта с interactive_type=chest):
    - Проигрывает анимацию открытия и звук
    - Открывает панель сундука (chest_rus.png / chest_eng.png по языку)
    - При закрытии проигрывает анимацию закрытия и звук
    """

    def __init__(self, game):
        self.game = game
        self._chest_image = None  # кэш загруженного интерфейса по текущему языку
        self._current_lang = None
        
        # Анимация сундука
        self.chest_state = 'closed'  # closed, opening, open, closing
        self.animation_frames = []  # список спрайтов для анимации
        self.current_frame = 0
        self.animation_speed = 0.1  # секунд на кадр
        self.animation_timer = 0.0
        self.animating_obj = None  # объект сундука, который анимируется
        
        self._load_chest_tileset()

    def _load_chest_tileset(self):
        """Загружает тайлсет сундука и извлекает кадры анимации."""
        tileset_path = resource_path("Game/assets/Tiles/Tilesets/chest.png")
        if not os.path.exists(tileset_path):
            if config.DEBUG_MODE:
                print(f"[CHEST] Тайлсет не найден: {tileset_path}")
            return
        
        try:
            tileset = pygame.image.load(tileset_path).convert_alpha()
            # Координаты кадров: (0,0), (0,32), (0,64), (0,96)
            # Предполагаем размер кадра 32x32
            frame_width, frame_height = 32, 32
            y_offsets = [0, 32, 64, 96]
            
            for y in y_offsets:
                frame = tileset.subsurface((0, y, frame_width, frame_height))
                self.animation_frames.append(frame)
            
            if config.DEBUG_MODE:
                print(f"[CHEST] Загружено {len(self.animation_frames)} кадров анимации")
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"[CHEST] Ошибка загрузки тайлсета: {e}")

    def _get_chest_image_path(self) -> str:
        """Путь к изображению интерфейса сундука по текущему языку."""
        if config.current_language == "russian":
            return config.CHEST_PANEL["IMAGE_PATH_RUS"]
        return config.CHEST_PANEL["IMAGE_PATH_ENG"]

    def _load_chest_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение интерфейса сундука по текущему языку (с кэшем)."""
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
        Обрабатывает взаимодействие с сундуком: запускает анимацию открытия.

        Args:
            obj: Объект сундука из карты (interactive=True, interactive_type=chest).
        """
        if self.chest_state != 'closed':
            return  # Уже открыт или анимируется
        
        player = getattr(self.game, "player", None)
        if player:
            steps_channel = getattr(player, "_steps_channel", None)
            if steps_channel:
                steps_channel.stop()
                setattr(player, "_steps_channel", None)
            player.is_walking = False

        # Ищем объект с chest=True в chest_objects для анимации
        chest_obj = None
        chest_objects = getattr(self.game, 'chest_objects', [])
        
        if config.DEBUG_MODE:
            print(f"[CHEST] Найдено chest_objects: {len(chest_objects)}")
            for idx, c in enumerate(chest_objects):
                print(f"[CHEST]   #{idx}: pos=({c.x}, {c.y}), size=({c.width}x{c.height}), chest={c.properties.get('chest', 'N/A')}")
        
        if chest_objects:
            # Берём ближайший к игроку объект сундука
            if player:
                min_dist = float('inf')
                for c_obj in chest_objects:
                    c_rect = pygame.Rect(int(c_obj.x), int(c_obj.y), 
                                        int(c_obj.width), int(c_obj.height))
                    dist = player.hitbox.center[0] - c_rect.centerx
                    dist = dist * dist + (player.hitbox.center[1] - c_rect.centery) ** 2
                    if dist < min_dist:
                        min_dist = dist
                        chest_obj = c_obj
        
        if chest_obj is None:
            if config.DEBUG_MODE:
                print("[CHEST] Объект с chest=True не найден, используем interactive объект")
            chest_obj = obj
        
        if config.DEBUG_MODE:
            print(f"[CHEST] Используем объект на позиции ({chest_obj.x}, {chest_obj.y}), размер ({chest_obj.width}x{chest_obj.height})")

        # Начинаем анимацию открытия
        self.chest_state = 'opening'
        self.current_frame = 0
        self.animation_timer = 0.0
        self.animating_obj = chest_obj
        
        # Воспроизводим звук открытия
        if hasattr(self.game, 'sound_manager') and self.game.sound_manager:
            self.game.sound_manager.play_sound('chest_open')
        
        if config.DEBUG_MODE:
            print("[CHEST] Начата анимация открытия")

    def _finish_opening(self):
        """Завершает анимацию открытия и показывает интерфейс."""
        self.chest_state = 'open'
        
        img = self._load_chest_image()
        if img is None:
            if config.DEBUG_MODE:
                print("[CHEST] Не удалось загрузить изображение сундука")
            self.chest_state = 'closed'
            return

        self.game.chest_panel_img = img
        self.game.show_chest = True
        self.game.active_chest_obj = self.animating_obj
        
        if config.DEBUG_MODE:
            print("[CHEST] Открыт интерфейс сундука")

    def close(self):
        """Закрывает интерфейс сундука и запускает анимацию закрытия."""
        if self.chest_state != 'open':
            return
        
        # Сначала закрываем интерфейс
        self.game.show_chest = False
        self.game.chest_panel_img = None
        
        # Запускаем анимацию закрытия
        self.chest_state = 'closing'
        self.current_frame = len(self.animation_frames) - 1
        self.animation_timer = 0.0
        
        # Воспроизводим звук закрытия
        if hasattr(self.game, 'sound_manager') and self.game.sound_manager:
            self.game.sound_manager.play_sound('chest_close')
        
        if config.DEBUG_MODE:
            print("[CHEST] Начата анимация закрытия")

    def _finish_closing(self):
        """Завершает анимацию закрытия."""
        self.chest_state = 'closed'
        self.animating_obj = None
        self.game.active_chest_obj = None
        self.game.active_npc_obj = None
        
        if config.DEBUG_MODE:
            print("[CHEST] Сундук закрыт")

    def update(self, dt: float):
        """
        Обновляет анимацию сундука.

        Args:
            dt: Время с последнего кадра (в секундах).
        """
        if self.chest_state == 'opening':
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.current_frame += 1
                
                if self.current_frame >= len(self.animation_frames):
                    self._finish_opening()
        
        elif self.chest_state == 'closing':
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0.0
                self.current_frame -= 1
                
                if self.current_frame < 0:
                    self._finish_closing()

    def draw(self, screen: pygame.Surface, camera):
        """
        Отрисовывает анимацию сундука (если анимируется).

        Args:
            screen: Поверхность для рисования (virtual_screen).
            camera: Объект камеры для преобразования координат.
        """
        if self.chest_state in ('opening', 'closing') and self.animating_obj and self.animation_frames:
            if 0 <= self.current_frame < len(self.animation_frames):
                frame = self.animation_frames[self.current_frame]
                
                # Используем координаты объекта напрямую (obj.x, obj.y в пикселях)
                # В Tiled координата Y указывает на нижний край объекта, поэтому вычитаем высоту
                # Дополнительное смещение для выравнивания с тайлом (32 - 11 = 21 пикселя вверх)
                world_x = int(self.animating_obj.x)
                world_y = int(self.animating_obj.y) - int(self.animating_obj.height) - 21
                
                if config.DEBUG_MODE and self.current_frame == 0:
                    print(f"[CHEST] Анимация на позиции: ({world_x}, {world_y}), размер кадра: {frame.get_size()}, объект y={self.animating_obj.y}, высота={self.animating_obj.height}")
                
                # Рисуем спрайт в позиции объекта с учётом камеры
                obj_rect = pygame.Rect(world_x, world_y, frame.get_width(), frame.get_height())
                screen_pos = camera.apply(obj_rect)
                screen.blit(frame, screen_pos.topleft)
