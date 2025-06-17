import pygame
from level.spritesheet import SpriteSheet
from level.player_movement import PlayerMovementHandler
from core.config import config


class Player(pygame.sprite.Sprite):
    """
    Класс, представляющий игрока.
    """

    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        self.state_name = "idle_front"
        self.state = config.PLAYER_STATES[self.state_name]
        self.sprite_sheet = SpriteSheet(self.state["sprite_sheet"], *config.FRAME_SIZE)
        self.frames = self.state["frames"]
        self.animation_speed = self.state["animation_speed"]
        self.animation_time = 0
        self.current_frame = 0

        self.image = self._get_frame()
        self.rect = self.image.get_rect(center=(x, y))

        # Создаем хитбокс с учетом смещений из конфига
        self.hitbox = self.rect.inflate(
            config.PLAYER_HITBOX["WIDTH_OFFSET"],
            config.PLAYER_HITBOX["HEIGHT_OFFSET"]
        )
        # Применяем смещение центра
        self.hitbox.center = (
            x + config.PLAYER_HITBOX["X_OFFSET"],
            y + config.PLAYER_HITBOX["Y_OFFSET"]
        )

        self.speed = config.PLAYER_SPEED
        self.movement_handler = PlayerMovementHandler(self)

    def _get_frame(self):
        x, y = self.frames[self.current_frame]
        frame = self.sprite_sheet.get_image(x, y, *config.FRAME_SIZE)
        return pygame.transform.flip(frame, self.state.get("flip", False), False)

    def set_state(self, state_name):
        if state_name == self.state_name:
            return
        if state_name in config.PLAYER_STATES:
            self.state_name = state_name
            self.state = config.PLAYER_STATES[self.state_name]
            self.sprite_sheet = SpriteSheet(self.state["sprite_sheet"], *config.FRAME_SIZE)
            self.frames = self.state["frames"]
            self.animation_speed = self.state["animation_speed"]
            self.current_frame = 0
            self.image = self._get_frame()

    def update(self, dt, level_width, level_height, collision_objects):
        self.movement_handler.handle_movement(dt, level_width, level_height, collision_objects)
        self._animate(dt)
        # Обновляем позицию rect в соответствии с hitbox
        self.rect.center = (
            self.hitbox.centerx - config.PLAYER_HITBOX["X_OFFSET"],
            self.hitbox.centery - config.PLAYER_HITBOX["Y_OFFSET"]
        )

    def _animate(self, dt):
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self._get_frame()
