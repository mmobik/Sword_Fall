import pygame
import math
from level.collisions import CollisionHandler
from core.config import config


class PlayerMovementHandler:
    def __init__(self, player):
        self.player = player
        self.collision_handler = CollisionHandler()
        self.collision_buffer = 2
        self.last_state = "idle_front"  # Запоминаем последнее состояние
        self.state_change_time = 0  # Время последнего изменения состояния

    def handle_movement(self, dt, level_width, level_height, collision_objects):
        pygame.event.pump()  # Обновляем состояние клавиш
        keys = pygame.key.get_pressed()
        move_x = keys[pygame.K_d] - keys[pygame.K_a]
        move_y = keys[pygame.K_s] - keys[pygame.K_w]
        # print("move_x:", move_x, "move_y:", move_y)  # Отладка

        # Нормализация вектора только при диагональном движении
        is_diagonal = move_x != 0 and move_y != 0
        if is_diagonal:
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x /= length
            move_y /= length

        # Движение игрока без скольжения и снижения скорости
        original_x = self.player.hitbox.x
        original_y = self.player.hitbox.y
        
        # Сначала пробуем двигаться по обеим осям
        new_x, new_y = self.collision_handler.handle_movement_collisions(
            self.player, original_x + move_x * self.player.speed * dt,
            original_y + move_y * self.player.speed * dt,
            collision_objects
        )
        
        # Если движение по обеим осям заблокировано, пробуем по одной оси
        if abs(new_x - original_x) < 0.1 and abs(new_y - original_y) < 0.1 and move_x != 0 and move_y != 0:
            # Пробуем только по X
            temp_x, _ = self.collision_handler.handle_movement_collisions(
                self.player, original_x + move_x * self.player.speed * dt,
                original_y,
                collision_objects
            )
            # Пробуем только по Y
            _, temp_y = self.collision_handler.handle_movement_collisions(
                self.player, original_x,
                original_y + move_y * self.player.speed * dt,
                collision_objects
            )
            # Выбираем то, что не заблокировано
            if abs(temp_x - original_x) >= 0.1:
                new_x = temp_x
                new_y = original_y
            elif abs(temp_y - original_y) >= 0.1:
                new_x = original_x
                new_y = temp_y
        
        # Ограничение по границам уровня
        new_x = max(0, min(new_x, level_width - self.player.hitbox.width))
        new_y = max(0, min(new_y, level_height - self.player.hitbox.height))
        
        self.player.hitbox.x = new_x
        self.player.hitbox.y = new_y
        self.player.rect.topleft = (self.player.hitbox.x, self.player.hitbox.y)

        # Анимация с улучшенной логикой
        self._update_animation_state(move_x, move_y, dt)

    def _update_animation_state(self, move_x, move_y, dt):
        self.state_change_time += dt
        
        # Определяем новое состояние только если есть движение
        new_state = None
        
        # Приоритет движения: вверх > вниз > влево > вправо
        if move_y < 0:  # Движение вверх
            new_state = "run_up"
        elif move_y > 0:  # Движение вниз
            new_state = "run_down"
        elif move_x < 0:  # Движение влево
            new_state = "run_left"
        elif move_x > 0:  # Движение вправо
            new_state = "run_right"
        else:
            # Если нет движения, определяем idle состояние на основе последнего движения
            if self.last_state.startswith("run_right"):
                new_state = "idle_right"
            elif self.last_state.startswith("run_left"):
                new_state = "idle_left"
            elif self.last_state.startswith("run_up"):
                new_state = "idle_back"
            elif self.last_state.startswith("run_down"):
                new_state = "idle_front"
            else:
                # Если не было движения, оставляем текущее состояние
                new_state = self.player.state_name

        # Переключаем состояние только если оно изменилось и прошло достаточно времени
        if new_state and new_state != self.player.state_name and self.state_change_time > 0.1:
            if config.DEBUG_MODE:
                print(f"Переключение состояния с {self.player.state_name} на {new_state}")
            self.player.set_state(new_state)
            self.last_state = new_state
            self.state_change_time = 0
        elif new_state and new_state != self.last_state:
            # Обновляем last_state даже если не переключаем состояние
            self.last_state = new_state
