import pygame
import math
from level.collisions import CollisionHandler


class PlayerMovementHandler:
    def __init__(self, player):
        self.player = player
        self.collision_handler = CollisionHandler()
        self.collision_buffer = 2

    def handle_movement(self, dt, level_width, level_height, collision_objects):
        keys = pygame.key.get_pressed()
        move_x = keys[pygame.K_d] - keys[pygame.K_a]
        move_y = keys[pygame.K_s] - keys[pygame.K_w]

        # Нормализация вектора (если есть движение)
        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x /= length
            move_y /= length

        # Рассчитываем новую позицию
        new_x = self.player.hitbox.x + move_x * self.player.speed * dt
        new_y = self.player.hitbox.y + move_y * self.player.speed * dt

        # Ограничение границами уровня
        new_x = max(0, min(new_x, level_width - self.player.hitbox.width))
        new_y = max(0, min(new_y, level_height - self.player.hitbox.height))

        # Обработка коллизий
        new_x, new_y = self.collision_handler.handle_movement_collisions(
            self.player, new_x, new_y, collision_objects
        )

        # Обновляем позицию игрока
        self.player.hitbox.x = new_x
        self.player.hitbox.y = new_y
        self.player.rect.center = self.player.hitbox.center

        # Анимация
        new_state = None
        if move_x > 0:
            new_state = "run_right"
        elif move_x < 0:
            new_state = "run_left"
        elif move_y < 0:
            new_state = "run_up"
        elif move_y > 0:
            new_state = "run_down"
        else:
            if self.player.state_name.startswith("run_right"):
                new_state = "idle_right"
            elif self.player.state_name.startswith("run_left"):
                new_state = "idle_left"
            elif self.player.state_name.startswith("run_up"):
                new_state = "idle_back"
            elif self.player.state_name.startswith("run_down"):
                new_state = "idle_front"

        if new_state and new_state != self.player.state_name:
            self.player.set_state(new_state)
