import pygame
import pytmx

from core import SoundManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from core import WIDTH, HEIGHT, TARGET_FPS, ASSETS, FPS
from core import GameStateManager
from level import Player
from level import Camera
from level import create_level
from core import GAME_NAME


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        icon = pygame.image.load(ASSETS["ICON"])
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)
        self.main_menu = MainMenu(self.sound_manager, lambda: self.toggle_settings(), self.change_game_state)
        self.settings_menu = SettingsMenu(self.sound_manager, lambda: self.toggle_settings())
        pygame.mixer.music.load("assets/Sounds/Soundtracks/Dark_fantasm.mp3")
        pygame.mixer.music.play(-1)

    def toggle_settings(self):
        if self.game_state_manager.get_state() == "main_menu":
            self.game_state_manager.change_state("settings_menu", self.settings_menu)
        else:
            self.game_state_manager.change_state("main_menu", self.main_menu)

    def change_game_state(self, new_state, menu=None):
        self.game_state_manager.change_state(new_state, menu)
        if new_state == "new_game":
            self.sound_manager.play_music("Soundtracks/House.mp3")
        elif new_state == "main_menu":
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("Sounds/Soundracks/Dark_fantasm.mp3")
                pygame.mixer.music.play(-1)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        level_width, level_height, background = create_level()
        camera = Camera(level_width, level_height)
        player = Player(level_width // 2, level_height // 2)
        all_sprites = pygame.sprite.Group(player)

        while running:
            dt = clock.tick(FPS) / 1000
            mouse_pos = pygame.mouse.get_pos()

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                current_state = self.game_state_manager.get_state()

                if current_state == "settings_menu":
                    self.settings_menu.handle_event(event, mouse_pos, self.sound_manager)
                elif current_state == "main_menu":
                    self.main_menu.handle_event(event, mouse_pos, self.sound_manager)

            # Обновление  постоянное (плохо)
            all_sprites.update(dt, level_width, level_height)
            camera.update(player)

            # Отрисовка
            if self.game_state_manager.get_state() == "new_game":
                self.screen.blit(background, (0, 0), (camera.offset.x, camera.offset.y, WIDTH, HEIGHT))
                for sprite in all_sprites:
                    self.screen.blit(sprite.image, camera.apply(sprite.rect))
            else:
                # Отрисовка меню и настроек
                mouse_pos = pygame.mouse.get_pos()  # Получаем позицию мыши
                if self.game_state_manager.get_state() == "settings_menu":
                    self.settings_menu.draw(self.screen, mouse_pos)
                elif self.game_state_manager.get_state() == "main_menu":
                    self.main_menu.draw(self.screen, mouse_pos)

            pygame.display.flip()
            self.clock.tick(TARGET_FPS)
        self.sound_manager.stop_music()


if __name__ == "__main__":
    game = Game()
    game.run()
