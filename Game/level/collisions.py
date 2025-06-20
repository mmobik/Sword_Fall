"""
Модуль обработки коллизий.

Содержит класс CollisionHandler для обработки столкновений между объектами
и игроком с поддержкой скольжения вдоль стен.
"""

import pygame
from core.config import config


class CollisionHandler:
    """
    Обработчик коллизий для игровых объектов.
    
    Обеспечивает загрузку объектов коллизий из карты и обработку
    столкновений с поддержкой скольжения вдоль стен.
    """

    def __init__(self):
        """Инициализация обработчика коллизий."""
        self.collision_buffer = 1  # Небольшой буфер для предотвращения "залипания"

    @staticmethod
    def load_collision_objects(tmx_map):
        """
        Загружает объекты коллизий из TMX карты.
        
        Args:
            tmx_map: Загруженная TMX карта.
            
        Returns:
            Список объектов коллизий с их свойствами.
        """
        collision_objects = []
        collision_layer = tmx_map.get_layer_by_name(
            config.COLLISION_SETTINGS["COLLISION_LAYER_NAME"]
        )

        if collision_layer:
            for obj in collision_layer:
                if obj.properties.get("collision",
                                      config.COLLISION_SETTINGS["DEFAULT_COLLISION"]):
                    collision_rect = pygame.Rect(
                        int(obj.x),
                        int(obj.y),
                        int(obj.width),
                        int(obj.height)
                    )
                    properties = {
                        'rect': collision_rect,
                        'type': obj.properties.get("type", "solid"),
                        'properties': dict(obj.properties)
                    }
                    collision_objects.append(properties)

        return collision_objects

    def check_collision(self, rect: pygame.Rect, collision_objects: list) -> dict | None:
        """
        Проверяет коллизию с объектами с учетом буфера.
        
        Args:
            rect: Прямоугольник для проверки коллизии.
            collision_objects: Список объектов коллизий.
            
        Returns:
            Объект коллизии или None, если коллизии нет.
        """
        buffered_rect = rect.inflate(-self.collision_buffer, -self.collision_buffer)
        for obj in collision_objects:
            if buffered_rect.colliderect(obj['rect']):
                return obj
        return None

    def handle_movement_collisions(self, player, new_x: float, new_y: float,
                                   collision_objects: list) -> tuple[float, float]:
        """
        Обрабатывает коллизии при движении игрока.
        
        Реализует алгоритм скольжения вдоль стен для плавного движения.
        
        Args:
            player: Объект игрока.
            new_x: Новая X координата.
            new_y: Новая Y координата.
            collision_objects: Список объектов коллизий.
            
        Returns:
            Кортеж (final_x, final_y) с финальными координатами.
        """
        original_x = player.hitbox.x
        original_y = player.hitbox.y

        # Алгоритм скольжения
        # 1. Пробуем двигаться по диагонали
        test_rect_diag = player.hitbox.copy()
        test_rect_diag.x = new_x
        test_rect_diag.y = new_y
        collision_diag = self.check_collision(test_rect_diag, collision_objects)

        if not collision_diag:
            final_x = new_x
            final_y = new_y
        else:
            # 2. Пробуем только по X
            test_rect_x = player.hitbox.copy()
            test_rect_x.x = new_x
            test_rect_x.y = original_y
            collision_x = self.check_collision(test_rect_x, collision_objects)

            if not collision_x:
                final_x = new_x
                final_y = original_y
            else:
                # 3. Пробуем только по Y
                test_rect_y = player.hitbox.copy()
                test_rect_y.x = original_x
                test_rect_y.y = new_y
                collision_y = self.check_collision(test_rect_y, collision_objects)

                if not collision_y:
                    final_x = original_x
                    final_y = new_y
                else:
                    # 4. Стоим на месте
                    final_x = original_x
                    final_y = original_y

        # Проверяем, не застрял ли игрок
        if abs(final_x - original_x) < 0.1 and abs(final_y - original_y) < 0.1:
            # Проверяем, действительно ли игрок пытается двигаться
            dx = new_x - original_x
            dy = new_y - original_y

            if abs(dx) > 0.1 or abs(dy) > 0.1:  # Игрок пытается двигаться
                if config.DEBUG_MODE:
                    print(f"Полная блокировка: позиция ({int(final_x)}, {int(final_y)})")

                # Пробуем оттолкнуть игрока в направлении движения
                if abs(dx) > abs(dy):
                    # Движение больше по X
                    test_rect = player.hitbox.copy()
                    test_rect.x = original_x + (1 if dx > 0 else -1)
                    if not self.check_collision(test_rect, collision_objects):
                        final_x = test_rect.x
                else:
                    # Движение больше по Y
                    test_rect = player.hitbox.copy()
                    test_rect.y = original_y + (1 if dy > 0 else -1)
                    if not self.check_collision(test_rect, collision_objects):
                        final_y = test_rect.y

        return final_x, final_y
