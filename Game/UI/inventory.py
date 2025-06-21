"""
Система инвентаря для игрока.
Включает характеристики, экипировку и предметы.
"""

import pygame
import os
from typing import Dict, List, Optional, Tuple
from level.player_stats import PlayerStats
from core.config import config


class InventoryItem:
    """Класс для предметов инвентаря."""
    
    def __init__(self, name: str, item_type: str, image_path: Optional[str] = None, stats: Optional[Dict] = None):
        self.name = name
        self.item_type = item_type  # weapon, armor, consumable, etc.
        self.image_path = image_path
        self.stats = stats or {}
        self.image: Optional[pygame.Surface] = None
        self._load_image()
    
    def _load_image(self):
        """Загружает изображение предмета."""
        if self.image_path:
            try:
                self.image = pygame.image.load(self.image_path).convert_alpha()
            except Exception as e:
                print(f"[INVENTORY ERROR] Ошибка загрузки изображения {self.image_path}: {e}")
                self.image = None


class Equipment:
    """Класс для экипировки персонажа."""
    
    def __init__(self):
        self.slots: Dict[str, Optional[InventoryItem]] = {
            "weapon": None,
            "armor": None,
            "helmet": None,
            "gloves": None,
            "boots": None,
            "accessory": None
        }
    
    def equip_item(self, item: InventoryItem, slot: str) -> Optional[InventoryItem]:
        """Экипирует предмет. Возвращает предыдущий предмет в слоте."""
        if slot not in self.slots:
            return None
        
        previous_item = self.slots[slot]
        self.slots[slot] = item
        return previous_item
    
    def unequip_item(self, slot: str) -> Optional[InventoryItem]:
        """Снимает предмет из слота."""
        if slot not in self.slots:
            return None
        
        item = self.slots[slot]
        self.slots[slot] = None
        return item
    
    def get_equipped_stats(self) -> Dict:
        """Возвращает суммарные характеристики экипировки."""
        total_stats: Dict = {}
        for slot, item in self.slots.items():
            if item and item.stats:
                for stat_name, stat_value in item.stats.items():
                    if stat_name in total_stats:
                        total_stats[stat_name] += stat_value
                    else:
                        total_stats[stat_name] = stat_value
        return total_stats


