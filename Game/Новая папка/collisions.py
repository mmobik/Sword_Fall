import pygame
from Game.core.config import config


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
        rect = player.hitbox
        original_x = rect.x
        original_y = rect.y

        # Движение по X
        rect.x = new_x
        collision_x = self.check_collision(rect, collision_objects)
        if collision_x:
            if new_x > original_x:
                rect.right = collision_x['rect'].left
            else:
                rect.left = collision_x['rect'].right
            new_x = rect.x

        # Движение по Y
        rect.y = new_y
        collision_y = self.check_collision(rect, collision_objects)
        if collision_y:
            if new_y > original_y:
                rect.bottom = collision_y['rect'].top
            else:
                rect.top = collision_y['rect'].bottom
            new_y = rect.y

        return new_x, new_y
