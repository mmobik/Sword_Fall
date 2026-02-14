"""
Боевая система игры.

Пока что отвечает только за отображение оружия и управление спрайтами игрока
в зависимости от экипированного оружия.
"""

from typing import Optional, Dict, Any
import os
from UI.items import InventoryItem
from core.pathutils import resource_path
from core.config import config


class CombatSystem:
    """
    Класс боевой системы.
    
    Пока что отвечает за:
    - Определение состояния игрока (с оружием / без оружия)
    - Управление путями к спрайтам в зависимости от экипировки
    - Подготовка каркаса для смены спрайтов оружия и доспехов
    """
    
    # Базовые пути к спрайтам
    # Используем точные пути как указано пользователем
    UNARMED_SPRITE_PATH = "Game/assets/Sprites/player/unarmed"
    ARMED_SPRITE_PATH = "Game/assets/Sprites/player/armed"
    
    def __init__(self, player=None):
        """
        Инициализация боевой системы.
        
        Args:
            player: Ссылка на объект игрока (опционально).
        """
        self.player = player
        self._current_weapon: Optional[InventoryItem] = None
        self._current_armor: Optional[Dict[str, Optional[InventoryItem]]] = {}
        
    def get_equipped_weapon(self, inventory) -> Optional[InventoryItem]:
        """
        Получает экипированное оружие из инвентаря.
        
        Args:
            inventory: Объект инвентаря с equipment_slots.
            
        Returns:
            Экипированное оружие или None.
        """
        if not inventory or not hasattr(inventory, 'equipment_slots'):
            return None
            
        # Проверяем слоты для оружия
        weapon_slots = ["Правая рука", "Левая рука"]
        for slot_name in weapon_slots:
            weapon = inventory.equipment_slots.get(slot_name)
            if weapon and isinstance(weapon, InventoryItem):
                # Проверяем, что это оружие
                if weapon.type == "weapon" or hasattr(weapon, 'weapon_type'):
                    return weapon
                    
        return None
    
    def is_armed(self, inventory) -> bool:
        """
        Проверяет, экипировано ли оружие.
        
        Args:
            inventory: Объект инвентаря с equipment_slots.
            
        Returns:
            True, если оружие экипировано, иначе False.
        """
        return self.get_equipped_weapon(inventory) is not None
    
    def get_sprite_state(self, inventory) -> str:
        """
        Определяет состояние спрайта (armed/unarmed).
        
        Args:
            inventory: Объект инвентаря с equipment_slots.
            
        Returns:
            "armed" если оружие экипировано, "unarmed" иначе.
        """
        return "armed" if self.is_armed(inventory) else "unarmed"
    
    def get_sprite_path(self, inventory, animation_name: str) -> str:
        """
        Получает путь к спрайту для конкретной анимации.
        
        Args:
            inventory: Объект инвентаря с equipment_slots.
            animation_name: Имя анимации (например, "idle_front", "run_right").
            
        Returns:
            Полный путь к файлу спрайта (нормализованный для использования с resource_path).
        """
        state = self.get_sprite_state(inventory)
        
        # Маппинг имен анимаций к именам файлов
        animation_mapping = {
            "idle_front": "idle_front.png",
            "idle_right": "idle_right.png",
            "idle_left": "idle_left.png",
            "idle_back": "idle_back.png",
            "run_right": "run_right.png",
            "run_left": "run_left.png",
            "run_up": "run_up.png",
            "run_down": "run_down.png",
        }
        
        filename = animation_mapping.get(animation_name, "idle_front.png")
        
        # Если состояние armed, проверяем наличие файла
        # Если файла нет, используем fallback на unarmed
        if state == "armed":
            base_path = self.ARMED_SPRITE_PATH
            # Проверяем существование файла (используем resource_path для проверки)
            from core.pathutils import resource_path
            full_path = f"{base_path}/{filename}"
            full_path_normalized = full_path.replace("\\", "/")
            absolute_path = resource_path(full_path_normalized)
            
            # Если файл существует, используем его
            if os.path.exists(absolute_path):
                return full_path_normalized
            # Иначе используем fallback на unarmed
            else:
                if config.DEBUG_MODE:
                    print(f"[COMBAT] Файл {full_path_normalized} не найден, используем fallback на unarmed")
                base_path = self.UNARMED_SPRITE_PATH
        else:
            base_path = self.UNARMED_SPRITE_PATH
        
        # Используем os.path.join для кроссплатформенности, но возвращаем с forward slashes
        # так как resource_path ожидает такой формат
        full_path = f"{base_path}/{filename}"
        return full_path.replace("\\", "/")
    
    def update_equipment(self, inventory):
        """
        Обновляет информацию об экипировке.
        
        Args:
            inventory: Объект инвентаря с equipment_slots.
        """
        self._current_weapon = self.get_equipped_weapon(inventory)
        
        # Подготовка для будущего использования доспехов
        if inventory and hasattr(inventory, 'equipment_slots'):
            armor_slots = ["Голова", "Грудь", "Руки", "Ноги", "Плечи", "Плащ"]
            for slot_name in armor_slots:
                self._current_armor[slot_name] = inventory.equipment_slots.get(slot_name)
    
    def get_weapon_sprite_variant(self, weapon: Optional[InventoryItem]) -> Optional[str]:
        """
        Получает вариант спрайта оружия (для будущего использования).
        
        Пока что возвращает None, но в будущем может возвращать путь
        к специфичному спрайту оружия.
        
        Args:
            weapon: Объект оружия.
            
        Returns:
            Путь к спрайту оружия или None для использования базового.
        """
        if not weapon:
            return None
            
        # В будущем здесь можно будет возвращать путь к спрайту
        # на основе weapon.id или weapon.weapon_type
        # Например: f"Game/assets/Sprites/player/weapons/{weapon.id}.png"
        # 
        # Каркас для будущей реализации:
        # if hasattr(weapon, 'sprite_path') and weapon.sprite_path:
        #     return weapon.sprite_path
        # elif hasattr(weapon, 'weapon_type'):
        #     return f"Game/assets/Sprites/player/weapons/{weapon.weapon_type}/{weapon.id}.png"
        return None
    
    def get_armor_sprite_variant(self, armor_slot: str, armor: Optional[InventoryItem]) -> Optional[str]:
        """
        Получает вариант спрайта доспеха (для будущего использования).
        
        Args:
            armor_slot: Название слота доспеха (например, "Голова", "Грудь", "Ноги").
            armor: Объект доспеха.
            
        Returns:
            Путь к спрайту доспеха или None для использования базового.
        """
        if not armor:
            return None
            
        # В будущем здесь можно будет возвращать путь к спрайту
        # на основе armor.id или armor.type
        # 
        # Каркас для будущей реализации:
        # if hasattr(armor, 'sprite_path') and armor.sprite_path:
        #     return armor.sprite_path
        # 
        # # Маппинг слотов на подпапки
        # slot_mapping = {
        #     "Голова": "helmet",
        #     "Грудь": "chest",
        #     "Руки": "arms",
        #     "Ноги": "legs",
        #     "Плечи": "shoulders",
        #     "Плащ": "cloak"
        # }
        # 
        # subfolder = slot_mapping.get(armor_slot, "misc")
        # return f"Game/assets/Sprites/player/armor/{subfolder}/{armor.id}.png"
        return None
    
    def get_combined_sprite_path(self, inventory, animation_name: str, 
                                 weapon_sprite: Optional[str] = None,
                                 armor_sprites: Optional[Dict[str, Optional[str]]] = None) -> str:
        """
        Получает комбинированный путь к спрайту с учетом оружия и доспехов.
        
        Это каркас для будущей реализации, где спрайты оружия и доспехов
        могут накладываться поверх базового спрайта игрока.
        
        Args:
            inventory: Объект инвентаря с equipment_slots.
            animation_name: Имя анимации.
            weapon_sprite: Путь к спрайту оружия (опционально).
            armor_sprites: Словарь путей к спрайтам доспехов по слотам (опционально).
            
        Returns:
            Базовый путь к спрайту (пока что без комбинирования).
        """
        # Пока что возвращаем базовый путь
        # В будущем здесь можно будет комбинировать спрайты
        return self.get_sprite_path(inventory, animation_name)