class Inventory:
    """Основной класс инвентаря."""
    
    def __init__(self, screen: pygame.Surface, player_stats: PlayerStats):
        self.screen = screen
        self.player_stats = player_stats
        self.equipment = Equipment()
        self.items: List[InventoryItem] = []
        self.max_items = 20
        
        # Настройки UI
        self.inventory_open = False
        self.inventory_x = 50
        self.inventory_y = 50
        self.inventory_width = 600
        self.inventory_height = 400
        
        # Цвета
        self.background_color = (0, 0, 0, 200)
        self.border_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.slot_color = (50, 50, 50)
        self.slot_hover_color = (80, 80, 80)
        
        # Шрифты
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 28)
        
        # Размеры слотов
        self.slot_size = 50
        self.slot_padding = 5
        
        # Создаем тестовые предметы
        self._create_test_items()
    
    def _create_test_items(self):
        """Создает тестовые предметы для демонстрации."""
        test_items = [
            InventoryItem("Железный меч", "weapon", stats={"attack": 15, "strength": 5}),
            InventoryItem("Кожаная броня", "armor", stats={"defense": 10, "health": 20}),
            InventoryItem("Зелье здоровья", "consumable", stats={"heal": 50}),
            InventoryItem("Магическое кольцо", "accessory", stats={"magic": 10, "mana": 30})
        ]
        
        for item in test_items:
            self.add_item(item)
    
    def add_item(self, item: InventoryItem) -> bool:
        """Добавляет предмет в инвентарь."""
        if len(self.items) < self.max_items:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self, item: InventoryItem) -> bool:
        """Удаляет предмет из инвентаря."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def toggle_inventory(self):
        """Переключает состояние инвентаря (открыт/закрыт)."""
        self.inventory_open = not self.inventory_open
    
    def handle_click(self, mouse_pos: Tuple[int, int]):
        """Обрабатывает клик мыши в инвентаре."""
        if not self.inventory_open:
            return
        
        x, y = mouse_pos
        if not self._is_in_inventory_bounds(x, y):
            return
        
        # Проверяем клик по слотам экипировки
        equipment_click = self._handle_equipment_click(x, y)
        if equipment_click:
            return
        
        # Проверяем клик по предметам
        self._handle_item_click(x, y)
    
    def _is_in_inventory_bounds(self, x: int, y: int) -> bool:
        """Проверяет, находится ли точка в пределах инвентаря."""
        return (self.inventory_x <= x <= self.inventory_x + self.inventory_width and
                self.inventory_y <= y <= self.inventory_y + self.inventory_height)
    
    def _handle_equipment_click(self, x: int, y: int) -> bool:
        """Обрабатывает клик по слотам экипировки."""
        equipment_start_x = self.inventory_x + 20
        equipment_start_y = self.inventory_y + 60
        
        for i, (slot_name, item) in enumerate(self.equipment.slots.items()):
            slot_x = equipment_start_x + (i % 3) * (self.slot_size + self.slot_padding)
            slot_y = equipment_start_y + (i // 3) * (self.slot_size + self.slot_padding)
            
            if (slot_x <= x <= slot_x + self.slot_size and
                slot_y <= y <= slot_y + self.slot_size):
                print(f"[INVENTORY DEBUG] Клик по слоту экипировки: {slot_name}")
                return True
        
        return False
    
    def _handle_item_click(self, x: int, y: int):
        """Обрабатывает клик по предметам."""
        items_start_x = self.inventory_x + 200
        items_start_y = self.inventory_y + 60
        items_per_row = 8
        
        for i, item in enumerate(self.items):
            item_x = items_start_x + (i % items_per_row) * (self.slot_size + self.slot_padding)
            item_y = items_start_y + (i // items_per_row) * (self.slot_size + self.slot_padding)
            
            if (item_x <= x <= item_x + self.slot_size and
                item_y <= y <= item_y + self.slot_size):
                print(f"[INVENTORY DEBUG] Клик по предмету: {item.name}")
                break
    
    def draw(self):
        """Отрисовывает инвентарь."""
        if not self.inventory_open:
            return
        
        # Фон инвентаря
        self._draw_background()
        
        # Заголовок
        self._draw_title()
        
        # Экипировка
        self._draw_equipment()
        
        # Предметы
        self._draw_items()
        
        # Характеристики
        self._draw_stats()
    
    def _draw_background(self):
        """Отрисовывает фон инвентаря."""
        # Создаем полупрозрачную поверхность
        surface = pygame.Surface((self.inventory_width, self.inventory_height))
        surface.set_alpha(200)
        surface.fill(self.background_color)
        self.screen.blit(surface, (self.inventory_x, self.inventory_y))
        
        # Граница
        pygame.draw.rect(self.screen, self.border_color, 
                        (self.inventory_x, self.inventory_y, self.inventory_width, self.inventory_height), 2)
    
    def _draw_title(self):
        """Отрисовывает заголовок инвентаря."""
        title = "ИНВЕНТАРЬ"
        title_surface = self.font_large.render(title, True, self.text_color)
        title_x = self.inventory_x + (self.inventory_width - title_surface.get_width()) // 2
        title_y = self.inventory_y + 10
        self.screen.blit(title_surface, (title_x, title_y))
    
    def _draw_equipment(self):
        """Отрисовывает слоты экипировки."""
        equipment_start_x = self.inventory_x + 20
        equipment_start_y = self.inventory_y + 60
        
        # Заголовок экипировки
        equipment_title = "ЭКИПИРОВКА"
        title_surface = self.font_medium.render(equipment_title, True, self.text_color)
        self.screen.blit(title_surface, (equipment_start_x, equipment_start_y - 25))
        
        # Только первые 3 слота (Оружие, Броня, Шлем)
        slot_names = ["Оружие", "Броня", "Шлем"]
        
        for i, (slot_name, item) in enumerate(self.equipment.slots.items()):
            # Пропускаем слоты после первых 3
            if i >= 3:
                break
                
            slot_x = equipment_start_x + (i % 3) * (self.slot_size + self.slot_padding)
            slot_y = equipment_start_y + (i // 3) * (self.slot_size + self.slot_padding)
            
            # Слот
            pygame.draw.rect(self.screen, self.slot_color, 
                           (slot_x, slot_y, self.slot_size, self.slot_size))
            pygame.draw.rect(self.screen, self.border_color, 
                           (slot_x, slot_y, self.slot_size, self.slot_size), 1)
            
            # Название слота (только для первых 3)
            slot_text = slot_names[i]
            text_surface = self.font_small.render(slot_text, True, self.text_color)
            text_x = slot_x + (self.slot_size - text_surface.get_width()) // 2
            text_y = slot_y + self.slot_size + 2
            self.screen.blit(text_surface, (text_x, text_y))
            
            # Предмет в слоте (убираем желтую надпись)
            if item:
                # Можно добавить иконку или символ вместо текста
                # Например, точку или символ
                pygame.draw.circle(self.screen, (255, 255, 0), 
                                 (slot_x + self.slot_size // 2, slot_y + self.slot_size // 2), 3)
    
    def _draw_items(self):
        """Отрисовывает предметы инвентаря."""
        items_start_x = self.inventory_x + 200
        items_start_y = self.inventory_y + 60
        items_per_row = 8
        
        for i, item in enumerate(self.items):
            item_x = items_start_x + (i % items_per_row) * (self.slot_size + self.slot_padding)
            item_y = items_start_y + (i // items_per_row) * (self.slot_size + self.slot_padding)
            
            # Слот предмета
            pygame.draw.rect(self.screen, self.slot_color, 
                           (item_x, item_y, self.slot_size, self.slot_size))
            pygame.draw.rect(self.screen, self.border_color, 
                           (item_x, item_y, self.slot_size, self.slot_size), 1)
            
            # Предмет (заменяем текст на точку)
            pygame.draw.circle(self.screen, (255, 255, 0), 
                             (item_x + self.slot_size // 2, item_y + self.slot_size // 2), 3)
    
    def _draw_stats(self):
        """Отрисовывает характеристики персонажа."""
        stats_start_x = self.inventory_x + 20
        stats_start_y = self.inventory_y + 250
        
        # Заголовок характеристик
        stats_title = "ХАРАКТЕРИСТИКИ"
        title_surface = self.font_medium.render(stats_title, True, self.text_color)
        self.screen.blit(title_surface, (stats_start_x, stats_start_y - 25))
        
        # Базовые характеристики
        stats = [
            f"HP: {self.player_stats.health.current_value:.0f}/{self.player_stats.health.max_value:.0f}",
            f"SP: {self.player_stats.stamina.current_value:.0f}/{self.player_stats.stamina.max_value:.0f}",
            f"XP: {self.player_stats.experience.current_value:.0f}/{self.player_stats.experience.experience_to_next:.0f}",
            f"Уровень: {self.player_stats.experience.level}"
        ]
        
        # Характеристики экипировки
        equipped_stats = self.equipment.get_equipped_stats()
        if equipped_stats:
            stats.append("--- Экипировка ---")
            for stat_name, stat_value in equipped_stats.items():
                stats.append(f"{stat_name}: +{stat_value}")
        
        for i, stat_text in enumerate(stats):
            stat_surface = self.font_small.render(stat_text, True, self.text_color)
            stat_x = stats_start_x + (i % 2) * 150
            stat_y = stats_start_y + (i // 2) * 20
            self.screen.blit(stat_surface, (stat_x, stat_y)) 