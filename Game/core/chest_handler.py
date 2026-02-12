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
from core.chest_storage import ChestStorage


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
        
        # Текущий открытый сундук
        self.current_chest_storage: Optional[ChestStorage] = None
        self.current_chest_id: Optional[str] = None
        
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
            image = pygame.image.load(path).convert_alpha()
            # Уменьшаем изображение сундука в 2 раза
            original_size = image.get_size()
            new_size = (original_size[0] // 2, original_size[1] // 2)
            self._chest_image = pygame.transform.scale(image, new_size)
            self._current_lang = lang
            if config.DEBUG_MODE:
                print(f"[CHEST] Изображение сундука масштабировано: {original_size} -> {new_size}")
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

        # Получаем или создаем хранилище для этого сундука
        if self.animating_obj:
            self.current_chest_id = f"chest_{int(self.animating_obj.x)}_{int(self.animating_obj.y)}"
            if hasattr(self.game, 'chest_manager'):
                self.current_chest_storage = self.game.chest_manager.get_or_create_chest(
                    self.current_chest_id, 
                    max_slots=24  # 24 слота в сундуке
                )
                if config.DEBUG_MODE:
                    print(f"[CHEST] Открыт сундук {self.current_chest_id}")

        # Загружаем изображение сундука
        self.game.chest_panel_img = self._load_chest_image()
        
        self.game.show_chest = True
        self.game.active_chest_obj = self.animating_obj
        
        if config.DEBUG_MODE:
            print("[CHEST] Открыт интерфейс сундука")

    def close(self):
        """Закрывает интерфейс сундука и запускает анимацию закрытия."""
        if self.chest_state != 'open':
            return
        
        # Сохраняем содержимое сундука
        if hasattr(self.game, 'chest_manager') and self.current_chest_storage:
            self.game.chest_manager.save_chests()
            if config.DEBUG_MODE:
                print(f"[CHEST] Сохранено содержимое сундука {self.current_chest_id}")
        
        # Очищаем ссылки на текущий сундук
        self.current_chest_storage = None
        self.current_chest_id = None
        
        # Закрываем интерфейс и очищаем изображение
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
        """
        Отрисовывает интерфейс сундука с слотами и инвентарем.
        
        Args:
            screen: Поверхность для рисования (actual screen).
        """
        if self.chest_state != 'open' or not self.current_chest_storage:
            return
        
        # Фоновое изображение сундука (если есть)
        if self.game.chest_panel_img:
            img = self.game.chest_panel_img
            img_w, img_h = img.get_size()
            x = (config.WIDTH - img_w) // 2
            y = (config.HEIGHT - img_h) // 2
            
            # Черный фон под изображением
            screen.fill((0, 0, 0), (x, y, img_w, img_h))
            screen.blit(img, (x, y))
        
        # Параметры слотов
        slot_size = 70
        slot_spacing = 10
        cols = 6  # 6 колонок
        rows = 4  # 4 ряда (всего 24 слота)
        
        # Позиция сетки слотов сундука (слева)
        chest_grid_x = 100
        chest_grid_y = 200
        
        # Отрисовываем заголовок
        font = pygame.font.Font(None, 36)
        title_text = "Сундук" if config.current_language == "russian" else "Chest"
        title_surface = font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surface, (chest_grid_x, chest_grid_y - 50))
        
        # Отрисовываем слоты сундука
        for idx in range(self.current_chest_storage.max_slots):
            row = idx // cols
            col = idx % cols
            
            slot_x = chest_grid_x + col * (slot_size + slot_spacing)
            slot_y = chest_grid_y + row * (slot_size + slot_spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            
            # Рисуем рамку слота
            pygame.draw.rect(screen, (80, 80, 80), slot_rect, 2)
            
            # Рисуем предмет в слоте (если есть)
            item = self.current_chest_storage.get_item(idx)
            if item and item.image:
                # Масштабируем изображение предмета под размер слота
                item_img = pygame.transform.smoothscale(item.image, (slot_size - 10, slot_size - 10))
                screen.blit(item_img, (slot_x + 5, slot_y + 5))
        
        # Отрисовываем инвентарь справа (используя существующую систему Inventory)
        if hasattr(self.game, 'player_ui') and self.game.player_ui and hasattr(self.game.player_ui, 'inventory'):
            self._draw_inventory_side(screen)
    
    def _draw_inventory_side(self, screen: pygame.Surface):
        """
        Отрисовывает инвентарь игрока справа от сундука.
        
        Args:
            screen: Поверхность для рисования.
        """
        # Параметры слотов инвентаря
        slot_size = 70
        slot_spacing = 10
        cols = 4  # 4 колонки
        
        # Позиция сетки инвентаря (справа)
        inv_grid_x = 800
        inv_grid_y = 200
        
        # Заголовок
        font = pygame.font.Font(None, 36)
        title_text = "Инвентарь" if config.current_language == "russian" else "Inventory"
        title_surface = font.render(title_text, True, (255, 255, 255))
        screen.blit(title_surface, (inv_grid_x, inv_grid_y - 50))
        
        # Получаем инвентарь игрока
        inventory = self.game.player_ui.inventory
        
        # Отрисовываем видимые слоты инвентаря
        for visible_idx in range(len(inventory.inventory_slots_positions)):
            global_idx = inventory._visible_index_to_global(visible_idx)
            if 0 <= global_idx < len(inventory.inventory_slots):
                item = inventory.inventory_slots[global_idx]
                
                row = visible_idx // cols
                col = visible_idx % cols
                
                slot_x = inv_grid_x + col * (slot_size + slot_spacing)
                slot_y = inv_grid_y + row * (slot_size + slot_spacing)
                slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
                
                # Рисуем рамку слота
                pygame.draw.rect(screen, (80, 80, 80), slot_rect, 2)
                
                # Рисуем предмет (если есть)
                if item and item.image:
                    item_img = pygame.transform.smoothscale(item.image, (slot_size - 10, slot_size - 10))
                    screen.blit(item_img, (slot_x + 5, slot_y + 5))
        
        # Отрисовываем перетаскиваемый предмет у курсора
        if self.dragged_item and self.dragged_item.image:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            drag_img = pygame.transform.smoothscale(self.dragged_item.image, (self.chest_slot_size - 10, self.chest_slot_size - 10))
            screen.blit(drag_img, (mouse_x - drag_img.get_width() // 2, mouse_y - drag_img.get_height() // 2))
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обрабатывает события для интерфейса сундука.
        
        Args:
            event: Событие pygame.
            
        Returns:
            True если событие обработано, False иначе.
        """
        if self.chest_state != 'open' or not self.current_chest_storage:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Левая кнопка мыши
            mouse_x, mouse_y = event.pos
            
            # Проверяем клик по слотам сундука
            chest_slot = self._get_chest_slot_at_pos(mouse_x, mouse_y)
            if chest_slot is not None:
                self._handle_chest_slot_click(chest_slot)
                return True
            
            # Проверяем клик по слотам инвентаря
            inv_slot = self._get_inventory_slot_at_pos(mouse_x, mouse_y)
            if inv_slot is not None:
                self._handle_inventory_slot_click(inv_slot)
                return True
            
            # Клик вне слотов - отменяем перетаскивание
            if self.dragged_item:
                self._cancel_drag()
                return True
        
        return False
    
    def _get_chest_slot_at_pos(self, x: int, y: int) -> Optional[int]:
        """
        Определяет индекс слота сундука по координатам мыши.
        
        Args:
            x, y: Координаты мыши.
            
        Returns:
            Индекс слота или None.
        """
        for idx in range(self.current_chest_storage.max_slots):
            row = idx // self.chest_cols
            col = idx % self.chest_cols
            
            slot_x = self.chest_grid_x + col * (self.chest_slot_size + self.chest_slot_spacing)
            slot_y = self.chest_grid_y + row * (self.chest_slot_size + self.chest_slot_spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, self.chest_slot_size, self.chest_slot_size)
            
            if slot_rect.collidepoint(x, y):
                return idx
        
        return None
    
    def _get_inventory_slot_at_pos(self, x: int, y: int) -> Optional[int]:
        """
        Определяет индекс слота инвентаря по координатам мыши.
        
        Args:
            x, y: Координаты мыши.
            
        Returns:
            Глобальный индекс слота инвентаря или None.
        """
        inventory = self.game.player_ui.inventory
        
        for visible_idx in range(len(inventory.inventory_slots_positions)):
            row = visible_idx // self.inv_cols
            col = visible_idx % self.inv_cols
            
            slot_x = self.inv_grid_x + col * (self.inv_slot_size + self.inv_slot_spacing)
            slot_y = self.inv_grid_y + row * (self.inv_slot_size + self.inv_slot_spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, self.inv_slot_size, self.inv_slot_size)
            
            if slot_rect.collidepoint(x, y):
                global_idx = inventory._visible_index_to_global(visible_idx)
                return global_idx if 0 <= global_idx < len(inventory.inventory_slots) else None
        
        return None
    
    def _handle_chest_slot_click(self, slot_idx: int):
        """
        Обрабатывает клик по слоту сундука.
        
        Args:
            slot_idx: Индекс слота сундука.
        """
        if self.dragged_item is None:
            # Берем предмет из сундука
            item = self.current_chest_storage.get_item(slot_idx)
            if item:
                self.dragged_item = self.current_chest_storage.remove_item(slot_idx)
                self.drag_source = ('chest', slot_idx)
                if config.DEBUG_MODE:
                    print(f"[CHEST] Взят предмет {self.dragged_item.name} из сундука, слот {slot_idx}")
        else:
            # Кладем предмет в сундук
            existing_item = self.current_chest_storage.get_item(slot_idx)
            if existing_item is None:
                # Слот пустой, просто кладем
                self.current_chest_storage.add_item(self.dragged_item, slot_idx)
                if config.DEBUG_MODE:
                    print(f"[CHEST] Положен предмет {self.dragged_item.name} в сундук, слот {slot_idx}")
                self.dragged_item = None
                self.drag_source = None
            else:
                # Слот занят, меняем местами
                self.current_chest_storage.remove_item(slot_idx)
                self.current_chest_storage.add_item(self.dragged_item, slot_idx)
                self._return_item_to_source(existing_item)
                if config.DEBUG_MODE:
                    print(f"[CHEST] Обмен: {self.dragged_item.name} -> слот {slot_idx}, {existing_item.name} -> источник")
                self.dragged_item = None
                self.drag_source = None
    
    def _handle_inventory_slot_click(self, slot_idx: int):
        """
        Обрабатывает клик по слоту инвентаря.
        
        Args:
            slot_idx: Глобальный индекс слота инвентаря.
        """
        inventory = self.game.player_ui.inventory
        
        if self.dragged_item is None:
            # Берем предмет из инвентаря
            item = inventory.inventory_slots[slot_idx]
            if item:
                inventory.inventory_slots[slot_idx] = None
                self.dragged_item = item
                self.drag_source = ('inventory', slot_idx)
                if config.DEBUG_MODE:
                    print(f"[CHEST] Взят предмет {self.dragged_item.name} из инвентаря, слот {slot_idx}")
        else:
            # Кладем предмет в инвентарь
            existing_item = inventory.inventory_slots[slot_idx]
            if existing_item is None:
                # Слот пустой, просто кладем
                inventory.inventory_slots[slot_idx] = self.dragged_item
                if config.DEBUG_MODE:
                    print(f"[CHEST] Положен предмет {self.dragged_item.name} в инвентарь, слот {slot_idx}")
                self.dragged_item = None
                self.drag_source = None
            else:
                # Слот занят, меняем местами
                inventory.inventory_slots[slot_idx] = self.dragged_item
                self._return_item_to_source(existing_item)
                if config.DEBUG_MODE:
                    print(f"[CHEST] Обмен: {self.dragged_item.name} -> слот {slot_idx}, {existing_item.name} -> источник")
                self.dragged_item = None
                self.drag_source = None
    
    def _return_item_to_source(self, item):
        """
        Возвращает предмет в исходный слот при обмене.
        
        Args:
            item: Предмет для возврата.
        """
        if self.drag_source is None:
            return
        
        source_type, source_idx = self.drag_source
        
        if source_type == 'chest':
            self.current_chest_storage.add_item(item, source_idx)
        elif source_type == 'inventory':
            inventory = self.game.player_ui.inventory
            inventory.inventory_slots[source_idx] = item
    
    def _cancel_drag(self):
        """Отменяет перетаскивание и возвращает предмет в исходный слот."""
        if self.dragged_item and self.drag_source:
            self._return_item_to_source(self.dragged_item)
            if config.DEBUG_MODE:
                print(f"[CHEST] Перетаскивание отменено, предмет {self.dragged_item.name} возвращен")
            self.dragged_item = None
            self.drag_source = None
