import pygame
from sound_manager import SoundManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from config import WIDTH, HEIGHT, TARGET_FPS
from game_state_manager import GameStateManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Main_menu")
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)
        self.main_menu = MainMenu(self.sound_manager, self.toggle_settings,
                                  self.change_game_state)
        self.settings_menu = SettingsMenu(self.sound_manager, self.toggle_settings)
        pygame.mixer.music.load("Sounds/Soundtracks/Dark_fantasm.mp3")
        pygame.mixer.music.play(-1)

    def toggle_settings(self):
        if self.game_state_manager.get_state() == "main_menu":
            self.game_state_manager.change_state("settings_menu")
        else:
            self.game_state_manager.change_state("main_menu")

    def change_game_state(self, new_state):
        self.game_state_manager.change_state(new_state)
        if new_state == "new_game":
            self.sound_manager.play_music("House.mp3")
        elif new_state == "main_menu":
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("Sounds/Soundracks/Dark_fantasm.mp3")
                pygame.mixer.music.play(-1)

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.game_state_manager.get_state() == "settings_menu":
                    self.settings_menu.handle_event(event, mouse_pos)
                elif self.game_state_manager.get_state() == "main_menu":
                    self.main_menu.handle_event(event, mouse_pos)

            if self.game_state_manager.get_state() == "settings_menu":
                self.settings_menu.draw(self.screen, mouse_pos)
            elif self.game_state_manager.get_state() == "main_menu":
                self.main_menu.draw(self.screen, mouse_pos)
            elif self.game_state_manager.get_state() == "new_game":
                self.screen.blit(self.game_state_manager.new_game_background, (0, 0))

            pygame.display.flip()
            self.clock.tick(TARGET_FPS)
        self.sound_manager.stop_music()
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
