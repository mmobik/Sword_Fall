from Game.core.config import config
from Game.core.sound_manager import SoundManager
from Game.core.game_state_manager import GameStateManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu
from level import Player, Camera, create_level
import pygame
import sys


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(config.SCREEN_SIZE)
        pygame.display.set_caption(config.GAME_NAME)
        icon = pygame.image.load(config.ASSETS["ICON"])
        pygame.display.set_icon(icon)

        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)

        self.fps_counter = 0
        self.last_fps_time = pygame.time.get_ticks()
        self.fps_history = []

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
        self.sound_manager.play_music("Dark_fantasm.mp3")

    def show_main_menu(self):
        self.game_state_manager.change_state("main_menu", self.main_menu)

    def show_settings(self):
        self.game_state_manager.change_state("settings_menu", self.settings_menu)

    def show_language(self):
        self.game_state_manager.change_state("language_menu", self.language_menu)

    def change_language(self, lang):
        config.set_language(lang)
        print(f"Язык изменен на: {lang}")

        # Пересоздаем меню с новым языком
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

        # Возвращаемся в меню настроек
        self.show_settings()

    def start_game(self, state):
        if state == "new_game":
            self.game_state_manager.change_state(state, self.main_menu)
            self.sound_manager.play_music("house.mp3")
        else:
            self.game_state_manager.change_state(state)

        # В файле game.py
    def run(self):
        clock = pygame.time.Clock()
        running = True
        level_width, level_height, background = create_level()
        camera = Camera(level_width, level_height)
        player = Player(level_width // 2, level_height // 2)
        all_sprites = pygame.sprite.Group(player)

        while running:
            dt = clock.tick(config.FPS) / 1000
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()

            # Счетчик FPS
            self.fps_counter += 1
            if current_time - self.last_fps_time >= 5000:  # 5 секунд
                current_fps = self.fps_counter / 5  # Средний FPS за 5 секунд
                self.fps_history.append(current_fps)
                print(f"Current FPS: {current_fps:.1f} | State: {self.game_state_manager.game_state}")
                if len(self.fps_history) > 1:
                    improvement = ((current_fps - self.fps_history[-2]) / self.fps_history[-2]) * 100
                    print(f"Performance change: {improvement:+.1f}%")
                self.fps_counter = 0
                self.last_fps_time = current_time

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if (self.game_state_manager.current_menu and
                        self.game_state_manager.should_process_menu):
                    self.game_state_manager.current_menu.handle_event(event, mouse_pos, self.sound_manager)

            # Обновление игры
            if self.game_state_manager.game_state == "new_game":
                all_sprites.update(dt, level_width, level_height)
                camera.update(player)

            # Отрисовка
            self.screen.fill((0, 0, 0))

            if self.game_state_manager.game_state == "new_game":
                self.screen.blit(background, (0, 0),
                                 (camera.offset.x, camera.offset.y, config.WIDTH, config.HEIGHT))
                for sprite in all_sprites:
                    self.screen.blit(sprite.image, camera.apply(sprite.rect))
            elif self.game_state_manager.current_menu:
                self.game_state_manager.current_menu.draw(self.screen, mouse_pos)

            pygame.display.flip()
            self.clock.tick(config.TARGET_FPS)

        self.sound_manager.stop_music()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
