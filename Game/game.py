import pygame
import sys
from pathlib import Path
import time
from core.config import config
from core.sound_manager import SoundManager
from core.game_state_manager import GameStateManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu
from level.player import Player
from level.camera import Camera
from level.level_manager import create_level

sys.path.append(str(Path(__file__).parent.parent))



class Game:
    def __init__(self):
        # Инициализация Pygame с оптимизациями
        pygame.init()
        pygame.mixer.init()

        # Настройки дисплея
        self.screen = pygame.display.set_mode(
            config.SCREEN_SIZE,
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED,
            vsync=1
        )
        pygame.display.set_caption(config.GAME_NAME)

        # Настройки производительности
        self.target_fps = 144
        self.clock = pygame.time.Clock()
        self.dt = 0.0

        # Игровые менеджеры
        self.sound_manager = SoundManager()
        self.game_state_manager = GameStateManager(self.sound_manager)

        # Инициализация состояний
        self._init_menus()
        self._init_game_objects()

        # Статистика
        self.fps_history = []
        self.last_log_time = time.time()
        self.debug_mode = False

    def _init_menus(self):
        """Инициализация всех меню"""
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
        """Ленивая инициализация игровых объектов"""
        self.player = None
        self.camera = None
        self.level_data = None

    def run(self):
        """Главный игровой цикл"""
        running = True

        while running:
            # Управление временем кадра
            self.dt = self.clock.tick(self.target_fps) / 1000.0

            # Логирование производительности
            current_time = time.time()
            if current_time - self.last_log_time >= 2.0:
                self._log_performance()
                self.last_log_time = current_time

            # Обработка событий
            running = self._handle_events()

            # Обновление состояния
            self._update_game_state()

            # Отрисовка
            self._render_frame()

            # Отладочная информация
            if self.debug_mode:
                self._draw_debug_info()

    def _handle_events(self) -> bool:
        """Обработка ввода"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode

            # Передаем события текущему меню
            if self.game_state_manager.current_menu:
                mouse_pos = pygame.mouse.get_pos()
                self.game_state_manager.current_menu.handle_event(event, mouse_pos)

        return True

    def _update_game_state(self):
        """Обновление игровой логики"""
        if self.game_state_manager.game_state == "new_game":
            if not self.player or not self.camera or not self.level_data:
                self._load_game_resources()

            if self.player and self.camera and self.level_data:
                self.player.update(self.dt, *self.level_data[:2])
                self.camera.update(self.player)

    def _load_game_resources(self):
        """Загрузка игровых ресурсов"""
        self.level_data = create_level()
        self.player = Player(
            self.level_data[0] // 2 - config.FRAME_SIZE[0] // 2,  # Центрирование
            self.level_data[1] // 2 - config.FRAME_SIZE[1] // 2
        )
        self.camera = Camera(*self.level_data[:2])

    def _render_frame(self):
        """Оптимизированный рендеринг с приоритетами"""
        self.screen.fill((0, 0, 0))  # Всегда очищаем экран

        # Оптимизация для меню
        if self.game_state_manager.current_menu:
            mouse_pos = pygame.mouse.get_pos()

            # Ограничиваем FPS в меню до 60 для экономии ресурсов
            if self.game_state_manager.game_state != "new_game":
                self.clock.tick(60)

            self.game_state_manager.current_menu.draw(self.screen, mouse_pos)

        # Полный FPS в игре
        elif self.game_state_manager.game_state == "new_game":
            self._render_game()
            self.clock.tick(self.target_fps)

        pygame.display.flip()

    def _render_game(self):
        """Отрисовка игрового уровня"""
        if not self.player or not self.camera or not self.level_data:
            return

        # Фон
        bg_rect = (
            self.camera.offset.x,
            self.camera.offset.y,
            config.WIDTH,
            config.HEIGHT
        )
        self.screen.blit(self.level_data[2], (0, 0), bg_rect)

        # Персонаж
        self.screen.blit(
            self.player.image,
            self.camera.apply(self.player.rect)
        )

    def _log_performance(self):
        """Логирование статистики"""
        current_fps = self.clock.get_fps()
        self.fps_history.append(current_fps)
        print(f"[PERF] FPS: {current_fps:.1f} | State: {self.game_state_manager.game_state}")

    def _draw_debug_info(self):
        """Отрисовка отладочной информации"""
        font = pygame.font.SysFont('Arial', 20)
        debug_text = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"State: {self.game_state_manager.game_state}",
        ]

        if self.player:
            debug_text.append(f"Player: ({self.player.rect.x:.0f}, {self.player.rect.y:.0f})")

        for i, text in enumerate(debug_text):
            surface = font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, 10 + i * 25))

    # Методы управления состоянием ------------------------------------------------
    def show_main_menu(self):
        """Переход в главное меню"""
        self.game_state_manager.change_state("main_menu", self.main_menu)
        self.sound_manager.play_music("Dark_fantasm.mp3")

    def show_settings(self):
        """Открытие настроек"""
        self.game_state_manager.change_state("settings_menu", self.settings_menu)

    def show_language(self):
        """Открытие языковых настроек"""
        self.game_state_manager.change_state("language_menu", self.language_menu)

    def change_language(self, lang: str):
        """Смена языка с обновлением всех меню"""
        if config.current_language == lang:
            return

        # Сохраняем текущее состояние мыши для плавного перехода
        current_mouse_pos = pygame.mouse.get_pos()

        config.set_language(lang)
        print(f"Язык изменен на: {lang}")

        # Обновляем текстуры во всех меню с проверкой изменений
        if hasattr(self.main_menu, 'update_textures'):
            self.main_menu.update_textures()
        if hasattr(self.settings_menu, 'update_textures'):
            self.settings_menu.update_textures()
        if hasattr(self.language_menu, 'update_textures'):
            self.language_menu.update_textures()

        # Возвращаемся в меню настроек с сохранением позиции мыши
        self.show_settings()

        # Принудительно обновляем отрисовку для предотвращения мерцания
        if self.game_state_manager.current_menu:
            self.game_state_manager.current_menu.draw(self.screen, current_mouse_pos)
            pygame.display.flip()

    def start_game(self, state: str):
        """Запуск игры"""
        if state == "new_game":
            self.game_state_manager.change_state(state, None)
            self.sound_manager.play_music("house.mp3")
        else:
            self.game_state_manager.change_state(state)


if __name__ == "__main__":
    game = Game()
    game.run()
