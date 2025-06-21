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
        # Проверяем, жив ли игрок - если нет, блокируем движение
        if not self.player.is_alive():
            # Устанавливаем состояние idle и останавливаем движение
            if self.player.state_name.startswith("run"):
                if self.player.state_name.startswith("run_right"):
                    self.player.set_state("idle_right")
                elif self.player.state_name.startswith("run_left"):
                    self.player.set_state("idle_left")
                elif self.player.state_name.startswith("run_up"):
                    self.player.set_state("idle_back")
                elif self.player.state_name.startswith("run_down"):
                    self.player.set_state("idle_front")
            
            # Останавливаем звук шагов
            if hasattr(self.player, '_was_walking') and self.player._was_walking:
                self.player._was_walking = False
                if hasattr(self.player, '_steps_channel') and self.player._steps_channel:
                    self.player._steps_channel.stop()
                    self.player._steps_channel = None
            
            # Устанавливаем флаг движения в False
            self.player.is_walking = False
            return
        
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

        # --- Логика звука шагов и выносливости ---
        is_moving = (abs(move_x) > 0 or abs(move_y) > 0)
        
        # Обновляем флаг движения для системы выносливости
        self.player.is_walking = is_moving
        
        if hasattr(self.player, 'sound_manager') and self.player.sound_manager:
            steps_channel = getattr(self.player, '_steps_channel', None)
            if is_moving:
                if not hasattr(self.player, '_was_walking') or not self.player._was_walking:
                    # Начать проигрывать звук шагов
                    self.player._was_walking = True
                    sound = self.player.sound_manager.sounds.get('steps')
                    if sound:
                        # Устанавливаем громкость перед воспроизведением
                        sound.set_volume(self.player.sound_manager.music_volume)
                        self.player._steps_channel = sound.play(loops=-1)
                else:
                    # Обновляем громкость уже играющего звука
                    if steps_channel:
                        sound = self.player.sound_manager.sounds.get('steps')
                        if sound:
                            old_volume = sound.get_volume()
                            sound.set_volume(self.player.sound_manager.music_volume)
                            if config.DEBUG_MODE and abs(old_volume - self.player.sound_manager.music_volume) > 0.01:
                                print(f"[MOVEMENT DEBUG] Громкость шагов изменена: {old_volume:.2f} -> {self.player.sound_manager.music_volume:.2f}")
            else:
                if hasattr(self.player, '_was_walking') and self.player._was_walking:
                    # Остановить звук шагов
                    self.player._was_walking = False
                    if steps_channel:
                        steps_channel.stop()
                        self.player._steps_channel = None

    def _update_animation_state(self, move_x, move_y, dt):
        self.state_change_time += dt

        # Новая логика:
        if move_y < 0:
            if move_x > 0:
                new_state = "run_right"  # вверх-вправо
            elif move_x < 0:
                new_state = "run_left"   # вверх-влево
            else:
                new_state = "run_up"     # строго вверх
        elif move_y > 0:
            if move_x > 0:
                new_state = "run_right"  # вниз-вправо
            elif move_x < 0:
                new_state = "run_left"   # вниз-влево
            else:
                new_state = "run_down"   # строго вниз
        elif move_x < 0:
            new_state = "run_left"
        elif move_x > 0:
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
                new_state = self.player.state_name

        if new_state and new_state != self.player.state_name and self.state_change_time > 0.1:
            if config.DEBUG_MODE:
                print(f"Переключение состояния с {self.player.state_name} на {new_state}")
            self.player.set_state(new_state)
            self.last_state = new_state
            self.state_change_time = 0
        elif new_state and new_state != self.last_state:
            self.last_state = new_state
