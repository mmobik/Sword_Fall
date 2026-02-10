import pygame
import os
from typing import Optional, Dict, Any, Tuple

class InventoryItem:
    """Класс для представления предмета в инвентаре."""
    
    # Размер слота по умолчанию
    SLOT_SIZE = 50
    
    def __init__(self, item_id: str, name: str, description: str = "", 
                 item_type: str = "consumable", image_path: Optional[str] = None,
                 stats: Optional[Dict[str, Any]] = None, max_stack: int = 99,
                 rarity: str = "common"):  # Добавим редкость: common, uncommon, rare, epic, legendary
        self.id = item_id
        self.name = name
        self.description = description
        self.type = item_type
        self.max_stack = max_stack
        self.count = 1
        self.stats = stats or {}
        self.rarity = rarity
        self.equipped = False  # Надет ли предмет
        
        # Цвета для редкости
        self.rarity_colors = {
            "common": (200, 200, 200),
            "uncommon": (30, 255, 0),
            "rare": (0, 100, 255),
            "epic": (163, 53, 238),
            "legendary": (255, 215, 0)
        }
        
        # Загружаем изображение
        self.image = None
        if image_path:
            self.load_image(image_path)
    
    def load_image(self, image_path: str):
        """Загружает и масштабирует изображение."""
        try:
            if os.path.exists(image_path):
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, 
                                                   (self.SLOT_SIZE, self.SLOT_SIZE))
            else:
                print(f"[ITEM WARNING] Файл не найден: {image_path}")
                # Создаем placeholder изображение
                self.image = pygame.Surface((self.SLOT_SIZE, self.SLOT_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (100, 100, 100, 200), 
                               (0, 0, self.SLOT_SIZE, self.SLOT_SIZE))
                font = pygame.font.Font(None, 24)
                text = font.render("?", True, (255, 255, 255))
                self.image.blit(text, (self.SLOT_SIZE//2-5, self.SLOT_SIZE//2-10))
        except Exception as e:
            print(f"[ITEM ERROR] Ошибка загрузки {image_path}: {e}")
            self.image = None
    
    def can_stack_with(self, other_item: 'InventoryItem') -> bool:
        """Можно ли сложить с другим предметом."""
        return (self.id == other_item.id and 
                self.count + other_item.count <= self.max_stack)
    
    def split(self, amount: int) -> Optional['InventoryItem']:
        """Разделить стак на два."""
        if amount >= self.count:
            return None
        
        # Создаем копию с тем же изображением
        new_item = InventoryItem(
            item_id=self.id,
            name=self.name,
            description=self.description,
            item_type=self.type,
            stats=self.stats.copy(),
            max_stack=self.max_stack,
            rarity=self.rarity
        )
        new_item.image = self.image  # Используем то же изображение
        
        self.count -= amount
        new_item.count = amount
        
        return new_item
    
    def merge(self, other_item: 'InventoryItem') -> bool:
        """Объединить с другим предметом (если возможно)."""
        if not self.can_stack_with(other_item):
            return False
        
        total = self.count + other_item.count
        if total <= self.max_stack:
            self.count = total
            return True
        else:
            self.count = self.max_stack
            other_item.count = total - self.max_stack
            return True
    
    def get_display_name(self) -> str:
        """Имя с количеством (если больше 1)."""
        if self.count > 1:
            return f"{self.name} x{self.count}"
        return self.name
    
    def get_rarity_color(self) -> Tuple[int, int, int]:
        """Возвращает цвет редкости."""
        return self.rarity_colors.get(self.rarity, (200, 200, 200))
    
    def draw(self, surface: pygame.Surface, x: int, y: int, 
             show_count: bool = True, selected: bool = False):
        """Отрисовка предмета в слоте."""
        # Рамка слота
        slot_rect = pygame.Rect(x, y, self.SLOT_SIZE, self.SLOT_SIZE)
        
        # Цвет рамки в зависимости от редкости
        rarity_color = self.get_rarity_color()
        pygame.draw.rect(surface, rarity_color, slot_rect, 2)
        
        # Заливка слота
        if selected:
            pygame.draw.rect(surface, (50, 50, 50, 180), slot_rect)
        else:
            pygame.draw.rect(surface, (40, 40, 40, 180), slot_rect)
        
        # Изображение предмета
        if self.image:
            img_x = x + (self.SLOT_SIZE - self.image.get_width()) // 2
            img_y = y + (self.SLOT_SIZE - self.image.get_height()) // 2
            surface.blit(self.image, (img_x, img_y))
            
            # Количество (если больше 1)
            if show_count and self.count > 1:
                self._draw_count(surface, x, y)
    
    def _draw_count(self, surface: pygame.Surface, x: int, y: int):
        """Отрисовка количества предметов."""
        font = pygame.font.Font(None, 20)
        count_text = font.render(str(self.count), True, (255, 255, 255))
        text_x = x + self.SLOT_SIZE - 15
        text_y = y + self.SLOT_SIZE - 20
        
        # Фон для текста
        text_bg = pygame.Surface((20, 20), pygame.SRCALPHA)
        text_bg.fill((0, 0, 0, 150))
        surface.blit(text_bg, (text_x - 5, text_y - 5))
        
        surface.blit(count_text, (text_x, text_y))
