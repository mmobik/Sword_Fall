"""
Модуль игрового цикла.

Содержит класс GameLoop для управления основным игровым циклом,
обработки событий, обновления состояния и рендеринга.
"""

import time
import pygame
from core.config import config


class GameLoop:
    """
    Класс для управления основным игровым циклом.
    
    Обеспечивает обработку событий, обновление игрового состояния,
    рендеринг кадров и управление производительностью.
    """

    def __init__(self, game):
        """
        Инициализация игрового цикла.
        
        Args:
            game: Ссылка на основной объект игры.
        """
        self.game = game

    def run(self):
        """Запускает основной игровой цикл."""
        running = True
        while running:
            self.game.dt = self.game.clock.tick(self.game.target_fps) / 1000.0
            current_time = time.time()

            if current_time - self.game.last_log_time >= 2.0:
                self._log_performance()
                self.game.last_log_time = current_time

            running = self._handle_events()
            self._update_game_state()
            self._render_frame()

    def _handle_events(self) -> bool:
        """
        Обрабатывает события игры.
        
        Returns:
            True, если игра должна продолжиться, False для выхода.
        """
        self.game.update_talk_button_state()

        if self.game.waiting_for_first_update:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Сохраняем настройки звука при выходе
                    self.game.sound_manager.save_settings()
                    return False
            return True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Сохраняем настройки звука при выходе
                self.game.sound_manager.save_settings()
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    old_debug = config.DEBUG_MODE
                    config.set_debug_mode(not config.DEBUG_MODE)
                    print(f"[DEBUG] Режим отладки {'включен' if config.DEBUG_MODE else 'выключен'} (был: {old_debug})")

                if (event.key == pygame.K_ESCAPE and
                        self.game.game_state_manager.game_state == "new_game"):
                    steps_channel = getattr(self.game.player, '_steps_channel', None)
                    if steps_channel:
                        steps_channel.stop()
                        setattr(self.game.player, '_steps_channel', None)
                    if self.game.player:
                        self.game.player.is_walking = False
                    self.game.show_main_menu()

                if (event.key == pygame.K_e and
                        self.game.game_state_manager.game_state == "new_game"):
                    self.game.dialogue_handler.try_interact_with_npc()
                
                # Воскрешение игрока
                if (event.key == pygame.K_r and
                        self.game.game_state_manager.game_state == "new_game" and
                        self.game.player and not self.game.player.is_alive()):
                    self.game.player.revive()
                
                # Тестовые клавиши для демонстрации системы характеристик (только в режиме отладки)
                if config.DEBUG_MODE and self.game.game_state_manager.game_state == "new_game" and self.game.player:
                    print(f"[DEBUG] Проверка тестовых клавиш: DEBUG_MODE={config.DEBUG_MODE}, state={self.game.game_state_manager.game_state}, player={self.game.player is not None}")
                    if event.key == pygame.K_h:
                        damage = self.game.player.take_damage(10.0)
                        print(f"[DEBUG] Игрок получил урон: {damage} HP")
                    elif event.key == pygame.K_j:
                        heal = self.game.player.heal(20.0)
                        print(f"[DEBUG] Игрок восстановился: {heal} HP")
                    elif event.key == pygame.K_k:
                        if self.game.player.stats.use_stamina(30.0):
                            print("[DEBUG] Использовано 30 SP")
                        else:
                            print("[DEBUG] Недостаточно выносливости!")
                    elif event.key == pygame.K_l:
                        levels = self.game.player.add_experience(50.0)
                        print(f"[DEBUG] Получено 50 XP, уровней: {levels}")
                elif event.key in [pygame.K_h, pygame.K_j, pygame.K_k, pygame.K_l]:
                    print(f"[DEBUG] Тестовая клавиша нажата, но условия не выполнены:")
                    print(f"  DEBUG_MODE: {config.DEBUG_MODE}")
                    print(f"  game_state: {self.game.game_state_manager.game_state}")
                    print(f"  player exists: {self.game.player is not None}")
                
                # Альтернативные тестовые клавиши (работают всегда, если игрок существует)
                if (self.game.game_state_manager.game_state == "new_game" and 
                    self.game.player and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]):
                    if event.key == pygame.K_1:  # Цифра 1
                        damage = self.game.player.take_damage(10.0, source="test")
                        if config.DEBUG_MODE:
                            print(f"[TEST] Игрок получил урон: {damage} HP")
                    elif event.key == pygame.K_2:  # Цифра 2
                        heal = self.game.player.heal(20.0, source="test")
                        if config.DEBUG_MODE:
                            print(f"[TEST] Игрок восстановился: {heal} HP")
                    elif event.key == pygame.K_3:  # Цифра 3
                        if self.game.player.stats.use_stamina(30.0):
                            if config.DEBUG_MODE:
                                print("[TEST] Использовано 30 SP")
                        else:
                            if config.DEBUG_MODE:
                                print("[TEST] Недостаточно выносливости!")
                    elif event.key == pygame.K_4:  # Цифра 4
                        levels = self.game.player.add_experience(50.0)
                        if config.DEBUG_MODE:
                            print(f"[TEST] Получено 50 XP, уровней: {levels}")
                    elif event.key == pygame.K_5:  # Цифра 5
                        if not self.game.player.is_alive():
                            self.game.player.revive()
                            if config.DEBUG_MODE:
                                print("[TEST] Игрок воскрешен!")
                        else:
                            if config.DEBUG_MODE:
                                print("[TEST] Игрок уже жив!")

            if self.game.game_state_manager.current_menu:
                mouse_pos = pygame.mouse.get_pos()
                self.game.game_state_manager.current_menu.handle_event(event, mouse_pos)
            
            # Обрабатываем события UI (инвентарь)
            if (self.game.game_state_manager.game_state == "new_game" and 
                self.game.player_ui):
                self.game.player_ui.handle_event(event)

        return True

    def _update_game_state(self):
        """Обновляет игровое состояние."""
        if self.game.game_state_manager.current_menu:
            self.game.game_state_manager.current_menu.update(self.game.dt)

        if self.game.game_state_manager.game_state == "new_game":
            if not all([self.game.player, self.game.camera, self.game.level]):
                self.game.game_resources.load_game_resources()
                self.game.waiting_for_first_update = True

            if (all([self.game.player, self.game.camera, self.game.level,
                     self.game.all_sprites]) and not self.game.waiting_for_first_update):
                if not self.game.wait_for_key_release:
                    self.game.all_sprites.update(
                        self.game.dt,
                        self.game.level.width * self.game.level.tilewidth,
                        self.game.level.height * self.game.level.tileheight,
                        self.game.collision_objects
                    )
                    self.game.camera.update(self.game.player)
                else:
                    keys = pygame.key.get_pressed()
                    move_keys = [
                        pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
                    ]
                    if not any(keys[k] for k in move_keys):
                        self.game.wait_for_key_release = False

            if (self.game.waiting_for_first_update and
                    all([self.game.player, self.game.camera, self.game.level,
                         self.game.all_sprites])):
                self.game.waiting_for_first_update = False
                self.game.wait_for_key_release = True

    def _render_frame(self):
        """Отрисовывает текущий кадр."""
        if self.game.game_state_manager.current_menu:
            self.game.screen.fill((0, 0, 0))
            mouse_pos = pygame.mouse.get_pos()
            self.game.game_state_manager.current_menu.draw(self.game.screen, mouse_pos)
            pygame.display.flip()

        elif self.game.game_state_manager.game_state == "new_game":
            self.game.virtual_screen.fill((0, 0, 0))
            self.game.render_game()
            self.game.update_talk_button_alpha()

            # Отрисовка кнопки разговора
            if (self.game.talk_button_img and self.game.talk_button_alpha > 0 and
                    not self.game.show_dialogue):
                btn_w, btn_h = self.game.talk_button_img.get_size()

                if self.game.player and self.game.camera:
                    player_screen_x = (self.game.player.hitbox.centerx -
                                       self.game.camera.offset.x)
                    player_screen_y = (self.game.player.hitbox.centery -
                                       self.game.camera.offset.y)
                    x = player_screen_x - btn_w // 2
                    y = player_screen_y - btn_h + config.DIALOGUE_BUTTON["OFFSET_Y"]
                else:
                    x = (config.VIRTUAL_WIDTH - btn_w) // 2
                    y = config.VIRTUAL_HEIGHT - btn_h - config.DIALOGUE_BUTTON["FALLBACK_Y"]

                btn_img = self.game.talk_button_img.copy()
                btn_img.set_alpha(int(self.game.talk_button_alpha))
                self.game.virtual_screen.blit(btn_img, (x, y))
                self.game.talk_button_rect = pygame.Rect(x, y, btn_w, btn_h)

            # Отрисовка диалогов
            if self.game.show_dialogue and self.game.dialogue_panel_img:
                self.game.update_typewriter_text()
                self.game.dialogue_panel.render()

                if self.game.active_npc_obj:
                    npc_type = self.game.active_npc_obj.properties.get(
                        'interactive_type', '').lower()
                    if npc_type != 'king':
                        if (time.time() - self.game.dialogue_start_time >
                                config.DIALOGUE_PANEL["SHOW_DURATION"]):
                            self.game.show_dialogue = False
                            self.game.dialogue_text = ""
                            self.game.dialogue_text_shown = ""
                            self.game.active_npc_obj = None

            scaled_screen = pygame.transform.scale(
                self.game.virtual_screen, (config.WIDTH, config.HEIGHT))
            self.game.screen.blit(scaled_screen, (0, 0))
            pygame.display.flip()

    def _log_performance(self):
        """Логирует информацию о производительности."""
        current_fps = self.game.clock.get_fps()
        self.game.fps_history.append(current_fps)

        if config.DEBUG_MODE:
            print(f"[PERF] FPS: {current_fps:.1f} | "
                  f"State: {self.game.game_state_manager.game_state}")
