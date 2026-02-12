"""
Простая система инвентаря для отображения изображения inventory.png и acs.png.
"""

import pygame
import os
from typing import Optional, List, Dict, Tuple, Any
from level.player_stats import PlayerStats
from core.config import config
from UI.items import InventoryItem
from UI.equipment_data import DEFAULT_ACS_ITEMS, ITEM_DATABASE
from UI.equipment_logic import recalculate_equipment_bonuses

class Inventory:
    """Класс инвентаря для отображения инвентаря (I) и ACS (O - аксессуары)."""
    
    def __init__(self, screen: pygame.Surface, player_stats: PlayerStats, initial_open: bool = False):
        self.screen = screen
        self.player_stats = player_stats
        
        # Загружаем изображения интерфейсов
        self.inventory_image = self._load_inventory_image()  # Для I (профиль)
        self.acs_image = self._load_acs_image()              # Для O (слоты)
        self.inventory_profile = self._load_inventory_profile_image()
        
        # Состояние видимости
        self.inventory_open = initial_open  # I - профиль и характеристики
        self.acs_open = False               # O - слоты инвентаря и экипировки
        
        # Для хранения скриншотов фона
        self.background = None
        self.acs_background = None
        
        # === СИСТЕМА ПРЕДМЕТОВ И СЛОТОВ (ТОЛЬКО В ACS - КЛАВИША O) ===

        # Параметры сетки ACS‑инвентаря
        # Видимая область: 4 столбца × 5 строк = 20 ячеек
        # Максимальная высота: 32 строки (прокрутка по вертикали)
        self.inventory_cols = 4
        self.inventory_visible_rows = 5
        self.inventory_total_rows = 32
        self.inventory_scroll_row = 0  # индекс верхней видимой строки
        # Размер одной ячейки (ширина × высота) в пикселях
        self.inventory_slot_width = 132
        self.inventory_slot_height = 115
        # Отступы между ячейками
        self.inventory_slot_spacing_x = 10
        self.inventory_slot_spacing_y = 10
        # Базовые координаты левого верхнего угла решётки (можно легко сдвигать)
        self.inventory_grid_start_x = 1037
        self.inventory_grid_start_y = 221
        # Базовые координаты ползунка прокрутки (независимы от решётки по X/Y)
        grid_width_tmp = (
            self.inventory_cols * (self.inventory_slot_width + self.inventory_slot_spacing_x)
            - self.inventory_slot_spacing_x
        )
        self.inventory_scroll_x = self.inventory_grid_start_x + grid_width_tmp + 35
        self.inventory_scroll_y = self.inventory_grid_start_y
        # Диапазон по вертикали, в котором ползунок может перемещаться
        track_height_tmp = (
            self.inventory_visible_rows * (self.inventory_slot_height + self.inventory_slot_spacing_y)
            - self.inventory_slot_spacing_y
        )
        self.inventory_scroll_track_top = self.inventory_scroll_y + 20
        self.inventory_scroll_track_bottom = self.inventory_scroll_y + track_height_tmp - 20

        # Слоты инвентаря (4 × 32 = 128 слотов) - ТОЛЬКО В ACS
        self.inventory_slots = [None] * (self.inventory_cols * self.inventory_total_rows)
        self.inventory_slots_positions = []  # Координаты видимых слотов (только 4×8)

        # Скроллбар для инвентаря (ACS, категория "Инвентарь")
        self.inventory_scrollbar_rect = None
        self.inventory_scroll_thumb_rect = None
        self.inventory_dragging_scroll = False
        self.inventory_scroll_thumb_image: Optional[pygame.Surface] = self._load_inventory_scroll_thumb_image()
        
        # Слоты экипировки (ТОЛЬКО В ACS)
        self.equipment_slots = {
            "Голова": None,
            "Шея": None,
            "Плечи": None,
            "Грудь": None,
            "Руки": None,
            "Правая рука": None,
            "Левая рука": None,
            "Кольцо 1": None,
            "Кольцо 2": None,
            "Ноги": None
        }
        self.equipment_slots_positions = {}  # Координаты слотов экипировки
        
        # Перетаскивание (ТОЛЬКО В ACS)
        self.dragged_item = None
        self.drag_offset = (0, 0)
        self.selected_slot = None  # Выбранный слот
        
        # Категории для ползунка в ACS
        self.acs_categories = ["Инвентарь", "Экипировка", "Хранилище"]
        self.current_acs_category = 0  # 0-инвентарь, 1-экипировка, 2-хранилище
        
        # Категории для ползунка в инвентаре-профиле (I)
        self.attribute_categories = ["Физические", "Ментальные", "Духовные", "Производные"]
        self.current_attribute_category = 0  # Текущая категория атрибутов
        
        # Контекстное меню (ТОЛЬКО В ACS)
        self.context_menu = None
        self.context_menu_pos = (0, 0)
        
        # Кнопки прокачки (ТОЛЬКО В I - профиль)
        self.attribute_buttons = {}
        
        # Подсказка для атрибутов
        self.hovered_attribute = None
        self.tooltip_timer = 0.0
        self.tooltip_delay = 0.5  # Задержка перед показом подсказки (секунды)
        
        # Предзагруженные предметы для теста (в ACS инвентарь)
        self._load_default_items()
        
        if config.DEBUG_MODE:
            print(f"[INVENTORY DEBUG] Инвентарь создан")
            print(f"[INVENTORY DEBUG] I (Профиль): {self.inventory_open}")
            print(f"[INVENTORY DEBUG] O (ACS/Слоты): {self.acs_open}")
            print(f"[INVENTORY DEBUG] Предметов в ACS: {self.get_total_items()}")
    
    def _load_inventory_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение inventory.png для профиля (I)."""
        try:
            image_path = "Game/assets/images/game/playerData/inventory.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                image = pygame.transform.scale(image, (1000, 600))
                if config.DEBUG_MODE:
                    print(f"[INVENTORY DEBUG] Изображение inventory загружено: {image.get_size()}")
                return image
            else:
                print(f"[INVENTORY ERROR] Файл не найден: {image_path}")
                return None
        except Exception as e:
            print(f"[INVENTORY ERROR] Ошибка загрузки inventory: {e}")
            return None
    
    def _load_acs_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение acs.png для слотов (O)."""
        try:
            image_path = "Game/assets/images/game/playerData/acs.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                image = pygame.transform.scale(image, (1800, 1200))
                if config.DEBUG_MODE:
                    print(f"[INVENTORY DEBUG] Изображение ACS загружено: {image.get_size()}")
                return image
            else:
                print(f"[INVENTORY WARNING] Файл ACS не найден: {image_path}. Можно продолжить без него.")
                return None
        except Exception as e:
            print(f"[INVENTORY ERROR] Ошибка загрузки ACS: {e}")
            return None

    def _load_inventory_scroll_thumb_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение ползунка для инвентаря ACS."""
        try:
            # Используем путь из запроса пользователя, но в относительном виде
            image_path = "Game/assets/Images/game/playerData/slider.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                if config.DEBUG_MODE:
                    print(f"[INVENTORY DEBUG] Изображение slider загружено: {image.get_size()}")
                return image
            else:
                print(f"[INVENTORY WARNING] Файл slider не найден: {image_path}")
                return None
        except Exception as e:
            print(f"[INVENTORY ERROR] Ошибка загрузки slider: {e}")
            return None

    def _load_inventory_profile_image(self) -> Optional[pygame.Surface]:
        """Загружает изображение inventory_profile.png."""
        try:
            image_path = "Game/assets/Images/game/player_profile.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                if config.DEBUG_MODE:
                    print(f"[INVENTORY DEBUG] Изображение inventory_profile загружено: {image.get_size()}")
                return image
            else:
                print(f"[INVENTORY ERROR] Файл не найден: {image_path}")
                return None
        except Exception as e:
            print(f"[INVENTORY ERROR] Ошибка загрузки inventory_profile: {e}")
            return None
    
    def _load_default_items(self):
        """Добавляет тестовые предметы в ACS инвентарь."""
        try:
            # Добавляем предметы, описанные в отдельном модуле данных
            for item_data in DEFAULT_ACS_ITEMS:
                item = InventoryItem(
                    item_id=item_data["id"],
                    name=item_data["name"],
                    description=item_data.get("description", ""),
                    item_type=item_data.get("type", "consumable"),
                    image_path=item_data.get("image_path"),
                    stats=item_data.get("stats"),
                    max_stack=item_data.get("max_stack", 99),
                    rarity=item_data.get("rarity", "common"),
                )
                self.add_item_to_free_slot(item)
                
        except Exception as e:
            print(f"[INVENTORY ERROR] Ошибка загрузки тестовых предметов: {e}")
            # Создаем предметы без изображений для теста
            test_items = [
                InventoryItem("test1", "Тестовый предмет 1", "Просто тест", "consumable"),
                InventoryItem("test2", "Тестовый предмет 2", "Еще тест", "material", max_stack=20),
            ]
            for item in test_items:
                self.add_item_to_free_slot(item)

    # === СЕРИАЛИЗАЦИЯ / ДЕСЕРИАЛИЗАЦИЯ ИНВЕНТАРЯ ===

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует текущее состояние инвентаря в словарь.

        Сохраняются:
        - содержимое всех слотов инвентаря (индекс, id предмета, количество);
        - содержимое слотов экипировки.
        """
        inventory_data: List[Dict[str, Any]] = []
        for idx, item in enumerate(self.inventory_slots):
            if item:
                inventory_data.append(
                    {
                        "slot_index": idx,
                        "id": item.id,
                        "count": item.count,
                    }
                )

        equipment_data: Dict[str, Dict[str, Any]] = {}
        for slot_name, item in self.equipment_slots.items():
            if item:
                equipment_data[slot_name] = {
                    "id": item.id,
                    "count": item.count,
                }

        return {
            "inventory_slots": inventory_data,
            "equipment_slots": equipment_data,
        }

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Восстанавливает инвентарь из словаря (формат, возвращаемый to_dict).
        """
        # Сбрасываем текущие слоты
        self.inventory_slots = [None] * (self.inventory_cols * self.inventory_total_rows)
        self.equipment_slots = {slot_name: None for slot_name in self.equipment_slots}

        # Восстанавливаем слоты инвентаря
        for slot_info in data.get("inventory_slots", []):
            try:
                idx = int(slot_info.get("slot_index"))
                item_id = slot_info.get("id")
                count = int(slot_info.get("count", 1))
            except (TypeError, ValueError):
                continue

            if item_id is None or not (0 <= idx < len(self.inventory_slots)):
                continue

            item_data = ITEM_DATABASE.get(item_id)
            if not item_data:
                # Неизвестный предмет — пропускаем
                continue

            try:
                new_item = InventoryItem(
                    item_id=item_data["id"],
                    name=item_data["name"],
                    description=item_data.get("description", ""),
                    item_type=item_data.get("type", "consumable"),
                    image_path=item_data.get("image_path"),
                    stats=item_data.get("stats"),
                    max_stack=item_data.get("max_stack", 99),
                    rarity=item_data.get("rarity", "common"),
                )
                new_item.count = max(1, min(count, new_item.max_stack))
                self.inventory_slots[idx] = new_item
            except Exception:
                # Любые проблемы с конкретным предметом — просто пропускаем его
                continue

        # Восстанавливаем экипировку
        for slot_name, slot_info in (data.get("equipment_slots") or {}).items():
            if slot_name not in self.equipment_slots:
                continue
            item_id = slot_info.get("id")
            if not item_id:
                continue

            item_data = ITEM_DATABASE.get(item_id)
            if not item_data:
                continue

            try:
                count = int(slot_info.get("count", 1))
            except (TypeError, ValueError):
                count = 1

            try:
                new_item = InventoryItem(
                    item_id=item_data["id"],
                    name=item_data["name"],
                    description=item_data.get("description", ""),
                    item_type=item_data.get("type", "consumable"),
                    image_path=item_data.get("image_path"),
                    stats=item_data.get("stats"),
                    max_stack=item_data.get("max_stack", 99),
                    rarity=item_data.get("rarity", "common"),
                )
                new_item.count = max(1, min(count, new_item.max_stack))

                # Проверяем, можно ли надеть предмет в этот слот
                if self._can_equip_to_slot(new_item, slot_name):
                    self.equipment_slots[slot_name] = new_item
            except Exception:
                continue

        # После восстановления экипировки пересчитываем бонусы
        recalculate_equipment_bonuses(self.player_stats, self.equipment_slots.values())
    
    # === МЕТОДЫ ДЛЯ РАБОТЫ С ПРЕДМЕТАМИ (ACS) ===
    
    def add_item(self, item_id: str, count: int = 1, **kwargs) -> bool:
        """Добавляет предмет в ACS инвентарь по ID."""
        # Ищем описание предмета в общей базе данных
        item_data = ITEM_DATABASE.get(item_id)
        
        if not item_data:
            print(f"[INVENTORY WARNING] Предмет {item_id} не найден")
            return False
        
        # Создаем предмет
        item_data.update(kwargs)
        item = InventoryItem(**item_data)
        item.count = count
        
        return self.add_item_to_free_slot(item)
    
    def add_item_to_free_slot(self, item: InventoryItem) -> bool:
        """Добавляет предмет в первый свободный слот ACS инвентаря."""
        # Сначала проверяем, можно ли сложить с существующим стаком
        for i, slot_item in enumerate(self.inventory_slots):
            if slot_item and slot_item.can_stack_with(item):
                slot_item.count += item.count
                if slot_item.count > slot_item.max_stack:
                    item.count = slot_item.count - slot_item.max_stack
                    slot_item.count = slot_item.max_stack
                else:
                    return True
        
        # Если не удалось сложить, ищем пустой слот
        for i, slot_item in enumerate(self.inventory_slots):
            if slot_item is None:
                self.inventory_slots[i] = item
                return True
        
        print(f"[INVENTORY WARNING] Нет свободных слотов для {item.name}")
        return False
    
    def remove_item(self, item_id: str, count: int = 1) -> bool:
        """Удаляет предмет из ACS инвентаря."""
        removed_count = 0
        
        for i, slot_item in enumerate(self.inventory_slots):
            if slot_item and slot_item.id == item_id:
                if slot_item.count > count:
                    slot_item.count -= count
                    removed_count = count
                    break
                else:
                    removed_count += slot_item.count
                    self.inventory_slots[i] = None
                    if removed_count >= count:
                        break
        
        return removed_count >= count
    
    def get_total_items(self) -> int:
        """Возвращает общее количество предметов в ACS инвентаре."""
        count = 0
        for item in self.inventory_slots:
            if item:
                count += item.count
        return count
    
    def _calculate_inventory_slot_positions(self, acs_x: int, acs_y: int):
        """Вычисляет позиции слотов инвентаря в ACS."""
        if not self.acs_image:
            return
            
        # Начальные координаты для сетки инвентаря в ACS
        # Левый верхний угол решетки берём из настроек (inventory_grid_start_x/y)
        inv_start_x = self.inventory_grid_start_x
        inv_start_y = self.inventory_grid_start_y
        
        slot_w = self.inventory_slot_width
        slot_h = self.inventory_slot_height
        spacing_x = self.inventory_slot_spacing_x
        spacing_y = self.inventory_slot_spacing_y
        cols = self.inventory_cols
        rows = self.inventory_visible_rows
        
        self.inventory_slots_positions = []
        
        for row in range(rows):
            for col in range(cols):
                x = inv_start_x + col * (slot_w + spacing_x)
                y = inv_start_y + row * (slot_h + spacing_y)
                self.inventory_slots_positions.append((x, y))

        # Обновляем скроллбар
        if self.inventory_total_rows > self.inventory_visible_rows:
            # Координаты ползунка берём из настроек (inventory_scroll_x/y),
            # а длину трека — из inventory_scroll_track_top/bottom
            slider_x = self.inventory_scroll_x
            slider_y = self.inventory_scroll_track_top
            slider_width = 18
            slider_height = max(0, self.inventory_scroll_track_bottom - self.inventory_scroll_track_top)

            self.inventory_scrollbar_rect = pygame.Rect(
                slider_x, slider_y, slider_width, slider_height
            )

            # Размер и позиция ползунка в зависимости от текущего скролла
            scroll_range_rows = self.inventory_total_rows - self.inventory_visible_rows
            thumb_min_height = 20
            thumb_height = max(
                thumb_min_height,
                int(slider_height * (self.inventory_visible_rows / self.inventory_total_rows)),
            )

            if scroll_range_rows > 0:
                max_thumb_offset = slider_height - thumb_height
                thumb_offset = int(
                    (self.inventory_scroll_row / scroll_range_rows) * max_thumb_offset
                )
            else:
                thumb_offset = 0

            self.inventory_scroll_thumb_rect = pygame.Rect(
                slider_x + 2,
                slider_y + thumb_offset,
                slider_width - 4,
                thumb_height,
            )
        else:
            self.inventory_scrollbar_rect = None
            self.inventory_scroll_thumb_rect = None

    def _set_inventory_scroll_row(self, row: int):
        """Устанавливает строку прокрутки инвентаря (ACS)."""
        max_row = max(0, self.inventory_total_rows - self.inventory_visible_rows)
        row = max(0, min(row, max_row))
        if row != self.inventory_scroll_row:
            self.inventory_scroll_row = row

    def _set_inventory_scroll_from_position(self, mouse_y: int):
        """Обновляет скролл инвентаря по позиции мыши на скроллбаре."""
        if not self.inventory_scrollbar_rect or self.inventory_total_rows <= self.inventory_visible_rows:
            return

        track_top = self.inventory_scrollbar_rect.top
        track_height = self.inventory_scrollbar_rect.height
        if track_height <= 0:
            return

        rel = (mouse_y - track_top) / track_height
        rel = max(0.0, min(1.0, rel))

        scroll_range_rows = self.inventory_total_rows - self.inventory_visible_rows
        target_row = int(round(rel * scroll_range_rows))
        self._set_inventory_scroll_row(target_row)

    def _visible_index_to_global(self, visible_index: int) -> int:
        """Преобразует индекс видимой ячейки 0..(cols*visible_rows-1) в глобальный индекс слота."""
        cols = self.inventory_cols
        row_visible = visible_index // cols
        col = visible_index % cols
        row_global = self.inventory_scroll_row + row_visible
        return row_global * cols + col
    
    def _calculate_equipment_slot_positions(self, acs_x: int, acs_y: int):
        """Вычисляет позиции слотов экипировки в ACS."""
        if not self.acs_image:
            return
            
        # Позиции для слотов экипировки (левая часть ACS)
        self.equipment_slots_positions = {
            "Голова": (acs_x + 400, acs_y + 100),
            "Шея": (acs_x + 400, acs_y + 200),
            "Плечи": (acs_x + 300, acs_y + 250),
            "Грудь": (acs_x + 400, acs_y + 300),
            "Руки": (acs_x + 500, acs_y + 250),
            "Правая рука": (acs_x + 600, acs_y + 350),
            "Левая рука": (acs_x + 200, acs_y + 350),
            "Кольцо 1": (acs_x + 300, acs_y + 450),
            "Кольцо 2": (acs_x + 500, acs_y + 450),  # Исправлено
            "Ноги": (acs_x + 400, acs_y + 500)
        }
    
    def _get_inventory_slot_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """Возвращает ИНДЕКС ВИДИМОГО слота инвентаря по позиции мыши (только в ACS)."""
        if not self.inventory_slots_positions:
            return None
        
        slot_w = self.inventory_slot_width
        slot_h = self.inventory_slot_height
        
        for i, (x, y) in enumerate(self.inventory_slots_positions):
            slot_rect = pygame.Rect(x, y, slot_w, slot_h)
            if slot_rect.collidepoint(pos):
                return i
        
        return None
    
    def _get_equipment_slot_at_position(self, pos: Tuple[int, int]) -> Optional[str]:
        """Возвращает название слота экипировки по позиции мыши (только в ACS)."""
        if not self.equipment_slots_positions:
            return None
        
        slot_size = InventoryItem.SLOT_SIZE
        
        for slot_name, (x, y) in self.equipment_slots_positions.items():
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)
            if slot_rect.collidepoint(pos):
                return slot_name
        
        return None
    
    def _get_chest_slot_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """Возвращает индекс слота сундука по позиции мыши (только в категории Хранилище)."""
        if not hasattr(self, 'current_chest_storage') or not self.current_chest_storage:
            return None
        
        # Параметры слотов сундука (должны совпадать с _draw_storage_slots)
        chest_slot_size = self.inventory_slot_width  # 132
        chest_slot_spacing = self.inventory_slot_spacing_x  # 10
        chest_cols = 6
        
        # Позиция сетки сундука (должна совпадать с _draw_storage_slots)
        # Вычисляем acs_x и acs_y так же, как в _draw_acs_interface
        if self.acs_image:
            acs_width = self.acs_image.get_width()
            acs_height = self.acs_image.get_height()
            acs_x = (config.VIRTUAL_WIDTH - acs_width) // 2
            acs_y = (config.VIRTUAL_HEIGHT - acs_height) // 2
        else:
            acs_x = 0
            acs_y = 0
        
        chest_grid_x = acs_x + 100
        chest_grid_y = acs_y + 300
        
        # Проверяем каждый слот
        for idx in range(self.current_chest_storage.max_slots):
            row = idx // chest_cols
            col = idx % chest_cols
            
            slot_x = chest_grid_x + col * (chest_slot_size + chest_slot_spacing)
            slot_y = chest_grid_y + row * (chest_slot_size + chest_slot_spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, chest_slot_size, chest_slot_size)
            
            if slot_rect.collidepoint(pos):
                return idx
        
        return None
    
    # === ОСНОВНЫЕ МЕТОДЫ ===
    
    def toggle_inventory(self):
        """Переключает состояние инвентаря-профиля (I)."""
        old_state = self.inventory_open
        self.inventory_open = not self.inventory_open
        
        # Закрываем ACS если открываем инвентарь-профиль
        if self.inventory_open:
            self.acs_open = False
            self._capture_background()
        else:
            self.background = None
            self.context_menu = None
            
        if config.DEBUG_MODE:
            print(f"[INVENTORY DEBUG] Инвентарь-профиль (I) переключен: {old_state} -> {self.inventory_open}")
    
    def toggle_acs(self):
        """Переключает состояние ACS слотов (O)."""
        old_state = self.acs_open
        self.acs_open = not self.acs_open
        
        # Закрываем инвентарь-профиль если открываем ACS
        if self.acs_open:
            self.inventory_open = False
            self._capture_background()
        else:
            self.acs_background = None
            self.context_menu = None
            
        if config.DEBUG_MODE:
            print(f"[INVENTORY DEBUG] ACS слоты (O) переключен: {old_state} -> {self.acs_open}")
    
    def _capture_background(self):
        """Сохраняет скриншот фона и останавливает звуки."""
        game = getattr(self.player_stats, 'game', None)
        if game and hasattr(game, 'virtual_screen'):
            self.background = game.virtual_screen.copy()
            self.acs_background = game.virtual_screen.copy()
        else:
            self.background = None
            self.acs_background = None
            
        # Остановить звук шагов у игрока
        if game and hasattr(game, 'player') and game.player:
            player = game.player
            if hasattr(player, '_steps_channel') and player._steps_channel:
                player._steps_channel.stop()
                player._steps_channel = None
            player._was_walking = False
            player.is_walking = False
    
    # === ОБРАБОТКА СОБЫТИЙ ДЛЯ ACS (O) ===
    
    def _handle_acs_mouse_click(self, mouse_pos):
        """Обработка нажатия мыши в ACS интерфейсе."""
        if self.context_menu:
            # Проверяем клик по контекстному меню
            self._handle_context_menu_click(mouse_pos)
            return
        
        # Проверяем клик по ползунку категорий
        if self._handle_slider_click(mouse_pos):
            return

        # Скроллбар инвентаря (категории "Инвентарь" и "Хранилище")
        if self.current_acs_category in (0, 2) and self.inventory_scrollbar_rect:
            if self.inventory_scrollbar_rect.collidepoint(mouse_pos):
                # Клик по области скроллбара — перемещаем ползунок
                self.inventory_dragging_scroll = True
                self._set_inventory_scroll_from_position(mouse_pos[1])
                return
        
        # Определяем, в какой слот кликнули
        slot_type = None
        slot_index = None  # глобальный индекс слота инвентаря
        visible_index = None
        slot_name = None
        item = None
        
        if self.current_acs_category == 0:  # Инвентарь
            visible_index = self._get_inventory_slot_at_position(mouse_pos)
            if visible_index is not None:
                slot_type = "inventory"
                slot_index = self._visible_index_to_global(visible_index)
                item = self.inventory_slots[slot_index]
        elif self.current_acs_category == 1:  # Экипировка
            slot_name = self._get_equipment_slot_at_position(mouse_pos)
            if slot_name is not None:
                slot_type = "equipment"
                item = self.equipment_slots[slot_name]
        elif self.current_acs_category == 2:  # Хранилище
            # Проверяем клик по слотам сундука
            chest_slot_index = self._get_chest_slot_at_position(mouse_pos)
            if chest_slot_index is not None:
                slot_type = "chest"
                slot_index = chest_slot_index
                if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                    item = self.current_chest_storage.get_item(chest_slot_index)
            else:
                # Проверяем клик по слотам инвентаря
                visible_index = self._get_inventory_slot_at_position(mouse_pos)
                if visible_index is not None:
                    slot_type = "inventory"
                    slot_index = self._visible_index_to_global(visible_index)
                    item = self.inventory_slots[slot_index]
        
        if slot_type and item:
            # Проверяем правый клик для контекстного меню
            if pygame.mouse.get_pressed()[2]:  # Правый клик
                self._open_context_menu(item, mouse_pos, slot_type, slot_index, slot_name)
            else:  # Левый клик
                # Начинаем перетаскивание
                self.dragged_item = item
                if slot_type == "inventory":
                    # Для расчета смещения используем координаты ВИДИМОГО слота
                    if visible_index is not None and 0 <= visible_index < len(self.inventory_slots_positions):
                        slot_x, slot_y = self.inventory_slots_positions[visible_index]
                    else:
                        slot_x, slot_y = mouse_pos
                    self.drag_offset = (
                        mouse_pos[0] - slot_x,
                        mouse_pos[1] - slot_y,
                    )
                    self.selected_slot = ("inventory", slot_index)
                elif slot_type == "equipment":
                    self.drag_offset = (mouse_pos[0] - self.equipment_slots_positions[slot_name][0],
                                      mouse_pos[1] - self.equipment_slots_positions[slot_name][1])
                    self.selected_slot = ("equipment", slot_name)
                elif slot_type == "chest":
                    # Убираем предмет из сундука
                    if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                        self.current_chest_storage.remove_item(slot_index)
                    self.drag_offset = (0, 0)
                    self.selected_slot = ("chest", slot_index)
                
                print(f"[ACS] Начато перетаскивание: {item.name}")
        elif slot_type and not item:
            # Клик по пустому слоту - если у нас есть перетаскиваемый предмет, кладем его
            if self.dragged_item:
                if slot_type == "chest":
                    # Кладем предмет в сундук
                    if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                        self.current_chest_storage.add_item(self.dragged_item, slot_index)
                        print(f"[ACS] Положен предмет {self.dragged_item.name} в сундук, слот {slot_index}")
                    self.dragged_item = None
                    self.selected_slot = None
                elif slot_type == "inventory":
                    # Кладем предмет в инвентарь
                    self.inventory_slots[slot_index] = self.dragged_item
                    print(f"[ACS] Положен предмет {self.dragged_item.name} в инвентарь, слот {slot_index}")
                    self.dragged_item = None
                    self.selected_slot = None
    
    def _handle_acs_mouse_release(self, mouse_pos):
        """Обработка отпускания мыши в ACS интерфейсе."""
        if not self.dragged_item:
            return
            
        # Определяем, куда бросаем предмет
        target_slot_type = None
        target_slot_index = None
        target_slot_name = None
        target_item = None
        
        if self.current_acs_category == 0:  # Инвентарь
            visible_index = self._get_inventory_slot_at_position(mouse_pos)
            if visible_index is not None:
                target_slot_type = "inventory"
                target_slot_index = self._visible_index_to_global(visible_index)
                target_item = self.inventory_slots[target_slot_index]
        elif self.current_acs_category == 1:  # Экипировка
            target_slot_name = self._get_equipment_slot_at_position(mouse_pos)
            if target_slot_name is not None:
                target_slot_type = "equipment"
                target_item = self.equipment_slots[target_slot_name]
        elif self.current_acs_category == 2:  # Хранилище
            # Проверяем сначала слоты сундука
            chest_slot_index = self._get_chest_slot_at_position(mouse_pos)
            if chest_slot_index is not None:
                target_slot_type = "chest"
                target_slot_index = chest_slot_index
                if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                    target_item = self.current_chest_storage.get_item(chest_slot_index)
            else:
                # Проверяем слоты инвентаря
                visible_index = self._get_inventory_slot_at_position(mouse_pos)
                if visible_index is not None:
                    target_slot_type = "inventory"
                    target_slot_index = self._visible_index_to_global(visible_index)
                    target_item = self.inventory_slots[target_slot_index]
        
        # Логика перемещения предметов
        if target_slot_type and self.selected_slot:
            self._move_item(self.selected_slot, (target_slot_type, target_slot_index, target_slot_name), target_item)
        
        self.dragged_item = None
        self.selected_slot = None
    
    def _move_item(self, source_slot, target_slot, target_item):
        """Перемещает предмет между слотами."""
        source_type, source_id = source_slot
        target_type, target_index, target_name = target_slot
        
        # Получаем источник
        source_item = None
        if source_type == "inventory":
            source_item = self.inventory_slots[source_id]
        elif source_type == "equipment":
            source_item = self.equipment_slots[source_id]
        elif source_type == "chest":
            if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                source_item = self.current_chest_storage.get_item(source_id)
        
        if not source_item:
            return
        
        # Проверяем, можно ли поместить предмет в слот экипировки
        if target_type == "equipment":
            if not self._can_equip_to_slot(source_item, target_name):
                print(f"[ACS] Нельзя надеть {source_item.name} в слот {target_name}")
                # Возвращаем предмет обратно
                if source_type == "chest":
                    if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                        self.current_chest_storage.add_item(source_item, source_id)
                elif source_type == "inventory":
                    self.inventory_slots[source_id] = source_item
                elif source_type == "equipment":
                    self.equipment_slots[source_id] = source_item
                return
        
        # Логика перемещения
        if target_item is None:
            # Пустой слот - перемещаем предмет
            # Удаляем из источника (уже удалено в _handle_acs_mouse_click для chest)
            if source_type == "inventory":
                self.inventory_slots[source_id] = None
            elif source_type == "equipment":
                self.equipment_slots[source_id] = None
            # Для chest уже удален в _handle_acs_mouse_click
            
            # Добавляем в цель
            if target_type == "inventory":
                self.inventory_slots[target_index] = source_item
            elif target_type == "equipment":
                self.equipment_slots[target_name] = source_item
            elif target_type == "chest":
                if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                    self.current_chest_storage.add_item(source_item, target_index)
        elif target_item.can_stack_with(source_item):
            # Можно сложить
            target_item.merge(source_item)
            # Удаляем из источника
            if source_type == "inventory":
                self.inventory_slots[source_id] = None
            elif source_type == "equipment":
                self.equipment_slots[source_id] = None
            # Для chest уже удален
        else:
            # Меняем предметы местами
            # Удаляем предметы из исходных мест
            if source_type == "inventory":
                self.inventory_slots[source_id] = None
            elif source_type == "equipment":
                self.equipment_slots[source_id] = None
            # Для chest уже удален
            
            if target_type == "inventory":
                self.inventory_slots[target_index] = None
            elif target_type == "equipment":
                self.equipment_slots[target_name] = None
            elif target_type == "chest":
                if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                    self.current_chest_storage.remove_item(target_index)
            
            # Размещаем предметы в новых местах
            if target_type == "inventory":
                self.inventory_slots[target_index] = source_item
            elif target_type == "equipment":
                self.equipment_slots[target_name] = source_item
            elif target_type == "chest":
                if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                    self.current_chest_storage.add_item(source_item, target_index)
            
            if source_type == "inventory":
                self.inventory_slots[source_id] = target_item
            elif source_type == "equipment":
                self.equipment_slots[source_id] = target_item
            elif source_type == "chest":
                if hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                    self.current_chest_storage.add_item(target_item, source_id)

        # После любого изменения слотов пересчитываем бонусы экипировки
        recalculate_equipment_bonuses(self.player_stats, self.equipment_slots.values())
    
    def _can_equip_to_slot(self, item: InventoryItem, slot_name: str) -> bool:
        """Проверяет, можно ли надеть предмет в указанный слот экипировки."""
        # Простая проверка по типу предмета
        slot_mapping = {
            "Голова": ["armor", "helmet"],
            "Грудь": ["armor", "chest"],
            "Ноги": ["armor", "legs"],
            "Правая рука": ["weapon", "shield"],
            "Левая рука": ["weapon", "shield"],
            "Кольцо 1": ["accessory", "ring"],
            "Кольцо 2": ["accessory", "ring"],
            "Шея": ["accessory", "amulet"]
        }
        
        allowed_types = slot_mapping.get(slot_name, [])
        return item.type in allowed_types
    
    def _handle_slider_click(self, mouse_pos) -> bool:
        """Обрабатывает клик по ползунку категорий. Возвращает True если клик был по ползунку."""
        if not hasattr(self, 'slider_rect'):
            return False
        
        if self.slider_rect.collidepoint(mouse_pos):
            # Определяем, по какой кнопке кликнули
            button_width = self.slider_rect.width // len(self.acs_categories)
            relative_x = mouse_pos[0] - self.slider_rect.x
            
            new_category = relative_x // button_width
            if 0 <= new_category < len(self.acs_categories):
                self.current_acs_category = new_category
                print(f"[ACS] Переключена категория: {self.acs_categories[new_category]}")
                return True
        
        return False
    
    # === КОНТЕКСТНОЕ МЕНЮ (ACS) ===
    
    def _open_context_menu(self, item: InventoryItem, pos: Tuple[int, int], 
                          slot_type: str, slot_index=None, slot_name=None):
        """Открывает контекстное меню для предмета в ACS."""
        self.context_menu = {
            "item": item,
            "slot_type": slot_type,
            "slot_index": slot_index,
            "slot_name": slot_name,
            "options": []
        }
        
        # Добавляем опции в зависимости от типа предмета
        if item.type == "consumable":
            self.context_menu["options"].append("Использовать")
        elif item.type in ["weapon", "armor", "accessory"]:
            if slot_type == "inventory":
                self.context_menu["options"].append("Надеть")
            elif slot_type == "equipment":
                self.context_menu["options"].append("Снять")
        
        self.context_menu["options"].extend([
            "Выбросить",
            "Разделить",
            "Информация"
        ])
        
        self.context_menu_pos = pos
        
        print(f"[ACS] Открыто контекстное меню для {item.name}")
    
    def _handle_context_menu_click(self, mouse_pos):
        """Обрабатывает клик по контекстному меню в ACS."""
        menu_x, menu_y = self.context_menu_pos
        option_height = 30
        
        for i, option in enumerate(self.context_menu["options"]):
            option_rect = pygame.Rect(menu_x, menu_y + i * option_height, 120, option_height)
            if option_rect.collidepoint(mouse_pos):
                self._execute_acs_context_option(option)
                break
        
        self.context_menu = None
    
    def _execute_acs_context_option(self, option: str):
        """Выполняет выбранную опцию контекстного меню в ACS."""
        item = self.context_menu["item"]
        slot_type = self.context_menu["slot_type"]
        
        if option == "Использовать":
            self._use_item_acs(item)
        elif option == "Надеть":
            self._equip_item_acs(item)
        elif option == "Снять":
            self._unequip_item_acs(item)
        elif option == "Выбросить":
            self._drop_item_acs(item)
        elif option == "Разделить":
            self._split_item_acs(item)
        elif option == "Информация":
            self._show_item_info(item)
    
    def _use_item_acs(self, item: InventoryItem):
        """Использует расходуемый предмет в ACS."""
        print(f"[ACS] Использован предмет: {item.name}")
        
        if item.id == "health_potion":
            heal_amount = item.stats.get("health_restore", 0)
            if hasattr(self.player_stats, 'health'):
                self.player_stats.health.heal(heal_amount)
                print(f"[ACS] Восстановлено {heal_amount} здоровья")
        
        # Уменьшаем количество
        item.count -= 1
        if item.count <= 0:
            # Удаляем предмет из слота
            if self.context_menu["slot_type"] == "inventory":
                index = self.context_menu["slot_index"]
                self.inventory_slots[index] = None
            elif self.context_menu["slot_type"] == "equipment":
                slot_name = self.context_menu["slot_name"]
                self.equipment_slots[slot_name] = None
    
    def _equip_item_acs(self, item: InventoryItem):
        """Надевает предмет из инвентаря в ACS."""
        print(f"[ACS] Попытка надеть предмет: {item.name}")
        # TODO: Реализовать логику надевания в подходящий слот экипировки
    
    def _unequip_item_acs(self, item: InventoryItem):
        """Снимает предмет экипировки в ACS."""
        slot_name = self.context_menu["slot_name"]
        print(f"[ACS] Снят предмет: {item.name} со слота {slot_name}")
        
        # Ищем пустой слот в инвентаре
        for i, slot_item in enumerate(self.inventory_slots):
            if slot_item is None:
                self.inventory_slots[i] = item
                self.equipment_slots[slot_name] = None
                print(f"[ACS] Предмет перемещен в инвентарь, слот {i}")
                return
        
        print(f"[ACS] Нет свободных слотов в инвентаре")
    
    def _drop_item_acs(self, item: InventoryItem):
        """Выбрасывает предмет из ACS."""
        print(f"[ACS] Выброшен предмет: {item.name} x{item.count}")
        
        # Удаляем предмет из слота
        if self.context_menu["slot_type"] == "inventory":
            index = self.context_menu["slot_index"]
            self.inventory_slots[index] = None
        elif self.context_menu["slot_type"] == "equipment":
            slot_name = self.context_menu["slot_name"]
            self.equipment_slots[slot_name] = None
    
    def _split_item_acs(self, item: InventoryItem):
        """Разделяет стак предметов в ACS."""
        if item.count <= 1:
            print("[ACS] Нельзя разделить стак из 1 предмета")
            return
        
        # Ищем пустой слот в инвентаре
        half_count = item.count // 2
        new_item = item.split(half_count)
        
        if new_item:
            if self.add_item_to_free_slot(new_item):
                print(f"[ACS] Стак разделен: {item.count} + {new_item.count}")
            else:
                # Если нет свободного слота, возвращаем предметы обратно
                item.merge(new_item)
                print("[ACS] Нет свободных слотов для разделения")
    
    def _show_item_info(self, item: InventoryItem):
        """Показывает информацию о предмете."""
        print(f"[ACS] Информация о предмете:")
        print(f"  Название: {item.name}")
        print(f"  Тип: {item.type}")
        print(f"  Редкость: {item.rarity}")
        print(f"  Описание: {item.description}")
        if item.stats:
            print(f"  Характеристики: {item.stats}")
        print(f"  Количество: {item.count}/{item.max_stack}")
    
    # === ОБРАБОТКА СОБЫТИЙ ДЛЯ ПРОФИЛЯ (I) ===
    
    def _handle_inventory_mouse_click(self, mouse_pos):
        """Обработка кликов в интерфейсе инвентаря-профиля."""
        # Проверяем клики по кнопкам прокачки атрибутов
        for attr_name, button_rect in self.attribute_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                if self.player_stats.spend_skill_point(attr_name):
                    print(f"[INVENTORY] Атрибут {self.player_stats.attributes[attr_name].display_name} увеличен")
                    print(f"[INVENTORY] Осталось очков: {self.player_stats.get_skill_points()}")
                else:
                    print(f"[INVENTORY] Не удалось увеличить атрибут")
                return True
        
        # Проверяем клик по ползунку категорий атрибутов
        if hasattr(self, 'attribute_slider_rect'):
            if self.attribute_slider_rect.collidepoint(mouse_pos):
                # Определяем, по какой кнопке кликнули
                button_width = self.attribute_slider_rect.width // len(self.attribute_categories)
                relative_x = mouse_pos[0] - self.attribute_slider_rect.x
                
                new_category = relative_x // button_width
                if 0 <= new_category < len(self.attribute_categories):
                    self.current_attribute_category = new_category
                    print(f"[INVENTORY] Переключена категория атрибутов: {self.attribute_categories[new_category]}")
                    return True
        
        return False
    
    def _handle_inventory_mouse_motion(self, mouse_pos):
        """Обработка движения мыши в интерфейсе инвентаря-профиля."""
        # Проверяем наведение на атрибуты для подсказок
        new_hovered_attribute = None
        
        # Проверяем каждую кнопку атрибута
        for attr_name, button_rect in self.attribute_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                new_hovered_attribute = attr_name
                break
        
        # Если изменился атрибут под курсором, сбрасываем таймер
        if new_hovered_attribute != self.hovered_attribute:
            self.hovered_attribute = new_hovered_attribute
            self.tooltip_timer = 0.0
        
        return False
    
    # === ОБРАБОТКА СОБЫТИЙ ===
    
    def handle_event(self, event, mouse_pos=None):
        """Обрабатывает события для инвентаря."""
        mouse_pos = mouse_pos or pygame.mouse.get_pos()
        
        if event.type == pygame.KEYDOWN:
            # ESC закрывает открытые окна
            if event.key == pygame.K_ESCAPE:
                if self.inventory_open:
                    self.toggle_inventory()
                    self._close_menu()
                elif self.acs_open:
                    # Если открыт сундук (категория Хранилище), закрываем через chest_handler
                    if self.current_acs_category == 2 and hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                        game = getattr(self.player_stats, 'game', None)
                        if game and hasattr(game, 'chest_handler'):
                            game.chest_handler.close()
                    else:
                        self.toggle_acs()
                        self._close_menu()
            
            # I - инвентарь-профиль
            elif event.key == pygame.K_i:
                self.toggle_inventory()
                if self.inventory_open:
                    self._open_menu("inventory_menu")
                else:
                    self._close_menu()
            
            # O - ACS (слоты)
            elif event.key == pygame.K_o:
                self.toggle_acs()
                if self.acs_open:
                    self._open_menu("acs_menu")
                else:
                    self._close_menu()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левый клик
                if self.inventory_open:
                    # Обрабатываем клики в профиле
                    self._handle_inventory_mouse_click(mouse_pos)
                elif self.acs_open:
                    # Обрабатываем клики в ACS
                    self._handle_acs_mouse_click(mouse_pos)
            elif event.button == 3:  # Правый клик
                if self.acs_open:
                    # Обрабатываем правый клик в ACS
                    self._handle_acs_mouse_click(mouse_pos)
            # Прокрутка колесом мыши для инвентаря ACS (категории 0 и 2)
            elif event.button in (4, 5) and self.acs_open and self.current_acs_category in (0, 2):
                # 4 - колесо вверх, 5 - вниз
                direction = -1 if event.button == 4 else 1
                self._set_inventory_scroll_row(self.inventory_scroll_row + direction)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.acs_open:
                # Завершаем перетаскивание предмета
                if self.dragged_item:
                    self._handle_acs_mouse_release(mouse_pos)
                # Завершаем перетаскивание скроллбара
                self.inventory_dragging_scroll = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.inventory_open:
                # Обновляем наведение для подсказок
                self._handle_inventory_mouse_motion(mouse_pos)
            elif self.acs_open and self.current_acs_category in (0, 2) and self.inventory_dragging_scroll:
                # Перетаскивание скроллбара инвентаря (категории 0 и 2)
                self._set_inventory_scroll_from_position(mouse_pos[1])
    
    def _open_menu(self, menu_type):
        """Обновляет состояние игры при открытии меню."""
        game = getattr(self.player_stats, 'game', None)
        if game and hasattr(game, 'game_state_manager'):
            if menu_type == "inventory_menu":
                game.game_state_manager.change_state("inventory_menu", self)
            elif menu_type == "acs_menu":
                game.game_state_manager.change_state("acs_menu", self)
    
    def _close_menu(self):
        """Обновляет состояние игры при закрытии меню."""
        game = getattr(self.player_stats, 'game', None)
        if game and hasattr(game, 'game_state_manager'):
            # Если закрываем хранилище, убедимся что сундук тоже закрыт
            if self.current_acs_category == 2 and hasattr(self, 'current_chest_storage') and self.current_chest_storage:
                if hasattr(game, 'chest_manager'):
                    game.chest_manager.save_chests()
                self.current_chest_storage = None
            
            game.game_state_manager.change_state("new_game", None)
            game.game_state_manager.current_menu = None
            if hasattr(game, 'player_ui') and game.player_ui:
                game.player_ui.just_closed_inventory = True
            if hasattr(game, 'talk_button') and hasattr(game.talk_button, 'force_show'):
                game.talk_button.force_show()
    
    def update(self, dt):
        """Обновляет состояние инвентаря."""
        # Обновляем таймер для подсказок
        if self.hovered_attribute:
            self.tooltip_timer += dt
    
    # === ОТРИСОВКА ===
    
    def draw(self, screen, mouse_pos=None):
        """Отрисовывает активный интерфейс."""
        if self.inventory_open:
            self._draw_inventory_profile(screen)  # I - профиль и характеристики
        elif self.acs_open:
            self._draw_acs_interface(screen)       # O - слоты инвентаря и экипировки
    
    def _draw_inventory_profile(self, screen):
        """Отрисовывает инвентарь-профиль (I) - только характеристики и профиль."""
        # Рисуем фон
        if self.background:
            if self.background.get_size() != screen.get_size():
                bg = pygame.transform.scale(self.background, screen.get_size())
            else:
                bg = self.background
            screen.blit(bg, (0, 0))
            # Затемнение
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
        
        # Рисуем сам инвентарь (только для профиля)
        if self.inventory_image:
            screen.blit(self.inventory_image, (config.VIRTUAL_WIDTH // 2, config.VIRTUAL_HEIGHT // 2))

        # Получаем ВСЕ характеристики для отображения
        stats_display = self.player_stats.get_all_stats_display()
        
        font = pygame.font.Font(None, 28)
        
        # Перевод названий на русский
        russian_names = {
            'health': 'Здоровье',
            'stamina': 'Выносливость',
            'mana': 'Мана',
            'experience': 'Опыт',
            'damage': 'Урон',
            'defense': 'Защита',
            'magic': 'Магия',
            'luck_stat': 'Удача',
            'carry_capacity': 'Грузоподъемность',
            'attack_speed': 'Скорость атаки',
            'stealth': 'Скрытность',
            'movement_speed': 'Скорость движения',
            'critical_chance': 'Шанс крита',
            'dodge_chance': 'Шанс уклонения'
        }
        
        base_x = config.VIRTUAL_WIDTH // 2 + 585
        base_y = config.VIRTUAL_HEIGHT // 2 + 100
        line_spacing = 36
        
        # Отображаем основные характеристики (первые 7)
        stats_items = list(stats_display.items())
        for i, (stat_name, value) in enumerate(stats_items[:7]):
            name = russian_names.get(stat_name, stat_name)
            stat_text = f"{name}: {value}"
            stat_surface = font.render(stat_text, True, (220, 220, 240))
            screen.blit(stat_surface, (base_x, base_y + i * line_spacing))
        
        # Профиль игрока
        if self.inventory_profile:
            profile_x = config.VIRTUAL_WIDTH // 2 + 135
            profile_y = config.VIRTUAL_WIDTH // 2 - 125
            screen.blit(self.inventory_profile, (profile_x, profile_y))
            
            font_large = pygame.font.Font(None, 32)
            nickname = "Алд"
            text_surface = font_large.render(nickname, True, (255, 255, 255))
            text_x = profile_x + (self.inventory_profile.get_width() - text_surface.get_width()) // 2
            text_y = profile_y + self.inventory_profile.get_height()
            screen.blit(text_surface, (text_x, text_y))
        
        # Ползунок категорий атрибутов
        self._draw_attribute_slider(screen)
        
        # Кнопки прокачки атрибутов (для текущей категории)
        self._draw_attribute_buttons(screen)
        
        # Отображаем подсказку если нужно
        if self.hovered_attribute and self.tooltip_timer >= self.tooltip_delay:
            self._draw_attribute_tooltip(screen, self.hovered_attribute)

    def _draw_attribute_slider(self, screen):
        """Отрисовывает ползунок категорий атрибутов."""
        slider_width = 400
        slider_height = 40
        slider_x = config.VIRTUAL_WIDTH // 2 + 135
        slider_y = config.VIRTUAL_HEIGHT // 2 - 125 + 180
        
        # Сохраняем rect ползунка для обработки кликов
        self.attribute_slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        
        # Фон ползунка
        pygame.draw.rect(screen, (60, 60, 60, 200), self.attribute_slider_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.attribute_slider_rect, 2)
        
        # Кнопки категорий
        button_width = slider_width // len(self.attribute_categories)
        font = pygame.font.Font(None, 22)
        
        for i, category in enumerate(self.attribute_categories):
            button_x = slider_x + i * button_width
            button_rect = pygame.Rect(button_x, slider_y, button_width, slider_height)
            
            # Подсветка текущей категории
            if i == self.current_attribute_category:
                pygame.draw.rect(screen, (80, 80, 120, 200), button_rect)
            
            # Текст категории
            text = font.render(category, True, (220, 220, 220))
            text_x = button_x + (button_width - text.get_width()) // 2
            text_y = slider_y + (slider_height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))
            
            # Разделитель между кнопками
            if i > 0:
                pygame.draw.line(screen, (100, 100, 100), 
                               (button_x, slider_y), 
                               (button_x, slider_y + slider_height), 1)
    
    def _draw_attribute_buttons(self, screen):
        """Отрисовывает кнопки для прокачки атрибутов."""
        font = pygame.font.Font(None, 24)
        
        # Позиции для атрибутов (под ползунком)
        start_x = config.VIRTUAL_WIDTH // 2 + 135
        start_y = config.VIRTUAL_HEIGHT // 2 - 125 + 240
        
        # Получаем очки прокачки
        skill_points = self.player_stats.get_skill_points()
        
        # Отображаем очки прокачки
        points_text = f"Очки прокачки: {skill_points}"
        points_surface = font.render(points_text, True, (255, 215, 0))
        screen.blit(points_surface, (start_x, start_y - 30))
        
        # Определяем категорию для отображения
        category_mapping = {
            "Физические": "physical",
            "Ментальные": "mental", 
            "Духовные": "spiritual",
            "Производные": "derived"
        }
        
        current_category = category_mapping.get(
            self.attribute_categories[self.current_attribute_category], 
            "physical"
        )
        
        # Получаем атрибуты для текущей категории
        category_attributes = self.player_stats.get_attributes_by_category(current_category)
        
        # Очищаем старые кнопки
        self.attribute_buttons = {}
        
        # Кнопки для каждого атрибута в категории
        for i, (attr_name, attribute) in enumerate(category_attributes.items()):
            y_pos = start_y + i * 35
            
            # Отображаем атрибут
            attr_text = attribute.get_display_value()
            attr_surface = font.render(attr_text, True, (200, 200, 200))
            screen.blit(attr_surface, (start_x, y_pos))
            
            # Кнопка "+" для прокачки (если есть очки и это не производный атрибут)
            if skill_points > 0 and attribute.category != "derived":
                button_rect = pygame.Rect(start_x + 220, y_pos, 25, 25)
                
                # Цвет кнопки в зависимости от возможности прокачки
                pygame.draw.rect(screen, (60, 100, 60), button_rect)
                pygame.draw.rect(screen, (100, 150, 100), button_rect, 2)
                
                plus_text = font.render("+", True, (220, 220, 220))
                screen.blit(plus_text, (start_x + 228, y_pos + 3))
                
                # Сохраняем кнопку для обработки кликов
                self.attribute_buttons[attr_name] = button_rect
            elif attribute.category == "derived":
                # Для производных атрибутов показываем информацию
                info_text = "(Автоматически)"
                info_surface = pygame.font.Font(None, 18).render(info_text, True, (150, 150, 150))
                screen.blit(info_surface, (start_x + 220, y_pos + 5))
    
    def _draw_attribute_tooltip(self, screen, attribute_name: str):
        """Отрисовывает подсказку для атрибута."""
        if attribute_name not in self.player_stats.attributes:
            return
        
        attribute = self.player_stats.attributes[attribute_name]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Получаем текст подсказки
        tooltip_text = attribute.get_tooltip()
        
        # Разбиваем текст на строки
        lines = tooltip_text.split('\n')
        font = pygame.font.Font(None, 22)
        
        # Вычисляем размеры подсказки
        max_width = 0
        total_height = 0
        rendered_lines = []
        
        for line in lines:
            text_surface = font.render(line, True, (220, 220, 220))
            rendered_lines.append(text_surface)
            max_width = max(max_width, text_surface.get_width())
            total_height += text_surface.get_height() + 2
        
        # Добавляем отступы
        padding = 10
        tooltip_width = max_width + padding * 2
        tooltip_height = total_height + padding * 2
        
        # Позиционируем подсказку (чтобы не выходила за экран)
        tooltip_x = mouse_x + 20
        tooltip_y = mouse_y + 20
        
        # Проверяем, не выходит ли подсказка за правый край экрана
        if tooltip_x + tooltip_width > screen.get_width():
            tooltip_x = mouse_x - tooltip_width - 20
        
        # Проверяем, не выходит ли подсказка за нижний край экрана
        if tooltip_y + tooltip_height > screen.get_height():
            tooltip_y = mouse_y - tooltip_height - 20
        
        # Рисуем фон подсказки
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(screen, (30, 30, 40, 240), tooltip_rect)
        pygame.draw.rect(screen, (80, 80, 100), tooltip_rect, 2)
        
        # Рисуем текст
        current_y = tooltip_y + padding
        for text_surface in rendered_lines:
            screen.blit(text_surface, (tooltip_x + padding, current_y))
            current_y += text_surface.get_height() + 2
    
    def _draw_acs_interface(self, screen):
        """Отрисовывает ACS интерфейс (O) - слоты инвентаря и экипировки."""
        # Рисуем фон
        if self.acs_background:
            if self.acs_background.get_size() != screen.get_size():
                bg = pygame.transform.scale(self.acs_background, screen.get_size())
            else:
                bg = self.acs_background
            screen.blit(bg, (0, 0))
            # Затемнение
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
        
        # Рисуем ACS интерфейс
        if self.acs_image:
            # Центрируем ACS на экране
            acs_x = (screen.get_width() - self.acs_image.get_width()) // 2
            acs_y = (screen.get_height() - self.acs_image.get_height()) // 2
            screen.blit(self.acs_image, (acs_x, acs_y))
            
            # Вычисляем позиции слотов
            self._calculate_inventory_slot_positions(acs_x, acs_y)
            if not self.equipment_slots_positions:
                self._calculate_equipment_slot_positions(acs_x, acs_y)
            
            # Отрисовываем в зависимости от выбранной категории
            if self.current_acs_category == 0:  # Инвентарь
                self._draw_inventory_slots(screen, acs_x, acs_y)
            elif self.current_acs_category == 1:  # Экипировка
                self._draw_equipment_slots(screen, acs_x, acs_y)
            elif self.current_acs_category == 2:  # Хранилище (заглушка)
                self._draw_storage_slots(screen, acs_x, acs_y)
            
            # Отрисовываем ползунок категорий
            self._draw_acs_slider(screen, acs_x, acs_y)
            
            # Заголовок текущей категории
            font = pygame.font.Font(None, 32)
            title = self.acs_categories[self.current_acs_category]
            title_surface = font.render(title, True, (255, 255, 255))
            title_x = acs_x + (self.acs_image.get_width() - title_surface.get_width()) // 2
            title_y = acs_y - 50
            screen.blit(title_surface, (title_x, title_y))
            
            # Отрисовываем перетаскиваемый предмет (если есть)
            if self.dragged_item:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # При перетаскивании убираем рамку редкости,
                # оставляем только иконку и счётчик.
                self.dragged_item.draw(
                    screen,
                    mouse_x - self.drag_offset[0],
                    mouse_y - self.drag_offset[1],
                    draw_rarity_border=False,
                )
            
            # Отрисовываем контекстное меню (если открыто)
            if self.context_menu:
                self._draw_context_menu(screen)
    
    def _draw_inventory_slots(self, screen, acs_x: int, acs_y: int):
        """Отрисовывает слоты инвентаря в ACS."""
        # Заголовок инвентаря
        font = pygame.font.Font(None, 28)
        total_slots = len(self.inventory_slots)
        title = f"Инвентарь ({total_slots} слотов)"
        title_surface = font.render(title, True, (220, 220, 220))
        # Центрируем заголовок над сеткой 4×8
        slot_w = self.inventory_slot_width
        slot_h = self.inventory_slot_height  # оставлено для читаемости, хотя ниже не используется
        spacing_x = self.inventory_slot_spacing_x
        grid_width = self.inventory_cols * (slot_w + spacing_x) - spacing_x
        # Используем те же базовые координаты, что и для решётки слотов
        inv_start_x = self.inventory_grid_start_x
        title_x = inv_start_x + grid_width // 2 - title_surface.get_width() // 2
        title_y = acs_y + 100
        screen.blit(title_surface, (title_x, title_y))
        
        # Отрисовываем слоты и предметы
        for visible_index, (x, y) in enumerate(self.inventory_slots_positions):
            slot_rect = pygame.Rect(x, y, slot_w, slot_h)

            # Глобальный индекс слота для этого видимого индекса
            global_index = self._visible_index_to_global(visible_index)
            if 0 <= global_index < len(self.inventory_slots):
                # В режиме отладки рисуем сетку (рамки всех слотов)
                if config.DEBUG_MODE:
                    pygame.draw.rect(screen, (100, 100, 100), slot_rect, 1)

                # Подсветка выбранного слота (только если не перетаскиваем предмет)
                if (
                    self.dragged_item is None
                    and self.selected_slot
                    and self.selected_slot[0] == "inventory"
                    and self.selected_slot[1] == global_index
                ):
                    pygame.draw.rect(screen, (150, 150, 50, 80), slot_rect, border_radius=4)

                # Предмет в слоте
                item = self.inventory_slots[global_index]
                if item and item is not self.dragged_item:
                    # Рисуем предмет внутри ячейки; если иконка меньше, она просто займет верхний‑левый угол
                    item.draw(screen, x, y)

        # Отрисовываем только ползунок (без линии‑трека), всегда видимый
        if self.inventory_scroll_thumb_rect:
            if self.inventory_scroll_thumb_image:
                # Масштабируем изображение под текущий размер ползунка
                thumb_surf = pygame.transform.smoothscale(
                    self.inventory_scroll_thumb_image,
                    (self.inventory_scroll_thumb_rect.width, self.inventory_scroll_thumb_rect.height),
                )
                screen.blit(thumb_surf, self.inventory_scroll_thumb_rect.topleft)
            else:
                # Фолбэк — простой прямоугольник, если картинка не загрузилась
                pygame.draw.rect(
                    screen,
                    (110, 110, 150),
                    self.inventory_scroll_thumb_rect,
                    border_radius=6,
                )
    
    def _draw_equipment_slots(self, screen, acs_x: int, acs_y: int):
        """Отрисовывает слоты экипировки в ACS."""
        # Заголовок экипировки
        font = pygame.font.Font(None, 28)
        title = "Экипировка персонажа"
        title_surface = font.render(title, True, (220, 220, 220))
        title_x = acs_x + 400 - title_surface.get_width() // 2
        title_y = acs_y + 50
        screen.blit(title_surface, (title_x, title_y))
        
        # Отрисовываем слоты экипировки
        for slot_name, (x, y) in self.equipment_slots_positions.items():
            # Рамка слота
            slot_rect = pygame.Rect(x, y, InventoryItem.SLOT_SIZE, InventoryItem.SLOT_SIZE)
            pygame.draw.rect(screen, (150, 150, 150), slot_rect, 2)
            
            # Подсветка выбранного слота (только если не перетаскиваем предмет)
            if (
                self.dragged_item is None
                and self.selected_slot
                and self.selected_slot[0] == "equipment"
                and self.selected_slot[1] == slot_name
            ):
                pygame.draw.rect(screen, (150, 150, 50, 100), slot_rect)
            
            # Предмет в слоте
            item = self.equipment_slots[slot_name]
            if item and item is not self.dragged_item:
                item.draw(screen, x, y)
            
            # Название слота
            font_small = pygame.font.Font(None, 16)
            text = font_small.render(slot_name, True, (200, 200, 200))
            text_x = x + (InventoryItem.SLOT_SIZE - text.get_width()) // 2
            text_y = y - 20
            screen.blit(text, (text_x, text_y))
    
    def _draw_storage_slots(self, screen, acs_x: int, acs_y: int):
        """Отрисовывает слоты хранилища сундука и инвентаря."""
        # Проверяем, есть ли открытый сундук
        if not hasattr(self, 'current_chest_storage') or not self.current_chest_storage:
            font = pygame.font.Font(None, 32)
            text = "Хранилище (в разработке)"
            text_surface = font.render(text, True, (200, 200, 200))
            text_x = acs_x + (self.acs_image.get_width() - text_surface.get_width()) // 2
            text_y = acs_y + (self.acs_image.get_height() - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
            return
        
        # Рисуем изображение сундука вместо ACS панели
        game = getattr(self.player_stats, 'game', None)
        if game and hasattr(game, 'chest_panel_img') and game.chest_panel_img:
            chest_img = game.chest_panel_img
            chest_x = (config.VIRTUAL_WIDTH - chest_img.get_width()) // 2
            chest_y = (config.VIRTUAL_HEIGHT - chest_img.get_height()) // 2
            screen.blit(chest_img, (chest_x, chest_y))
            # Обновляем координаты для отрисовки слотов
            acs_x = chest_x
            acs_y = chest_y
        
        # Параметры слотов сундука (левая часть)
        # Используем те же размеры что и для инвентаря
        chest_slot_size = self.inventory_slot_width  # 132
        chest_slot_spacing = self.inventory_slot_spacing_x  # 10
        chest_cols = 6
        chest_rows = 4  # 24 слота
        
        # Позиция сетки сундука (левая часть ACS панели)
        chest_grid_x = acs_x + 100
        chest_grid_y = acs_y + 300
        
        # Заголовок сундука
        font = pygame.font.Font(None, 28)
        title_text = "Сундук"
        title_surface = font.render(title_text, True, (220, 220, 220))
        title_x = chest_grid_x + (chest_cols * (chest_slot_size + chest_slot_spacing) - chest_slot_spacing) // 2 - title_surface.get_width() // 2
        title_y = chest_grid_y - 50
        screen.blit(title_surface, (title_x, title_y))
        
        # Отрисовываем слоты сундука
        for idx in range(self.current_chest_storage.max_slots):
            row = idx // chest_cols
            col = idx % chest_cols
            
            slot_x = chest_grid_x + col * (chest_slot_size + chest_slot_spacing)
            slot_y = chest_grid_y + row * (chest_slot_size + chest_slot_spacing)
            slot_rect = pygame.Rect(slot_x, slot_y, chest_slot_size, chest_slot_size)
            
            # Рисуем рамку слота
            if config.DEBUG_MODE:
                pygame.draw.rect(screen, (100, 100, 100), slot_rect, 1)
            
            # Подсветка выбранного слота (только если не перетаскиваем предмет)
            if (
                self.dragged_item is None
                and self.selected_slot
                and self.selected_slot[0] == "chest"
                and self.selected_slot[1] == idx
            ):
                pygame.draw.rect(screen, (150, 150, 50, 80), slot_rect, border_radius=4)
            
            # Рисуем предмет в слоте (если есть)
            item = self.current_chest_storage.get_item(idx)
            if item and item is not self.dragged_item:
                item.draw(screen, slot_x, slot_y)
        
        # Отрисовываем инвентарь справа (используем ту же логику что для обычного инвентаря)
        # Заголовок инвентаря
        title_text = "Инвентарь"
        title_surface = font.render(title_text, True, (220, 220, 220))
        inv_start_x = self.inventory_grid_start_x
        slot_w = self.inventory_slot_width
        spacing_x = self.inventory_slot_spacing_x
        grid_width = self.inventory_cols * (slot_w + spacing_x) - spacing_x
        title_x = inv_start_x + grid_width // 2 - title_surface.get_width() // 2
        title_y = acs_y + 250
        screen.blit(title_surface, (title_x, title_y))
        
        # Отрисовываем слоты и предметы инвентаря
        slot_h = self.inventory_slot_height
        for visible_index, (x, y) in enumerate(self.inventory_slots_positions):
            slot_rect = pygame.Rect(x, y, slot_w, slot_h)

            # Глобальный индекс слота для этого видимого индекса
            global_index = self._visible_index_to_global(visible_index)
            if 0 <= global_index < len(self.inventory_slots):
                # В режиме отладки рисуем сетку (рамки всех слотов)
                if config.DEBUG_MODE:
                    pygame.draw.rect(screen, (100, 100, 100), slot_rect, 1)

                # Подсветка выбранного слота (только если не перетаскиваем предмет)
                if (
                    self.dragged_item is None
                    and self.selected_slot
                    and self.selected_slot[0] == "inventory"
                    and self.selected_slot[1] == global_index
                ):
                    pygame.draw.rect(screen, (150, 150, 50, 80), slot_rect, border_radius=4)

                # Предмет в слоте
                item = self.inventory_slots[global_index]
                if item and item is not self.dragged_item:
                    item.draw(screen, x, y)

        # Отрисовываем только ползунок инвентаря
        if self.inventory_scroll_thumb_rect:
            if self.inventory_scroll_thumb_image:
                thumb_surf = pygame.transform.smoothscale(
                    self.inventory_scroll_thumb_image,
                    (self.inventory_scroll_thumb_rect.width, self.inventory_scroll_thumb_rect.height),
                )
                screen.blit(thumb_surf, self.inventory_scroll_thumb_rect.topleft)
            else:
                pygame.draw.rect(
                    screen,
                    (110, 110, 150),
                    self.inventory_scroll_thumb_rect,
                    border_radius=6,
                )
    
    def _draw_acs_slider(self, screen, acs_x: int, acs_y: int):
        """Отрисовывает ползунок категорий в ACS."""
        slider_width = 400
        slider_height = 40
        slider_x = acs_x + (self.acs_image.get_width() - slider_width) // 2
        slider_y = acs_y + self.acs_image.get_height() - 80
        
        # Сохраняем rect ползунка для обработки кликов
        self.slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        
        # Фон ползунка
        pygame.draw.rect(screen, (60, 60, 60, 200), self.slider_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.slider_rect, 2)
        
        # Кнопки категорий
        button_width = slider_width // len(self.acs_categories)
        font = pygame.font.Font(None, 22)
        
        for i, category in enumerate(self.acs_categories):
            button_x = slider_x + i * button_width
            button_rect = pygame.Rect(button_x, slider_y, button_width, slider_height)
            
            # Подсветка текущей категории
            if i == self.current_acs_category:
                pygame.draw.rect(screen, (80, 80, 120, 200), button_rect)
            
            # Текст категории
            text = font.render(category, True, (220, 220, 220))
            text_x = button_x + (button_width - text.get_width()) // 2
            text_y = slider_y + (slider_height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))
            
            # Разделитель между кнопками
            if i > 0:
                pygame.draw.line(screen, (100, 100, 100), 
                               (button_x, slider_y), 
                               (button_x, slider_y + slider_height), 1)
    
    def _draw_context_menu(self, screen):
        """Отрисовывает контекстное меню."""
        menu_x, menu_y = self.context_menu_pos
        option_height = 30
        option_width = 120
        
        # Фон меню
        menu_rect = pygame.Rect(menu_x, menu_y, 
                               option_width, 
                               len(self.context_menu["options"]) * option_height)
        pygame.draw.rect(screen, (40, 40, 40, 220), menu_rect)
        pygame.draw.rect(screen, (100, 100, 100), menu_rect, 1)
        
        # Опции меню
        font = pygame.font.Font(None, 24)
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(self.context_menu["options"]):
            option_rect = pygame.Rect(menu_x, menu_y + i * option_height, option_width, option_height)
            
            # Подсветка при наведении
            if option_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (60, 60, 60), option_rect)
            
            # Текст опции
            text = font.render(option, True, (220, 220, 220))
            text_x = menu_x + 10
            text_y = menu_y + i * option_height + (option_height - text.get_height()) // 2
            screen.blit(text, (text_x, text_y))
    
    def draw_acs(self, screen):
        """Публичный метод для отрисовки ACS (для совместимости)."""
        self._draw_acs_interface(screen)