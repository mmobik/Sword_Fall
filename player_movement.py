"""
Модуль обработки движения игрока.

Содержит класс для управления перемещением игрока по уровню,
обработки ввода с клавиатуры и ограничения движения в пределах уровня.
"""

import pygame
import math


class PlayerMovementHandler:
    """Обрабатывает перемещение игрока на основе пользовательского ввода."""

    def __init__(self, player):
        """Инициализирует обработчик движения для конкретного игрока.

        Args:
            player (Player): Экземпляр игрока, для которого обрабатывается движение
        """
        self.player = player

    def handle_movement(self, dt, level_width, level_height):
        """Обрабатывает ввод с клавиатуры и перемещает игрока.

        Вычисляет направление движения, нормализует вектор движения,
        обновляет позицию игрока и проверяет границы уровня.

        Args:
            dt (float): Время, прошедшее с последнего кадра (delta time)
            level_width (int): Ширина игрового уровня в пикселях
            level_height (int): Высота игрового уровня в пикселях
        """
        keys = pygame.key.get_pressed()

        # Получаем направление движения от пользовательского ввода
        move_x = keys[pygame.K_d] - keys[pygame.K_a]  # Горизонтальное движение (-1, 0, 1)
        move_y = keys[pygame.K_s] - keys[pygame.K_w]  # Вертикальное движение (-1, 0, 1)

        if move_x != 0 or move_y != 0:
            # Нормализуем вектор движения
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x /= length
            move_y /= length

            # Обновляем позицию игрока
            self.player.rect.x += move_x * self.player.speed * dt
            self.player.rect.y += move_y * self.player.speed * dt

            # Обновляем направление взгляда игрока
            if move_x != 0:
                self.player.direction = 1 if move_x > 0 else -1

            # Проверяем, чтобы игрок не вышел за границы уровня
            self.player.rect.left = max(0, self.player.rect.left)
            self.player.rect.right = min(level_width, self.player.rect.right)
            self.player.rect.top = max(0, self.player.rect.top)
            self.player.rect.bottom = min(level_height, self.player.rect.bottom)

            self.player.state = "run"
        else:
            self.player.state = "idle"

        # Обновление кадров анимации
        self.player.frames = self.player.run_frames if self.player.state == "run" else self.player.idle_frames
