import sys
import time

import pygame
from .config import WIDTH, HEIGHT, FADE_DURATION, TARGET_FPS


class GameStateManager:
    def __init__(self, sound_manager):
        self.game_state = "main_menu"
        self.sound_manager = sound_manager
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.new_game_background = None  # Инициализируем фон как None

    def change_state(self, new_state, menu=None):
        if new_state == "new_game":
            self.animate_transition(new_state, menu)
            self.game_state = new_state
        elif new_state == "settings_menu" or new_state == "main_menu":
            self.game_state = new_state
        else:
            self.game_state = new_state

    def get_state(self):
        return self.game_state

    def animate_transition(self, new_state_or_image, menu, duration=FADE_DURATION):
        alpha = 0
        start_time = time.time()

        while alpha < 255:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            time_elapsed = time.time() - start_time
            alpha = min(255, int(255 * time_elapsed / duration))
            self.fade_surface.fill((0, 0, 0, alpha))
            # Рисуем текущее меню
            if menu:
                menu.draw(pygame.display.get_surface(), pygame.mouse.get_pos())

            pygame.display.get_surface().blit(self.fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.Clock().tick(TARGET_FPS)

        pygame.display.flip()

        alpha = 255
        start_time = time.time()

        while alpha > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            time_elapsed = time.time() - start_time
            alpha = max(0, 255 - int(255 * time_elapsed / duration))

            self.fade_surface.fill((0, 0, 0, alpha))

            pygame.display.get_surface().blit(self.fade_surface, (0, 0))

            pygame.display.flip()
            pygame.time.Clock().tick(TARGET_FPS)
