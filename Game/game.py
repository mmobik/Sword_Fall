"""
Основной модуль игры.

Содержит главный класс Game, который управляет всеми аспектами игры:
инициализацией, меню, игровым процессом, диалогами и рендерингом.
"""

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
from core.game_resources import GameResources
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu
from UI.music_settings_menu import MusicSettingsMenu
from UI.talk_button import TalkButton
from UI.player_ui import PlayerUI


class Game:
    """
    Главный класс игры.
    
    Управляет всеми аспектами игры: инициализацией, меню, игровым процессом,
    диалогами, звуком и рендерингом.
    """

    def __init__(self):
        """Инициализация игры."""
        pygame.init()
        pygame.mixer.init()

        # Инициализация экрана
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
            if config.DEBUG_MODE:
                print(f"Иконка не загружена: {e}")

        # Основные параметры
        self.target_fps = config.FPS
        self.clock = pygame.time.Clock()
        self.dt = 0.0

        # Менеджеры
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)
        self.menu_handler = MenuHandler(self)

        # Инициализация компонентов
        self._init_menus()
        self._init_game_objects()

        # Отладочная информация
        self.fps_history = []
        self.last_log_time = time.time()
        self.debug_font = pygame.font.SysFont('Arial', 16)

        # Кнопка разговора
        self.talk_button_img = pygame.image.load(config.DIALOGUE_BUTTON["IMAGE_PATH"]).convert_alpha()
        self.show_talk_button = False
        self.talk_button_rect = None
        self.active_npc_obj = None
        self.talk_button_alpha = 0
        self.talk_button_target_alpha = 0
        self.talk_button_fade_speed = 800
        self.talk_button_show_delay = 0.25
        self.talk_button_enter_time = None

        # Панель диалогов
        self.dialogue_panel_img = pygame.image.load(config.DIALOGUE_PANEL["IMAGE_PATH"]).convert_alpha()
        self.show_dialogue = False
        self.dialogue_text = ""
        self.dialogue_start_time = 0
        self.dialogue_font = pygame.font.SysFont('Arial', config.DIALOGUE_PANEL["FONT_SIZE"])
        self.dialogue_text_shown = ""
        self.dialogue_type_time = 0
        self.dialogue_type_speed = 0.025

        # Состояние управления
        self.waiting_for_first_update = False
        self.unlock_control_time = 0
        self.wait_for_key_release = False

        # Изображения NPC
        self.guard_img = config.load_npc_image("GUARD")
        self.king_img = config.load_npc_image("KING")

        # Обработчики
        self.door_handler = DoorInteractionHandler(self)
        self.dialogue_panel = DialoguePanel(self)
        self.dialogue_handler = DialogueHandler(self)
        self.talk_button = TalkButton(self)
        self.game_resources = GameResources(self)

        # Глобальное состояние инвентаря
        self.inventory_open_state = False

    def _init_menus(self):
        """Инициализация всех меню игры."""
        self.main_menu = MainMenu(
            self.sound_manager,
            self.menu_handler.show_settings,
            self.menu_handler.start_game
        )
        self.settings_menu = SettingsMenu(
            self.sound_manager,
            self.menu_handler.show_main_menu,
            self.menu_handler.show_language
        )
        self.language_menu = LanguageMenu(
            self.sound_manager,
            self.menu_handler.show_settings,
            self.menu_handler.change_language
        )
        self.music_settings_menu = MusicSettingsMenu(
            self.sound_manager,
            self.menu_handler.show_settings
        )
        self.settings_menu.set_music_callback(self.menu_handler.show_music_settings)
        self.menu_handler.show_main_menu()

    def _init_game_objects(self):
        """Инициализация игровых объектов."""
        self.player = None
        self.camera = None
        self.level = None
        self.level_renderer = None
        self.collision_handler = None
        self.collision_objects = None
        self.all_sprites = None
        self.npc_dialogues = {}
        self.interactive_objects = []
        
        # UI игрока (будет инициализирован после создания игрока)
        self.player_ui = None

    @staticmethod
    def time():
        """Возвращает текущее время."""
        return time.time()

    def show_main_menu(self):
        """Показать главное меню."""
        self.menu_handler.show_main_menu()

    def show_settings(self):
        """Показать меню настроек."""
        self.menu_handler.show_settings()

    def show_language(self):
        """Показать меню выбора языка."""
        self.menu_handler.show_language()

    def show_music_settings(self):
        """Показать меню настроек музыки."""
        self.menu_handler.show_music_settings()

    def change_language(self, lang: str):
        """Изменить язык игры."""
        self.menu_handler.change_language(lang)

    def start_game(self, state: str):
        """Начать игру с указанным состоянием."""
        self.inventory_open_state = False  # Сброс состояния инвентаря при старте новой игры
        self.menu_handler.start_game(state)

    def _update_talk_button_state(self):
        """Обновить состояние кнопки разговора."""
        self.talk_button.update_talk_button_state()

    def _update_talk_button_alpha(self):
        """Обновить прозрачность кнопки разговора."""
        self.talk_button.update_talk_button_alpha()

    def _check_talk_button_click(self, mouse_pos):
        """Проверить клик по кнопке разговора."""
        return self.talk_button.check_talk_button_click(mouse_pos)

    def _render_game(self):
        """Отрисовка игровой сцены."""
        if not all([self.player, self.camera, self.level, self.level_renderer, self.all_sprites]):
            return

        # Отрисовка уровня
        if self.level_renderer:
            self.level_renderer.render(self.virtual_screen)

        # Отрисовка спрайтов
        if self.all_sprites and self.camera:
            for sprite in self.all_sprites:
                self.virtual_screen.blit(sprite.image, self.camera.apply(sprite.rect))

        # Отрисовка индикаторов урона и лечения
        if self.player:
            self.player.draw_indicators(self.virtual_screen)

        # Отладочная отрисовка
        if config.DEBUG_MODE and self.player and self.camera:
            pygame.draw.rect(self.virtual_screen, (0, 255, 0),
                             self.camera.apply(self.player.hitbox), 1)
            if self.collision_objects:
                for obj in self.collision_objects:
                    pygame.draw.rect(self.virtual_screen, (255, 0, 0),
                                     self.camera.apply(obj['rect']), 1)

        # Отрисовка наложенных тайлов
        if self.level_renderer and self.player:
            self.level_renderer.render_overlap_tiles(
                self.virtual_screen,
                (self.player.hitbox.centerx, self.player.hitbox.centery)
            )

        # Отрисовка UI игрока
        if self.player_ui:
            self.player_ui.update(self.dt)
            self.player_ui.draw()
            
            # Отрисовка экрана смерти
            if not self.player.is_alive():
                self.player_ui.draw_death_screen()

        if config.DEBUG_MODE:
            self._draw_debug_info()

    def _update_typewriter_text(self):
        """Обновление текста с эффектом печатной машинки."""
        if self.dialogue_text_shown == self.dialogue_text:
            return

        now = time.time()
        if now - self.dialogue_type_time >= self.dialogue_type_speed:
            next_len = len(self.dialogue_text_shown) + 1
            self.dialogue_text_shown = self.dialogue_text[:next_len]
            self.dialogue_type_time = now

    def _draw_debug_info(self):
        """Отрисовка отладочной информации."""
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
        """Загрузить новую карту."""
        self.game_resources.load_new_map(map_path)

    def load_new_map(self, map_path):
        """Публичный метод для загрузки новой карты."""
        self._load_new_map(map_path)

    def update_talk_button_state(self):
        """Публичный метод для обновления состояния кнопки разговора."""
        self._update_talk_button_state()

    def render_game(self):
        """Публичный метод для отрисовки игровой сцены."""
        self._render_game()

    def update_talk_button_alpha(self):
        """Публичный метод для обновления прозрачности кнопки разговора."""
        self._update_talk_button_alpha()

    def update_typewriter_text(self):
        """Публичный метод для обновления текста с эффектом печатной машинки."""
        self._update_typewriter_text()


def main():
    """Главная функция запуска игры."""
    game = Game()
    GameLoop(game).run()


if __name__ == "__main__":
    main()
