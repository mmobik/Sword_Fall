import pygame
from Game.level.spritesheet import SpriteSheet
from Game.level.player_movement import PlayerMovementHandler
from Game.core.config import config


class Player(pygame.sprite.Sprite):
    """
    Класс игрока.
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Инициализация игрока.

        Args:
            x (int): Начальная координата X.
            y (int): Начальная координата Y.
        """
        super().__init__()
        self.idle_sheet = SpriteSheet(config.ASSETS["IDLE_SHEET"], *config.FRAME_SIZE)
        self.run_sheet = SpriteSheet(config.ASSETS["RUN_SHEET"], *config.FRAME_SIZE)

        self.frame_size = config.FRAME_SIZE
        self.idle_frames = config.ANIMATION_FRAMES["IDLE"]
        self.run_frames = config.ANIMATION_FRAMES["RUN"]

        self.speed = config.PLAYER_SPEED
        self.direction = 1  # Направление
        self.current_frame = 0
        self.DEFAULT_ANIMATION_SPEED = config.DEFAULT_ANIMATION_SPEED
        self.NO_ANIMATION = config.NO_ANIMATION
        self.animation_speed = self.DEFAULT_ANIMATION_SPEED
        self.animation_time = 0
        self.movement_handler = PlayerMovementHandler(self)

        # Остановка анимации
        sheets = [self.idle_sheet, self.run_sheet]
        for sheet in sheets:
            if sheet.download == 0:
                self.animation_speed = self.NO_ANIMATION
                break

        # Начальное состояние
        self.state = "idle"  # Начальное состояние
        self.frames = self.idle_frames  # Кадры для текущего состояния
        self.image = self._get_frame()  # Текущий кадр
        self.rect = self.image.get_rect(center=(x, y))  # Прямоугольник для столкновений
        self.hitbox = self.rect.inflate(-30, -20)  # Прямоугольник для столкновений (меньше основного)

    def _get_frame(self):
        """
        Возвращает текущий кадр анимации с учетом направления.

        Returns:
            pygame.Surface: Текущий кадр.
        """
        x, y = self.frames[self.current_frame]
        sheet = self.idle_sheet if self.state == "idle" else self.run_sheet
        frame = sheet.get_image(x, y, *self.frame_size)
        return pygame.transform.flip(frame, self.direction == -1, False)

    def update(self, dt, level_width, level_height):
        """
        Обновляет состояние игрока.

        Args:
            dt (float): Время, прошедшее с предыдущего кадра (delta time).
            level_width (int): Ширина уровня.
            level_height (int): Высота уровня.
        """
        self.movement_handler.handle_movement(dt, level_width, level_height)
        self._animate(dt)
        self.hitbox.center = self.rect.center

    def _animate(self, dt):
        """
        Обновляет анимацию персонажа.

        Args:
            dt (float): Время, прошедшее с предыдущего кадра (delta time).
        """
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self._get_frame()
