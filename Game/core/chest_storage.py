"""
Модуль хранилища сундуков.

Содержит классы для управления содержимым сундуков в игре,
включая хранение предметов и сохранение состояния.
"""

import json
import os
from typing import Optional, Dict, List, Any
from UI.items import InventoryItem
from UI.equipment_data import ITEM_DATABASE
from core.config import config


class ChestStorage:
    """
    Класс для хранения содержимого одного сундука.
    """
    
    def __init__(self, chest_id: str, max_slots: int = 24):
        """
        Инициализирует хранилище сундука.
        
        Args:
            chest_id: Уникальный идентификатор сундука
            max_slots: Максимальное количество слотов в сундуке
        """
        self.chest_id = chest_id
        self.max_slots = max_slots
        self.slots: List[Optional[InventoryItem]] = [None] * max_slots
    
    def add_item(self, item: InventoryItem, slot_index: Optional[int] = None) -> bool:
        """
        Добавляет предмет в сундук.
        
        Args:
            item: Предмет для добавления
            slot_index: Индекс слота (если None, ищет первый свободный)
            
        Returns:
            True если предмет добавлен, False иначе
        """
        if slot_index is not None:
            # Добавляем в конкретный слот
            if 0 <= slot_index < self.max_slots:
                self.slots[slot_index] = item
                return True
            return False
        else:
            # Ищем первый свободный слот
            for i in range(self.max_slots):
                if self.slots[i] is None:
                    self.slots[i] = item
                    return True
            return False
    
    def remove_item(self, slot_index: int) -> Optional[InventoryItem]:
        """
        Удаляет предмет из слота.
        
        Args:
            slot_index: Индекс слота
            
        Returns:
            Удаленный предмет или None
        """
        if 0 <= slot_index < self.max_slots:
            item = self.slots[slot_index]
            self.slots[slot_index] = None
            return item
        return None
    
    def get_item(self, slot_index: int) -> Optional[InventoryItem]:
        """
        Получает предмет из слота без удаления.
        
        Args:
            slot_index: Индекс слота
            
        Returns:
            Предмет или None
        """
        if 0 <= slot_index < self.max_slots:
            return self.slots[slot_index]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует хранилище в словарь для сохранения.
        
        Returns:
            Словарь с данными хранилища
        """
        items_data = []
        for idx, item in enumerate(self.slots):
            if item:
                items_data.append({
                    "slot_index": idx,
                    "id": item.id,
                    "count": item.count
                })
        
        return {
            "chest_id": self.chest_id,
            "max_slots": self.max_slots,
            "items": items_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChestStorage':
        """
        Создает хранилище из словаря.
        
        Args:
            data: Словарь с данными хранилища
            
        Returns:
            Новый объект ChestStorage
        """
        chest_id = data.get("chest_id", "unknown")
        max_slots = data.get("max_slots", 24)
        storage = cls(chest_id, max_slots)
        
        # Восстанавливаем предметы
        for item_data in data.get("items", []):
            try:
                slot_index = int(item_data.get("slot_index"))
                item_id = item_data.get("id")
                count = int(item_data.get("count", 1))
            except (TypeError, ValueError):
                continue
            
            if item_id is None or not (0 <= slot_index < max_slots):
                continue
            
            # Получаем данные предмета из базы
            item_info = ITEM_DATABASE.get(item_id)
            if not item_info:
                continue
            
            try:
                item = InventoryItem(
                    item_id=item_info["id"],
                    name=item_info["name"],
                    description=item_info.get("description", ""),
                    item_type=item_info.get("type", "consumable"),
                    image_path=item_info.get("image_path"),
                    stats=item_info.get("stats"),
                    max_stack=item_info.get("max_stack", 99),
                    rarity=item_info.get("rarity", "common"),
                )
                item.count = max(1, min(count, item.max_stack))
                storage.slots[slot_index] = item
            except Exception as e:
                if config.DEBUG_MODE:
                    print(f"[CHEST_STORAGE] Ошибка загрузки предмета {item_id}: {e}")
                continue
        
        return storage


class ChestManager:
    """
    Менеджер для управления всеми сундуками в игре.
    """
    
    def __init__(self):
        """Инициализирует менеджер сундуков."""
        self.chests: Dict[str, ChestStorage] = {}
        self.save_file = "Game/userdata/chests.json"
        self.load_chests()
    
    def get_or_create_chest(self, chest_id: str, max_slots: int = 24) -> ChestStorage:
        """
        Получает существующий сундук или создает новый.
        
        Args:
            chest_id: Уникальный идентификатор сундука
            max_slots: Максимальное количество слотов
            
        Returns:
            Объект ChestStorage
        """
        if chest_id not in self.chests:
            self.chests[chest_id] = ChestStorage(chest_id, max_slots)
            if config.DEBUG_MODE:
                print(f"[CHEST_MANAGER] Создан новый сундук: {chest_id}")
        return self.chests[chest_id]
    
    def save_chests(self):
        """Сохраняет все сундуки в файл."""
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            
            # Преобразуем все сундуки в словари
            chests_data = {
                chest_id: chest.to_dict()
                for chest_id, chest in self.chests.items()
            }
            
            # Сохраняем в файл
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(chests_data, f, ensure_ascii=False, indent=2)
            
            if config.DEBUG_MODE:
                print(f"[CHEST_MANAGER] Сохранено {len(self.chests)} сундуков")
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"[CHEST_MANAGER] Ошибка сохранения сундуков: {e}")
    
    def load_chests(self):
        """Загружает все сундуки из файла."""
        if not os.path.exists(self.save_file):
            if config.DEBUG_MODE:
                print(f"[CHEST_MANAGER] Файл сохранения не найден: {self.save_file}")
            return
        
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                chests_data = json.load(f)
            
            # Восстанавливаем сундуки
            for chest_id, chest_data in chests_data.items():
                self.chests[chest_id] = ChestStorage.from_dict(chest_data)
            
            if config.DEBUG_MODE:
                print(f"[CHEST_MANAGER] Загружено {len(self.chests)} сундуков")
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"[CHEST_MANAGER] Ошибка загрузки сундуков: {e}")
    
    def clear_all(self):
        """Очищает все сундуки (для отладки)."""
        self.chests.clear()
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        if config.DEBUG_MODE:
            print("[CHEST_MANAGER] Все сундуки очищены")

