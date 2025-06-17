import pygame
from level.spritesheet import SpriteSheet
from level.player_movement import PlayerMovementHandler
from core.config import config


class Player(pygame.sprite.Sprite):
    """
    Класс, представляющий игрока.
    """

    def __init__(self, x: int, y: int, *groups) -> None:
        super().__init__(*groups)
        self.state_name = "idle_front"
        self.state = config.PLAYER_STATES[self.state_name]
        self.sprite_sheet = SpriteSheet(self.state["sprite_sheet"], *config.FRAME_SIZE)
        self.frames = self.state["frames"]
        self.animation_speed = self.state["animation_speed"]
        self.animation_time = 0
        self.current_frame = 0
        self.image = self._get_frame()
        
        # Создаем rect на основе изображения
        self.rect = self.image.get_rect()
        
        # Создаем хитбокс с фиксированными размерами из конфига
        hitbox_width = config.PLAYER_HITBOX["WIDTH"]
        hitbox_height = config.PLAYER_HITBOX["HEIGHT"]
        hitbox_x = x + config.PLAYER_HITBOX["X_OFFSET"] - hitbox_width // 2
        hitbox_y = y + config.PLAYER_HITBOX["Y_OFFSET"] - hitbox_height // 2
        
        self.hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
        
        # Устанавливаем позицию rect относительно hitbox
        self.rect.center = self.hitbox.center
        
        self.speed = config.PLAYER_SPEED
        self.movement_handler = PlayerMovementHandler(self)
        print(f"Игрок создан: rect={self.rect}, hitbox={self.hitbox}")

    def _get_frame(self):
        if not hasattr(self, 'sprite_sheet') or not self.sprite_sheet:
            print(f"Ошибка: спрайт-лист не загружен для состояния {self.state_name}")
            return pygame.Surface(config.FRAME_SIZE, pygame.SRCALPHA)

        x, y = self.frames[self.current_frame]
        frame = self.sprite_sheet.get_image(x, y, *config.FRAME_SIZE)
        if not frame:
            frame = pygame.Surface((64, 64), pygame.SRCALPHA)
            frame.fill((255, 0, 0))  # Красный квадрат\

        if frame:
            return pygame.transform.flip(frame, self.state.get("flip", False), False)
        return pygame.Surface(config.FRAME_SIZE, pygame.SRCALPHA)

    def set_state(self, state_name):
        if state_name == self.state_name:
            return
        if state_name in config.PLAYER_STATES:
            print(f"Установка состояния: {state_name}")
            self.state_name = state_name
            self.state = config.PLAYER_STATES[self.state_name]
            self.sprite_sheet = SpriteSheet(self.state["sprite_sheet"], *config.FRAME_SIZE)
            self.frames = self.state["frames"]
            self.animation_speed = self.state["animation_speed"]
            self.animation_time = 0
            self.current_frame = 0
            self.image = self._get_frame()
            print(f"Новое состояние установлено: {state_name}, кадров: {len(self.frames)}")
        else:
            print(f"Ошибка: состояние {state_name} не найдено в конфигурации")

    def update(self, dt, level_width, level_height, collision_objects):
        self.movement_handler.handle_movement(dt, level_width, level_height, collision_objects)
        self._animate(dt)
        # Обновляем позицию rect в соответствии с hitbox
        self.rect.center = self.hitbox.center

    def _animate(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self._get_frame()
