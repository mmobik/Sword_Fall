import pygame
from sound_manager import SoundManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from config import WIDTH, HEIGHT, TARGET_FPS, ASSETS, FPS
from game_state_manager import GameStateManager
from player import Player
from camera import Camera
from level_manager import create_level


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Инициализация mixer
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("GAME_NAME")
        icon = pygame.image.load(ASSETS["ICON"])
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)
        self.main_menu = MainMenu(self.sound_manager, lambda: self.toggle_settings(), self.change_game_state)
        self.settings_menu = SettingsMenu(self.sound_manager, lambda: self.toggle_settings())
        pygame.mixer.music.load("Sounds/Soundtracks/Dark_fantasm.mp3")
        pygame.mixer.music.play(-1)

    def toggle_settings(self):
        if self.game_state_manager.get_state() == "main_menu":
            self.game_state_manager.change_state("settings_menu", self.settings_menu)
        else:
            self.game_state_manager.change_state("main_menu", self.main_menu)

    def change_game_state(self, new_state, menu=None):
        self.game_state_manager.change_state(new_state, menu)
        if new_state == "new_game":
            self.sound_manager.play_music("House.mp3")
        elif new_state == "main_menu":
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("Sounds/Soundracks/Dark_fantasm.mp3")
                pygame.mixer.music.play(-1)

    def run(self):
        clock = pygame.time.Clock()  # Используем clock из self
        running = True
        level_width, level_height, background = create_level()
        camera = Camera(level_width, level_height)
        player = Player(WIDTH // 2, HEIGHT // 2)  # Передаем размеры экрана из конфига
        all_sprites = pygame.sprite.Group(player)

        while running:
            dt = clock.tick(FPS) / 1000
            mouse_pos = pygame.mouse.get_pos() # Получаем позицию мыши

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # === ВАЖНО! Проверь этот блок ===
                current_state = self.game_state_manager.get_state()
                print(f"Current game state: {current_state}")  # Добавили отладочное сообщение

                if current_state == "settings_menu":
                    print("Calling settings_menu.handle_event")  # Добавили отладочное сообщение
                    self.settings_menu.handle_event(event, mouse_pos, self.sound_manager)
                elif current_state == "main_menu":
                    print("Calling main_menu.handle_event")  # Добавили отладочное сообщение
                    self.main_menu.handle_event(event, mouse_pos, self.sound_manager)
                # === Конец важного блока ===

            # Обновление
            all_sprites.update(dt, level_width, level_height)
            camera.update(player)

            # Отрисовка
            if self.game_state_manager.get_state() == "new_game":
                self.screen.blit(background, (0, 0), (camera.offset.x, camera.offset.y, WIDTH, HEIGHT))
                for sprite in all_sprites:
                    self.screen.blit(sprite.image, camera.apply(sprite.rect))
            else:
                # Отрисовка меню и настроек (из SwordFall)
                mouse_pos = pygame.mouse.get_pos() # Получаем позицию мыши
                if self.game_state_manager.get_state() == "settings_menu":
                    self.settings_menu.draw(self.screen, mouse_pos)
                elif self.game_state_manager.get_state() == "main_menu":
                    self.main_menu.draw(self.screen, mouse_pos)
                elif self.game_state_manager.get_state() == "new_game":
                    self.screen.blit(self.game_state_manager.new_game_background, (0, 0))

            pygame.display.flip()
            self.clock.tick(TARGET_FPS)  # Используем clock из self
        self.sound_manager.stop_music()
        # pygame.quit() #Не нужно вызывать, т.к. вызывается в game_state_manager


if __name__ == "__main__":
    game = Game()
    game.run()
