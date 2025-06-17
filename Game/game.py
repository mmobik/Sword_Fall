import pygame
import sys
import time
from core.config import config
from core.sound_manager import SoundManager
from core.game_state_manager import GameStateManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu
from level.player import Player
from level.camera import Camera
from level.level_renderer import LevelRenderer
from level.collisions import CollisionHandler
import pytmx


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Виртуальный экран для масштабирования
        self.virtual_screen = pygame.Surface((config.VIRTUAL_WIDTH, config.VIRTUAL_HEIGHT))
        self.screen = pygame.display.set_mode(
            config.SCREEN_SIZE,
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED,
            vsync=1
        )
        pygame.display.set_caption(config.GAME_NAME)

        # Загрузка иконки
        try:
            icon = pygame.image.load(config.ASSETS["ICON"])
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Иконка не загружена: {e}")

        self.target_fps = config.FPS
        self.clock = pygame.time.Clock()
        self.dt = 0.0

        # Менеджеры
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)

        # Меню
        self._init_menus()
        self._init_game_objects()

        # Статистика
        self.fps_history = []
        self.last_log_time = time.time()
        self.debug_mode = True  # Включаем дебаг по умолчанию
        self.debug_font = pygame.font.SysFont('Arial', 16)

    def _init_menus(self):
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
        self.show_main_menu()

    def _init_game_objects(self):
        self.player = None
        self.camera = None
        self.level = None
        self.level_renderer = None
        self.collision_handler = None
        self.collision_objects = None
        self.all_sprites = None

    def run(self):
        running = True
        while running:
            self.dt = self.clock.tick(self.target_fps) / 1000.0
            current_time = time.time()
            if current_time - self.last_log_time >= 2.0:
                self._log_performance()
                self.last_log_time = current_time
            running = self._handle_events()
            self._update_game_state()
            self._render_frame()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                if event.key == pygame.K_ESCAPE and self.game_state_manager.game_state == "new_game":
                    self.show_main_menu()
            if self.game_state_manager.current_menu:
                mouse_pos = pygame.mouse.get_pos()
                self.game_state_manager.current_menu.handle_event(event, mouse_pos)
        return True

    def _update_game_state(self):
        if self.game_state_manager.game_state == "new_game":
            if not self.player or not self.camera or not self.level:
                self._load_game_resources()
            if self.player and self.camera and self.level and self.all_sprites:
                self.all_sprites.update(
                    self.dt,
                    self.level.width * self.level.tilewidth,
                    self.level.height * self.level.tileheight,
                    self.collision_objects
                )
                self.camera.update(self.player)

    def _load_game_resources(self):
        try:
            print("Загрузка карты...")
            self.level = pytmx.TiledMap(config.LEVEL_MAP_PATH)
            map_width = self.level.width * self.level.tilewidth
            map_height = self.level.height * self.level.tileheight
            print(f"Карта загружена. Размер: {map_width}x{map_height}")

            self.collision_handler = CollisionHandler()
            self.collision_objects = self.collision_handler.load_collision_objects(self.level)
            print(f"Загружено объектов коллизий: {len(self.collision_objects)}")

            print("Создание игрока...")
            # Поиск спавна игрока в карте
            spawn_x = 200  # Fallback позиция по X
            spawn_y = 200  # Fallback позиция по Y
            
            # Ищем слой PlayerSpawn
            for layer in self.level.layers:
                if hasattr(layer, 'name') and layer.name == "PlayerSpawn":
                    # Ищем объект спавна в слое
                    for obj in layer:
                        if hasattr(obj, 'properties') and obj.properties.get("object_type") == "player_spawn":
                            spawn_x = int(obj.x)
                            spawn_y = int(obj.y)
                            print(f"Найден спавн игрока: ({spawn_x}, {spawn_y})")
                            break
                    break
            else:
                print(f"Спавн не найден, используем fallback: ({spawn_x}, {spawn_y})")
            
            self.player = Player(spawn_x, spawn_y)
            print(f"Игрок создан. Позиция: {self.player.hitbox.topleft}")
            print(f"Размер спрайта: {self.player.image.get_size()}")
            print(f"Размер хитбокса: {self.player.hitbox.size}")

            self.all_sprites = pygame.sprite.GroupSingle(self.player)
            self.camera = Camera(map_width, map_height)
            self.level_renderer = LevelRenderer(self.level, self.camera)

        except Exception as e:
            print(f"Ошибка загрузки ресурсов: {e}")
            raise

    def _render_frame(self):
        if self.game_state_manager.current_menu:
            self.screen.fill((0, 0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.game_state_manager.current_menu.draw(self.screen, mouse_pos)
            pygame.display.flip()
        elif self.game_state_manager.game_state == "new_game":
            self.virtual_screen.fill((0, 0, 0))
            self._render_game()
            scaled_screen = pygame.transform.scale(self.virtual_screen, (config.WIDTH, config.HEIGHT))
            self.screen.blit(scaled_screen, (0, 0))
            pygame.display.flip()

    def _render_game(self):
        if not self.player or not self.camera or not self.level or not self.level_renderer or not self.all_sprites:
            return

        # Рендер уровня
        self.level_renderer.render(self.virtual_screen)

        # Рендер игрока
        for sprite in self.all_sprites:
            self.virtual_screen.blit(sprite.image, self.camera.apply(sprite.rect))

        # Дебаг-отрисовка
        if self.debug_mode:
            # Хитбокс игрока
            pygame.draw.rect(self.virtual_screen, (0, 255, 0), self.camera.apply(self.player.hitbox), 1)
            # Центр хитбокса
            pygame.draw.circle(self.virtual_screen, (255, 0, 255), self.camera.apply(self.player.hitbox).center, 3)
            # Коллизии
            if self.collision_objects:
                for obj in self.collision_objects:
                    pygame.draw.rect(self.virtual_screen, (255, 0, 0), self.camera.apply(obj['rect']), 1)

        # Оверлап-тайлы
        self.level_renderer.render_overlap_tiles(
            self.virtual_screen,
            (self.player.hitbox.centerx, self.player.hitbox.centery)
        )

        # Теперь debug-информация будет поверх всего
        if self.debug_mode:
            self._draw_debug_info()

    def _log_performance(self):
        current_fps = self.clock.get_fps()
        self.fps_history.append(current_fps)
        print(f"[PERF] FPS: {current_fps:.1f} | State: {self.game_state_manager.game_state}")

    def _draw_debug_info(self):
        debug_text = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"State: {self.game_state_manager.game_state}",
            f"Player Pos: {self.player.rect.topleft if self.player else 'N/A'}",
            f"Player Hitbox: {self.player.hitbox.topleft if self.player else 'N/A'}",
            f"Camera Offset: {self.camera.offset if self.camera else 'N/A'}",
            f"Frame: {self.player.current_frame if self.player else 'N/A'}",
            f"Anim State: {self.player.state_name if self.player else 'N/A'}"
        ]

        for i, text in enumerate(debug_text):
            surface = self.debug_font.render(text, True, (255, 255, 255))
            self.virtual_screen.blit(surface, (10, 10 + i * 20))

    # Методы управления состоянием ------------------------------------------------
    def show_main_menu(self):
        self.game_state_manager.change_state("main_menu", self.main_menu)
        self.sound_manager.play_music("Dark_fantasm.mp3")

    def show_settings(self):
        self.game_state_manager.change_state("settings_menu", self.settings_menu)

    def show_language(self):
        self.game_state_manager.change_state("language_menu", self.language_menu)

    def change_language(self, lang: str):
        if config.current_language == lang:
            return
        current_mouse_pos = pygame.mouse.get_pos()
        config.set_language(lang)
        print(f"Язык изменен на: {lang}")
        if hasattr(self.main_menu, 'update_textures'):
            self.main_menu.update_textures()
        if hasattr(self.settings_menu, 'update_textures'):
            self.settings_menu.update_textures()
        if hasattr(self.language_menu, 'update_textures'):
            self.language_menu.update_textures()
        self.show_settings()
        if self.game_state_manager.current_menu:
            self.game_state_manager.current_menu.draw(self.screen, current_mouse_pos)
            pygame.display.flip()

    def start_game(self, state: str):
        if state == "new_game":
            self.game_state_manager.change_state(state, None)
            self.sound_manager.play_music("house.mp3")
        else:
            self.game_state_manager.change_state(state)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
