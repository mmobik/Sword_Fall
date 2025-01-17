import pygame
import time
from utils import load_image
from config import WIDTH, HEIGHT, FADE_DURATION, TARGET_FPS


class GameStateManager:
    def __init__(self, sound_manager):
        self.game_state = "main_menu"
        self.sound_manager = sound_manager
        self.fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.new_game_background = None

    def change_state(self, new_state, new_image=None):
        if new_state == "new_game":
            if not self.new_game_background:
                self.new_game_background = load_image("Game/Bedroom.jpeg")
            self.animate_transition(self.new_game_background)
        self.game_state = new_state
        return

    def get_state(self):
        return self.game_state

    def animate_transition(self, new_image, duration=FADE_DURATION):
        alpha = 0
        start_time = time.time()

        while alpha < 255:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

            time_elapsed = time.time() - start_time
            alpha = min(255, int(255 * time_elapsed / duration))
            self.fade_surface.fill((0, 0, 0, alpha))
            # Рисуем текущее меню
            if self.game_state == "settings_menu":
                from UI.settings_menu import SettingsMenu
                settings_menu = SettingsMenu(self.sound_manager, lambda: None)
                settings_menu.draw(pygame.display.get_surface(), pygame.mouse.get_pos())
            elif self.game_state == "main_menu":
                from UI.main_menu import MainMenu
                main_menu = MainMenu(self.sound_manager, lambda: None, lambda x: None)
                main_menu.draw(pygame.display.get_surface(), pygame.mouse.get_pos())

            pygame.display.get_surface().blit(self.fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.Clock().tick(TARGET_FPS)

        pygame.display.get_surface().blit(new_image, (0, 0))
        pygame.display.flip()

        alpha = 255
        start_time = time.time()

        while alpha > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

            time_elapsed = time.time() - start_time
            alpha = max(0, 255 - int(255 * time_elapsed / duration))

            self.fade_surface.fill((0, 0, 0, alpha))
            pygame.display.get_surface().blit(new_image, (0, 0))
            pygame.display.get_surface().blit(self.fade_surface, (0, 0))

            pygame.display.flip()
            pygame.time.Clock().tick(TARGET_FPS)
