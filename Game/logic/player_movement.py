import pygame
import math
from collisions import CollisionHandler


class PlayerMovementHandler:
    """
    Класс для обработки перемещения игрока.
    """

    def __init__(self, player):
        """
        Инициализация обработчика перемещения.

        Args:
            player (Player): Объект игрока.
        """
        self.player = player
        self.collision_handler = CollisionHandler()
        self.collision_buffer = 2

    def handle_movement(self, dt, level_width, level_height, collision_objects):
        """
        Обрабатывает перемещение игрока.

        Args:
            dt (float): Время, прошедшее с предыдущего кадра.
            level_width (int): Ширина уровня.
            level_height (int): Высота уровня.
            collision_objects (list): Список объектов коллизий.
        """
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
        if move_x > 0:
            self.player.set_state("run_right")
        elif move_x < 0:
            self.player.set_state("run_left")
        elif move_y < 0:
            self.player.set_state("run_up")
        elif move_y > 0:
            self.player.set_state("run_down")
        else:
            current_state = self.player.state_name
            if current_state.startswith("run_right"):
                self.player.set_state("idle_right")
            elif current_state.startswith("run_left"):
                self.player.set_state("idle_left")
            elif current_state.startswith("run_up"):
                self.player.set_state("idle_back")
            elif current_state.startswith("run_down"):
                self.player.set_state("idle_front")
