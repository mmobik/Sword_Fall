import pygame
import math
from Game.core.config import config


class PlayerMovementHandler:
    def __init__(self, player):
        self.player = player

    def handle_movement(self, dt, level_width, level_height):
        keys = pygame.key.get_pressed()
        move_x = keys[pygame.K_d] - keys[pygame.K_a]
        move_y = keys[pygame.K_s] - keys[pygame.K_w]

        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            self.player.rect.x += (move_x / length) * self.player.speed * dt
            self.player.rect.y += (move_y / length) * self.player.speed * dt

            if move_x != 0:
                self.player.direction = 1 if move_x > 0 else -1

            self.player.rect.left = max(0, self.player.rect.left)
            self.player.rect.right = min(level_width, self.player.rect.right)
            self.player.rect.top = max(0, self.player.rect.top)
            self.player.rect.bottom = min(level_height, self.player.rect.bottom)

            self.player.state = "run"
        else:
            self.player.state = "idle"

        self.player.frames = self.player.run_frames if self.player.state == "run" else self.player.idle_frames
