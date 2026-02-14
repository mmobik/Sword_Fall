"""
Модуль для загрузки всех предметов из JSON файлов.
Загружает предметы из weapons.json, armor.json, consumables.json, artifacts.json, resources.json
"""

import json
import os
from typing import Dict, Any, Optional

# Глобальная база данных всех предметов
ITEMS_DATABASE: Dict[str, Dict[str, Any]] = {}


def load_items_from_json(file_path: str) -> Dict[str, Any]:
    """
    Загружает предметы из JSON файла.
    
    Args:
        file_path: Путь к JSON файлу
        
    Returns:
        Словарь с предметами {item_id: item_data}
    """
    try:
        if not os.path.exists(file_path):
            print(f"[ITEMS LOADER] Файл не найден: {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Если это пустой список или список, возвращаем пустой словарь
        if isinstance(data, list):
            if len(data) == 0:
                return {}  # Пустой файл
            # Если список не пустой, пытаемся преобразовать (но обычно это словарь)
            return {}
        
        # Если это словарь, возвращаем как есть
        if isinstance(data, dict):
            return data
        
        return {}
    except json.JSONDecodeError as e:
        print(f"[ITEMS LOADER] Ошибка парсинга JSON {file_path}: {e}")
        return {}
    except Exception as e:
        print(f"[ITEMS LOADER] Ошибка загрузки {file_path}: {e}")
        return {}


def normalize_item_data(item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Нормализует данные предмета для единообразного использования.
    Преобразует формат JSON в формат, совместимый с InventoryItem.
    
    Args:
        item_id: ID предмета
        item_data: Данные предмета из JSON
        
    Returns:
        Нормализованные данные предмета
    """
    normalized = {
        "id": item_id,
        "name": item_data.get("name", item_id),
        "description": item_data.get("description", ""),
        "type": item_data.get("type", "consumable"),
        "rarity": item_data.get("rarity", "common"),
        "stats": item_data.get("stats", {}),
        "max_stack": item_data.get("max_stack", 1),
    }
    
    # Обрабатываем путь к изображению (может быть icon или image_path)
    if "icon" in item_data:
        normalized["image_path"] = item_data["icon"]
    elif "image_path" in item_data:
        normalized["image_path"] = item_data["image_path"]
    elif "sprite" in item_data:
        normalized["image_path"] = item_data["sprite"]
    else:
        normalized["image_path"] = None
    
    # Добавляем дополнительные поля из JSON
    if "requirements" in item_data:
        normalized["requirements"] = item_data["requirements"]
    if "value" in item_data:
        normalized["value"] = item_data["value"]
    if "drop_chance" in item_data:
        normalized["drop_chance"] = item_data["drop_chance"]
    if "origin" in item_data:
        normalized["origin"] = item_data["origin"]
    if "weapon_type" in item_data:
        normalized["weapon_type"] = item_data["weapon_type"]
    
    return normalized


def load_all_items(items_dir: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Загружает все предметы из всех JSON файлов в папке items.
    
    Args:
        items_dir: Путь к папке с JSON файлами. Если None, используется Game/items
        
    Returns:
        Словарь всех предметов {item_id: normalized_item_data}
    """
    global ITEMS_DATABASE
    
    if items_dir is None:
        # Определяем путь относительно этого файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        items_dir = current_dir
    
    # Список файлов для загрузки
    json_files = [
        ("weapons.json", "weapon"),
        ("armor.json", "armor"),
        ("consumables.json", "consumable"),
        ("artifacts.json", "artifact"),
        ("resources.json", "resource"),
    ]
    
    all_items = {}
    
    for filename, default_type in json_files:
        file_path = os.path.join(items_dir, filename)
        items = load_items_from_json(file_path)
        
        # Нормализуем каждый предмет
        for item_id, item_data in items.items():
            # Устанавливаем тип по умолчанию, если не указан
            if "type" not in item_data:
                item_data["type"] = default_type
            
            normalized = normalize_item_data(item_id, item_data)
            all_items[item_id] = normalized
    
    # Сохраняем в глобальную базу данных
    ITEMS_DATABASE = all_items
    
    print(f"[ITEMS LOADER] Загружено предметов: {len(all_items)}")
    return all_items


def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    """
    Получает данные предмета по ID.
    
    Args:
        item_id: ID предмета
        
    Returns:
        Данные предмета или None
    """
    return ITEMS_DATABASE.get(item_id)


def get_all_items() -> Dict[str, Dict[str, Any]]:
    """
    Возвращает все загруженные предметы.
    
    Returns:
        Словарь всех предметов
    """
    # Если база данных пуста, пытаемся перезагрузить
    if not ITEMS_DATABASE:
        print("[ITEMS LOADER] База данных пуста, пытаемся перезагрузить...")
        load_all_items()
    return ITEMS_DATABASE.copy()


def reload_items(items_dir: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Перезагружает все предметы из JSON файлов.
    
    Args:
        items_dir: Путь к папке с JSON файлами
        
    Returns:
        Словарь всех предметов
    """
    return load_all_items(items_dir)

