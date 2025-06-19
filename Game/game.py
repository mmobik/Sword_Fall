import pygame
import time
from core.config import config
from core.sound_manager import SoundManager
from core.game_state_manager import GameStateManager
from UI.main_menu import MainMenu
from UI.settings_menu import SettingsMenu
from UI.language_menu import LanguageMenu
from UI.music_settings_menu import MusicSettingsMenu
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
            if config.DEBUG_MODE:
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
        self.debug_font = pygame.font.SysFont('Arial', 16)

        self.talk_button_img = pygame.image.load(config.DIALOGUE_BUTTON["IMAGE_PATH"]).convert_alpha()
        self.show_talk_button = False
        self.talk_button_rect = None
        self.active_npc_obj = None
        self.talk_button_alpha = 0  # Текущий альфа-канал кнопки (0-255)
        self.talk_button_target_alpha = 0  # Целевой альфа-канал (0 или 255)
        self.talk_button_fade_speed = 800  # скорость изменения альфы (значение в секундах, пикс/сек)
        self.talk_button_show_delay = 0.25  # Задержка перед появлением кнопки (сек)
        self.talk_button_enter_time = None  # Время входа в зону взаимодействия

        # Диалоговое окно
        self.dialogue_panel_img = pygame.image.load(config.DIALOGUE_PANEL["IMAGE_PATH"]).convert_alpha()
        self.show_dialogue = False
        self.dialogue_text = ""  # Полный текст
        self.dialogue_start_time = 0
        self.dialogue_font = pygame.font.SysFont('Arial', config.DIALOGUE_PANEL["FONT_SIZE"])
        self.dialogue_text_shown = ""  # Текст, который уже показан
        self.dialogue_type_time = 0  # Время последнего появления символа
        self.dialogue_type_speed = 0.025  # Задержка между символами (сек)

        self.waiting_for_first_update = False  # Блокировка управления до первой отрисовки после fade
        self.unlock_control_time = 0  # (больше не используется)
        self.wait_for_key_release = False  # Ждать отпускания всех клавиш после fade

        # --- ДОБАВЛЕНО: Картинка стражника ---
        self.guard_img = None
        try:
            self.guard_img = pygame.image.load("assets/images/game/The guard_4.png").convert_alpha()
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Guard image not loaded: {e}")

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
        self.music_settings_menu = MusicSettingsMenu(
            self.sound_manager,
            self.show_settings
        )
        
        # Устанавливаем callback для кнопки музыки
        self.settings_menu.set_music_callback(self.show_music_settings)
        
        self.show_main_menu()

    def _init_game_objects(self):
        self.player = None
        self.camera = None
        self.level = None
        self.level_renderer = None
        self.collision_handler = None
        self.collision_objects = None
        self.all_sprites = None
        self.npc_dialogues = {}  # npc_id -> dialogue instance
        self.interactive_objects = []  # Список интерактивных объектов

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
        self._update_talk_button_state()
        if self.waiting_for_first_update:
            # Блокируем все действия игрока до первой отрисовки уровня
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
            return True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    config.set_debug_mode(not config.DEBUG_MODE)
                if event.key == pygame.K_ESCAPE and self.game_state_manager.game_state == "new_game":
                    # Остановить звук шагов при выходе в меню
                    steps_channel = getattr(self.player, '_steps_channel', None)
                    if steps_channel:
                        steps_channel.stop()
                        setattr(self.player, '_steps_channel', None)
                    if self.player:
                        self.player.is_walking = False
                    self.show_main_menu()
                if event.key == pygame.K_e and self.game_state_manager.game_state == "new_game":
                    self._try_interact_with_npc()
            if self.game_state_manager.current_menu:
                mouse_pos = pygame.mouse.get_pos()
                self.game_state_manager.current_menu.handle_event(event, mouse_pos)
        return True

    def _update_game_state(self):
        # Обновляем текущее меню если оно есть
        if self.game_state_manager.current_menu:
            self.game_state_manager.current_menu.update(self.dt)
            
        if self.game_state_manager.game_state == "new_game":
            if not self.player or not self.camera or not self.level:
                self._load_game_resources()
                self.waiting_for_first_update = True
            if self.player and self.camera and self.level and self.all_sprites and not self.waiting_for_first_update:
                # Если нужно ждать отпускания клавиш — не двигаем игрока
                if not self.wait_for_key_release:
                    self.all_sprites.update(
                        self.dt,
                        self.level.width * self.level.tilewidth,
                        self.level.height * self.level.tileheight,
                        self.collision_objects
                    )
                    self.camera.update(self.player)
                else:
                    keys = pygame.key.get_pressed()
                    # Клавиши движения: W, A, S, D, стрелки
                    move_keys = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                                 pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
                    if not any(keys[k] for k in move_keys):
                        self.wait_for_key_release = False
            # Снимаем блокировку только после первой успешной загрузки и отрисовки
            if self.waiting_for_first_update and self.player and self.camera and self.level and self.all_sprites:
                self.waiting_for_first_update = False
                self.wait_for_key_release = True

    def _load_game_resources(self):
        try:
            # Лог загрузки карты
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
            # Синхронизируем rect и hitbox игрока сразу после создания
            self.player.update(0, map_width, map_height, self.collision_objects)
            # Центрируем камеру на игроке сразу после загрузки
            self.camera.update(self.player)

        except Exception as e:
            if config.DEBUG_MODE:
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
            self._update_talk_button_alpha()
            # Показываем кнопку только если не показывается диалог
            if self.talk_button_img and self.talk_button_alpha > 0 and not self.show_dialogue:
                btn_w, btn_h = self.talk_button_img.get_size()
                if self.player and self.camera:
                    player_screen_x = self.player.hitbox.centerx - self.camera.offset.x
                    player_screen_y = self.player.hitbox.centery - self.camera.offset.y
                    x = player_screen_x - btn_w // 2
                    y = player_screen_y - btn_h + config.DIALOGUE_BUTTON["OFFSET_Y"]
                else:
                    x = (config.VIRTUAL_WIDTH - btn_w) // 2
                    y = config.VIRTUAL_HEIGHT - btn_h - config.DIALOGUE_BUTTON["FALLBACK_Y"]
                btn_img = self.talk_button_img.copy()
                btn_img.set_alpha(int(self.talk_button_alpha))
                self.virtual_screen.blit(btn_img, (x, y))
                self.talk_button_rect = pygame.Rect(x, y, btn_w, btn_h)
            
            # Отрисовка диалогового окна
            if self.show_dialogue and self.dialogue_panel_img:
                self._update_typewriter_text()
                self._render_dialogue_panel()
                # Автоматическое скрытие диалога через заданное время
                if time.time() - self.dialogue_start_time > config.DIALOGUE_PANEL["SHOW_DURATION"]:
                    self.show_dialogue = False
                    self.dialogue_text = ""
                    self.dialogue_text_shown = ""
                    self.active_npc_obj = None  # Сбросить активного NPC, чтобы убрать картинку стражника
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

        if config.DEBUG_MODE:

            # Хитбокс игрока
            pygame.draw.rect(self.virtual_screen, (0, 255, 0), self.camera.apply(self.player.hitbox), 1)

            # Коллизии
            if self.collision_objects:
                for obj in self.collision_objects:
                    pygame.draw.rect(self.virtual_screen, (255, 0, 0), self.camera.apply(obj['rect']), 1)

        # Оверлап-тайлы
        self.level_renderer.render_overlap_tiles(
            self.virtual_screen,
            (self.player.hitbox.centerx, self.player.hitbox.centery)
        )

        if config.DEBUG_MODE:
            self._draw_debug_info()

    def _log_performance(self):
        current_fps = self.clock.get_fps()
        self.fps_history.append(current_fps)
        if config.DEBUG_MODE:
            print(f"[PERF] FPS: {current_fps:.1f} | State: {self.game_state_manager.game_state}")

    def _draw_debug_info(self):
        # Базовая информация для дебага
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

    # Методы управления состоянием
    def show_main_menu(self):
        self.game_state_manager.change_state("main_menu", self.main_menu)
        self.sound_manager.play_music("Dark_fantasm.mp3")

    def show_settings(self):
        self.game_state_manager.change_state("settings_menu", self.settings_menu)

    def show_language(self):
        self.game_state_manager.change_state("language_menu", self.language_menu)

    def show_music_settings(self):
        self.game_state_manager.change_state("music_settings_menu", self.music_settings_menu)

    def change_language(self, lang: str):
        if config.current_language == lang:
            return
        current_mouse_pos = pygame.mouse.get_pos()
        config.set_language(lang)
        if config.DEBUG_MODE:
            print(f"Язык изменен на: {lang}")
        if hasattr(self.main_menu, 'update_textures'):
            self.main_menu.update_textures()
        if hasattr(self.settings_menu, 'update_textures'):
            self.settings_menu.update_textures()
        if hasattr(self.language_menu, 'update_textures'):
            self.language_menu.update_textures()
        if hasattr(self.music_settings_menu, 'update_textures'):
            self.music_settings_menu.update_textures()
        self.show_settings()
        if self.game_state_manager.current_menu:
            self.game_state_manager.current_menu.draw(self.screen, current_mouse_pos)
            pygame.display.flip()

    def start_game(self, state: str):
        if state == "new_game":
            self.waiting_for_first_update = True
            self.wait_for_key_release = False
            self.game_state_manager.change_state(state, None)
            self.sound_manager.play_music("Central Hall.mp3")
        else:
            self.game_state_manager.change_state(state)

    def _update_talk_button_state(self):
        prev = self.show_talk_button
        self.show_talk_button = False
        if not self.show_dialogue:
            self.active_npc_obj = None
        in_zone = False
        if not self.player or not self.interactive_objects:
            self.talk_button_target_alpha = 0
            self.talk_button_enter_time = None
            return
        player_rect = self.player.hitbox
        for obj in self.interactive_objects:
            obj_rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
            npc_type = obj.properties.get('interactive_type', '').lower()
            if (npc_type == 'the guard' or npc_type == 'royal_guard') and player_rect.colliderect(obj_rect.inflate(10, 10)):
                in_zone = True
                self.active_npc_obj = obj
                break
        now = time.time()
        if in_zone:
            if self.talk_button_enter_time is None:
                self.talk_button_enter_time = now
            if (now - self.talk_button_enter_time) >= self.talk_button_show_delay and not self.show_dialogue:
                self.show_talk_button = True
        else:
            self.talk_button_enter_time = None
        # Меняем целевую альфу в зависимости от состояния
        if self.show_talk_button and not self.show_dialogue:
            self.talk_button_target_alpha = 255
        else:
            self.talk_button_target_alpha = 0

    def _update_talk_button_alpha(self):
        # Плавно изменяем альфу к целевому значению
        dt = self.dt if hasattr(self, 'dt') else 1/144
        speed = self.talk_button_fade_speed * dt
        if self.talk_button_alpha < self.talk_button_target_alpha:
            self.talk_button_alpha = min(self.talk_button_target_alpha, self.talk_button_alpha + speed)
        elif self.talk_button_alpha > self.talk_button_target_alpha:
            self.talk_button_alpha = max(self.talk_button_target_alpha, self.talk_button_alpha - speed)

    def _try_interact_with_npc(self):
        if self.show_dialogue:
            # Пока окно открыто, не даем открыть новую реплику
            return
        obj = self.active_npc_obj
        if obj is None:
            return
        npc_type = obj.properties.get('interactive_type', '').lower()
        npc_id = getattr(obj, 'id', id(obj))
        if npc_type == 'the guard' or npc_type == 'royal_guard':
            from dialogues.npc_dialogues import RoyalGuardDialogue
            if npc_id not in self.npc_dialogues:
                self.npc_dialogues[npc_id] = RoyalGuardDialogue(npc_id)
            dialogue = self.npc_dialogues[npc_id]
            # Показываем диалог на экране вместо вывода в терминал
            self.dialogue_text = dialogue.get_current_dialogue()
            self.dialogue_text_shown = ""
            self.dialogue_type_time = time.time()
            self.show_dialogue = True
            self.dialogue_start_time = time.time()
            dialogue.next_dialogue()
        # Здесь можно добавить обработку других типов NPC

    def _check_talk_button_click(self, mouse_pos):
        """Проверяет клик по кнопке с учетом прозрачности"""
        if not self.talk_button_rect or not self.talk_button_rect.collidepoint(mouse_pos):
            return False
        
        # Получаем локальные координаты относительно кнопки
        local_x = mouse_pos[0] - self.talk_button_rect.x
        local_y = mouse_pos[1] - self.talk_button_rect.y
        
        # Проверяем, что координаты в пределах изображения
        if (0 <= local_x < self.talk_button_img.get_width() and 
            0 <= local_y < self.talk_button_img.get_height()):
            # Получаем цвет пикселя (включая альфа-канал)
            pixel_color = self.talk_button_img.get_at((local_x, local_y))
            # Проверяем, что пиксель не полностью прозрачный (альфа > 0)
            return pixel_color[3] > 0
        
        return False

    def _update_typewriter_text(self):
        # Постепенно увеличиваем количество отображаемых символов
        if self.dialogue_text_shown == self.dialogue_text:
            return
        now = time.time()
        if now - self.dialogue_type_time >= self.dialogue_type_speed:
            next_len = len(self.dialogue_text_shown) + 1
            self.dialogue_text_shown = self.dialogue_text[:next_len]
            self.dialogue_type_time = now

    def _render_dialogue_panel(self):
        """Отрисовка панели диалога с текстом и именем NPC"""
        panel_w, panel_h = self.dialogue_panel_img.get_size()
        
        # Позиция панели снизу экрана
        x = (config.VIRTUAL_WIDTH - panel_w) // 2
        y = config.VIRTUAL_HEIGHT - panel_h - config.DIALOGUE_PANEL["OFFSET_Y"]

        # --- ДОБАВЛЕНО: Картинка стражника слева над панелью ---
        if self.guard_img and self.active_npc_obj:
            npc_type = self.active_npc_obj.properties.get('interactive_type', '').lower()
            if npc_type == 'the guard' or npc_type == 'royal_guard':
                guard_w, guard_h = self.guard_img.get_size()
                guard_x = x - guard_w + 50  # слева от панели, с небольшим отступом
                guard_y = y - guard_h // 1.65
                self.virtual_screen.blit(self.guard_img, (guard_x, guard_y))
        # --- КОНЕЦ ДОБАВЛЕНИЯ ---
        
        # Отрисовка панели
        self.virtual_screen.blit(self.dialogue_panel_img, (x, y))
        
        # Имя NPC (пока всегда 'Стражник', можно расширить)
        npc_name = "Стражник"
        name_font = pygame.font.SysFont('Arial', config.DIALOGUE_PANEL["FONT_SIZE"] + 8, bold=True)
        name_surface = name_font.render(npc_name, True, config.DIALOGUE_PANEL["FONT_COLOR"])
        name_x = x + config.DIALOGUE_PANEL["TEXT_OFFSET_X"]
        name_y = y  # небольшой отступ сверху панели
        self.virtual_screen.blit(name_surface, (name_x, name_y))
        
        # Отрисовка текста
        if self.dialogue_text_shown:
            text_surface = self.dialogue_font.render(
                self.dialogue_text_shown, 
                True, 
                config.DIALOGUE_PANEL["FONT_COLOR"]
            )
            text_x = x + config.DIALOGUE_PANEL["TEXT_OFFSET_X"]
            text_y = name_y + name_surface.get_height() + 8  # текст под именем
            self.virtual_screen.blit(text_surface, (text_x, text_y))


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
