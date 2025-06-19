import pygame
import time
from core.config import config
from core.game_loop import GameLoop
from core.dialogue_handler import DialogueHandler
from core.dialogue_panel import DialoguePanel
from core.door_handler import DoorInteractionHandler
from core.sound_manager import SoundManager
from core.game_state_manager import GameStateManager
from core.menu_handler import MenuHandler
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu
from UI.music_settings_menu import MusicSettingsMenu
from level.player import Player
from level.camera import Camera
from level.level_renderer import LevelRenderer
from level.collisions import CollisionHandler
import pytmx
from UI.talk_button import TalkButton


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.virtual_screen = pygame.Surface((config.VIRTUAL_WIDTH, config.VIRTUAL_HEIGHT))
        self.screen = pygame.display.set_mode(
            config.SCREEN_SIZE,
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED,
            vsync=1
        )
        pygame.display.set_caption(config.GAME_NAME)
        try:
            icon = pygame.image.load(config.ASSETS["ICON"])
            pygame.display.set_icon(icon)
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Иконка не загружена: {e}")
        self.target_fps = config.FPS
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)
        self.menu_handler = MenuHandler(self)
        self._init_menus()
        self._init_game_objects()
        self.fps_history = []
        self.last_log_time = time.time()
        self.debug_font = pygame.font.SysFont('Arial', 16)
        self.talk_button_img = pygame.image.load(config.DIALOGUE_BUTTON["IMAGE_PATH"]).convert_alpha()
        self.show_talk_button = False
        self.talk_button_rect = None
        self.active_npc_obj = None
        self.talk_button_alpha = 0
        self.talk_button_target_alpha = 0
        self.talk_button_fade_speed = 800
        self.talk_button_show_delay = 0.25
        self.talk_button_enter_time = None
        self.dialogue_panel_img = pygame.image.load(config.DIALOGUE_PANEL["IMAGE_PATH"]).convert_alpha()
        self.show_dialogue = False
        self.dialogue_text = ""
        self.dialogue_start_time = 0
        self.dialogue_font = pygame.font.SysFont('Arial', config.DIALOGUE_PANEL["FONT_SIZE"])
        self.dialogue_text_shown = ""
        self.dialogue_type_time = 0
        self.dialogue_type_speed = 0.025
        self.waiting_for_first_update = False
        self.unlock_control_time = 0
        self.wait_for_key_release = False
        self.guard_img = config.load_npc_image("GUARD")
        self.king_img = config.load_npc_image("KING")
        self.door_handler = DoorInteractionHandler(self)
        self.dialogue_panel = DialoguePanel(self)
        self.dialogue_handler = DialogueHandler(self)
        self.talk_button = TalkButton(self)

    def _init_menus(self):
        self.main_menu = MainMenu(self.sound_manager, self.menu_handler.show_settings, self.menu_handler.start_game)
        self.settings_menu = SettingsMenu(self.sound_manager, self.menu_handler.show_main_menu, self.menu_handler.show_language)
        self.language_menu = LanguageMenu(self.sound_manager, self.menu_handler.show_settings, self.menu_handler.change_language)
        self.music_settings_menu = MusicSettingsMenu(self.sound_manager, self.menu_handler.show_settings)
        self.settings_menu.set_music_callback(self.menu_handler.show_music_settings)
        self.menu_handler.show_main_menu()

    def _init_game_objects(self):
        self.player = None
        self.camera = None
        self.level = None
        self.level_renderer = None
        self.collision_handler = None
        self.collision_objects = None
        self.all_sprites = None
        self.npc_dialogues = {}
        self.interactive_objects = []

    def time(self):
        return time.time()

    # Методы-прокси для совместимости
    def show_main_menu(self):
        self.menu_handler.show_main_menu()

    def show_settings(self):
        self.menu_handler.show_settings()

    def show_language(self):
        self.menu_handler.show_language()

    def show_music_settings(self):
        self.menu_handler.show_music_settings()

    def change_language(self, lang: str):
        self.menu_handler.change_language(lang)

    def start_game(self, state: str):
        self.menu_handler.start_game(state)

    # Методы-прокси для talk button
    def _update_talk_button_state(self):
        self.talk_button.update_talk_button_state()

    def _update_talk_button_alpha(self):
        self.talk_button.update_talk_button_alpha()

    def _check_talk_button_click(self, mouse_pos):
        return self.talk_button.check_talk_button_click(mouse_pos)

    # Методы-прокси для загрузки ресурсов и рендеринга
    def _load_game_resources(self):
        try:
            if config.DEBUG_MODE:
                print("Загрузка карты...")
            self.level = pytmx.TiledMap(config.LEVEL_MAP_PATH)
            map_width = self.level.width * self.level.tilewidth
            map_height = self.level.height * self.level.tileheight
            if config.DEBUG_MODE:
                print(f"Карта загружена. Размер: {map_width}x{map_height}")

            self.collision_handler = CollisionHandler()
            self.collision_objects = self.collision_handler.load_collision_objects(self.level)
            self.interactive_objects = []
            for layer in self.level.layers:
                if hasattr(layer, 'name') and hasattr(layer, '__iter__'):
                    for obj in layer:
                        if hasattr(obj, 'properties') and obj.properties.get('interactive', False):
                            self.interactive_objects.append(obj)
            if config.DEBUG_MODE:
                print(f"Загружено объектов коллизий: {len(self.collision_objects)}")

            if config.DEBUG_MODE:
                print("Создание игрока...")

            spawn_x = 200
            spawn_y = 200

            spawn_found = False
            spawn_point_name = getattr(self, 'next_spawn_point_name', None)
            if spawn_point_name:
                for layer in self.level.layers:
                    if hasattr(layer, 'name') and layer.name == "PlayerSpawn":
                        for obj in layer:
                            if (hasattr(obj, 'properties') and obj.properties.get("object_type") == spawn_point_name) or \
                               (hasattr(obj, 'name') and obj.name == spawn_point_name):
                                spawn_x = int(obj.x)
                                spawn_y = int(obj.y)
                                spawn_found = True
                                break
                        if spawn_found:
                            break
                self.next_spawn_point_name = None

            if not spawn_found:
                for layer in self.level.layers:
                    if hasattr(layer, 'name') and layer.name == "PlayerSpawn":
                        for obj in layer:
                            if hasattr(obj, 'properties') and obj.properties.get("object_type") == "player_spawn":
                                spawn_x = int(obj.x)
                                spawn_y = int(obj.y)
                                if config.DEBUG_MODE:
                                    print(f"Найден спавн игрока: ({spawn_x}, {spawn_y})")
                                break
                        break
                else:
                    if config.DEBUG_MODE:
                        print(f"Спавн не найден, используем fallback: ({spawn_x}, {spawn_y})")
            
            self.player = Player(spawn_x, spawn_y, self.sound_manager)
            if config.DEBUG_MODE:
                print(f"Игрок создан. Позиция: {self.player.hitbox.topleft}")
                print(f"Размер спрайта: {self.player.image.get_size()}")
                print(f"Размер хитбокса: {self.player.hitbox.size}")

            self.all_sprites = pygame.sprite.Group()
            self.all_sprites.add(self.player)
            self.camera = Camera(map_width, map_height)
            self.level_renderer = LevelRenderer(self.level, self.camera)
            self.player.update(0, map_width, map_height, self.collision_objects)
            self.camera.update(self.player)

        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка загрузки ресурсов: {e}")
            raise

    def _render_game(self):
        if not self.player or not self.camera or not self.level or not self.level_renderer or not self.all_sprites:
            return
        self.level_renderer.render(self.virtual_screen)
        for sprite in self.all_sprites:
            self.virtual_screen.blit(sprite.image, self.camera.apply(sprite.rect))
        if config.DEBUG_MODE:
            pygame.draw.rect(self.virtual_screen, (0, 255, 0), self.camera.apply(self.player.hitbox), 1)
            if self.collision_objects:
                for obj in self.collision_objects:
                    pygame.draw.rect(self.virtual_screen, (255, 0, 0), self.camera.apply(obj['rect']), 1)
        self.level_renderer.render_overlap_tiles(
            self.virtual_screen,
            (self.player.hitbox.centerx, self.player.hitbox.centery)
        )
        if config.DEBUG_MODE:
            self._draw_debug_info()

    def _update_typewriter_text(self):
        if self.dialogue_text_shown == self.dialogue_text:
            return
        now = time.time()
        if now - self.dialogue_type_time >= self.dialogue_type_speed:
            next_len = len(self.dialogue_text_shown) + 1
            self.dialogue_text_shown = self.dialogue_text[:next_len]
            self.dialogue_type_time = now

    def _draw_debug_info(self):
        debug_text = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"State: {self.game_state_manager.game_state}",
            f"Player Pos: {self.player.rect.topleft if self.player else 'N/A'}",
            f"Player Hitbox: {self.player.hitbox.topleft if self.player else 'N/A'}",
            f"Hitbox Size: {self.player.hitbox.size if self.player else 'N/A'}",
            f"Camera Offset: {self.camera.offset if self.camera else 'N/A'}",
            f"Frame: {self.player.current_frame if self.player else 'N/A'}",
            f"Anim State: {self.player.state_name if self.player else 'N/A'}",
            f"Objects: {len(self.collision_objects) if self.collision_objects else 0}",
        ]
        for i, text in enumerate(debug_text):
            surface = self.debug_font.render(text, True, (255, 255, 255))
            self.virtual_screen.blit(surface, (10, 10 + i * 20))

    def _load_new_map(self, map_path):
        # Сохраняем путь в конфиг, чтобы корректно работала загрузка
        config.LEVEL_MAP_PATH = map_path
        self._load_game_resources()
        self.waiting_for_first_update = True
        self.wait_for_key_release = True


def main():
    game = Game()
    GameLoop(game).run()


if __name__ == "__main__":
    main()
