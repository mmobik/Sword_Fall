import pygame
import sys
from core import SoundManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu
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

        # Создаем все меню
        self.main_menu = MainMenu(
            self.sound_manager,
            self.show_settings,
            self.start_game
        )

        self.settings_menu = SettingsMenu(
            self.sound_manager,
            self.show_main_menu,
            self.show_language
        )

        self.language_menu = LanguageMenu(
            self.sound_manager,
            self.show_settings,
            self.change_language
        )

        # Устанавливаем начальное меню
        self.show_main_menu()

        # Загрузка музыки
        pygame.mixer.music.load("assets/Sounds/Soundtracks/Dark_fantasm.mp3")
        pygame.mixer.music.play(-1)

    def show_main_menu(self):
        self.game_state_manager.change_state("main_menu", self.main_menu)

    def show_settings(self):
        self.game_state_manager.change_state("settings_menu", self.settings_menu)

    def show_language(self):
        self.game_state_manager.change_state("language_menu", self.language_menu)

    def change_language(self, lang):
        print(f"Язык изменен на: {lang}")
        self.show_settings()

    def start_game(self, state):
        if state == "new_game":
            self.game_state_manager.change_state(state, self.main_menu)  # Передаем текущее меню для анимации
            self.sound_manager.play_music("Soundtracks/House.mp3")
        else:
            self.game_state_manager.change_state(state)

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

                if self.game_state_manager.current_menu:
                    self.game_state_manager.current_menu.handle_event(event, mouse_pos, self.sound_manager)

            # Обновление игры
            if self.game_state_manager.game_state == "new_game":
                all_sprites.update(dt, level_width, level_height)
                camera.update(player)

            # Отрисовка
            self.screen.fill((0, 0, 0))

            if self.game_state_manager.game_state == "new_game":
                self.screen.blit(background, (0, 0), (camera.offset.x, camera.offset.y, WIDTH, HEIGHT))
                for sprite in all_sprites:
                    self.screen.blit(sprite.image, camera.apply(sprite.rect))
            elif self.game_state_manager.current_menu:
                self.game_state_manager.current_menu.draw(self.screen, mouse_pos)

            pygame.display.flip()
            self.clock.tick(TARGET_FPS)

        self.sound_manager.stop_music()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()