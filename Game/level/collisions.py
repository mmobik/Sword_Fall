import pygame
from core.config import config


class CollisionHandler:
    def __init__(self):
        self.collision_buffer = 0  # Буфер для предотвращения "залипания"

    @staticmethod
    def load_collision_objects(tmx_map):
        collision_objects = []
        collision_layer = tmx_map.get_layer_by_name(config.COLLISION_SETTINGS["COLLISION_LAYER_NAME"])

        if collision_layer:
            for obj in collision_layer:
                if obj.properties.get("collision", config.COLLISION_SETTINGS["DEFAULT_COLLISION"]):
                    collision_rect = pygame.Rect(
                        int(obj.x),
                        int(obj.y),
                        int(obj.width),
                        int(obj.height))
                    properties = {
                        'rect': collision_rect,
                        'type': obj.properties.get("type", "solid"),
                        'properties': dict(obj.properties)
                    }
                    collision_objects.append(properties)

        return collision_objects

    def check_collision(self, rect, collision_objects):
        buffered_rect = rect.inflate(-self.collision_buffer, -self.collision_buffer)
        for obj in collision_objects:
            if buffered_rect.colliderect(obj['rect']):
                return obj
        return None

    def handle_movement_collisions(self, player, new_x, new_y, collision_objects):
        # Создаем временный rect для проверки коллизий
        temp_rect = pygame.Rect(new_x, new_y, player.hitbox.width, player.hitbox.height)
        original_x = player.hitbox.x
        original_y = player.hitbox.y

        # Движение по X
        collision_x = self.check_collision(temp_rect, collision_objects)
        if collision_x:
            if new_x > original_x:
                new_x = collision_x['rect'].left - temp_rect.width
            else:
                new_x = collision_x['rect'].right

        # Движение по Y
        temp_rect.x = new_x
        collision_y = self.check_collision(temp_rect, collision_objects)
        if collision_y:
            if new_y > original_y:
                new_y = collision_y['rect'].top - temp_rect.height
            else:
                new_y = collision_y['rect'].bottom

        return new_x, new_y
