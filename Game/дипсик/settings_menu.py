import pygame
from core.config import config
from core.utils import load_image
from .menu import Menu
from .button import Button


class SettingsMenu(Menu):
    def __init__(self, sound_manager, back_callback, language_callback):
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self.language_callback = language_callback
        self._bg_key = "SETTINGS_BG"
        self._static_surface = None  # Кэш статичной части
        self._last_mouse_pos = None
        self._last_language = config.current_language  # Отслеживаем смену языка
        self._create_buttons()
        self._pre_render_static()  # Предварительный рендеринг

    def _ensure_background(self):
        """Гарантирует, что фон будет загружен или создан"""
        if self._cached_bg is None:
            try:
                self._cached_bg = load_image(config.MENU_IMAGES[self._bg_key])
            except (KeyError, pygame.error, TypeError) as e:
                print(f"Ошибка загрузки фона настроек: {e}")
                # Создаём простой фон если загрузка не удалась
                self._cached_bg = pygame.Surface(config.SCREEN_SIZE)
                self._cached_bg.fill((40, 40, 60))  # Тёмно-синий фон

    def _create_buttons(self):
        """Создаем кнопки с обработчиками"""
        self.buttons = []

        buttons_data = [
            ("GAME_SETTINGS_BTN", config.SETTINGS_BUTTON_Y_START, self.settings_game_menu),
            ("GRAPHICS_SETTINGS_BTN", config.SETTINGS_BUTTON_Y_START + config.BUTTON_SPACING,
             self.settings_graphics_menu),
            ("LANGUAGE_SETTINGS_BTN", config.SETTINGS_BUTTON_Y_START + 2 * config.BUTTON_SPACING,
             self.open_language_menu),
            ("BACK_BTN", config.BACK_BUTTON_Y, self.back_callback)
        ]

        for btn_key, y_pos, action in buttons_data:
            try:
                btn = Button(
                    load_image(config.get_image(btn_key, "before")),
                    load_image(config.get_image(btn_key, "after")),
                    (config.SETTINGS_BUTTON_X, y_pos),
                    action,
                    self.sound_manager
                )
                self.add_button(btn)
            except Exception as e:
                print(f"Ошибка создания кнопки {btn_key}: {e}")

    def update_textures(self):
        """Обновление текстур при смене языка"""
        # Проверяем, действительно ли изменился язык
        if self._last_language != config.current_language:
            self._last_language = config.current_language
            self._static_surface = None  # Сбрасываем кэш только при реальной смене языка
            self._create_buttons()  # Пересоздаем кнопки с новыми изображениями
        self._pre_render_static()

    def draw(self, surface, mouse_pos=None):
        """Оптимизированная отрисовка без мерцания"""
        # Проверяем, нужно ли обновить кэш
        if self._static_surface is None:
            self._pre_render_static()
        
        # Если мышь не двигалась и язык не менялся - рисуем кэшированную статичную версию
        if mouse_pos == self._last_mouse_pos and self._last_language == config.current_language:
            surface.blit(self._static_surface, (0, 0))
            # Но все равно рисуем hover-эффекты если есть
            if mouse_pos:
                for button in self.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.draw(surface, mouse_pos)
            return

        self._last_mouse_pos = mouse_pos

        # Рисуем статичную часть
        surface.blit(self._static_surface, (0, 0))

        # Поверх рисуем все кнопки с учетом hover-эффектов
        for button in self.buttons:
                button.draw(surface, mouse_pos)

    def settings_game_menu(self):
        """Обработчик кнопки настроек игры"""
        print("Открыты настройки игры")
        # Здесь будет логика меню настроек игры
        # Например: self.game_state_manager.change_state("game_settings")

    def settings_graphics_menu(self):
        """Обработчик графических настроек"""
        print("Открыты графические настройки")
        # Здесь будет логика графических настроек
        # Например: self.game_state_manager.change_state("graphics_settings")

    def open_language_menu(self):
        """Обработчик кнопки языковых настроек"""
        print("Открытие меню языка")
        self.language_callback()  # Переходим в языковое меню

    def update(self):
        """Обновление состояния меню (если нужно)"""
        pass

    def _pre_render_static(self):
        """Создаем кэш статичной части меню"""
        self._static_surface = pygame.Surface(config.SCREEN_SIZE)

        # Загружаем и рисуем фон
        try:
            bg = load_image(config.MENU_IMAGES[self._bg_key])
            if bg is not None:
                self._static_surface.blit(bg, (0, 0))
            else:
                self._static_surface.fill((40, 40, 60))  # Фон по умолчанию
        except:
            self._static_surface.fill((40, 40, 60))  # Фон по умолчанию

        # Рисуем все кнопки в их обычном состоянии
        for button in self.buttons:
            button.draw(self._static_surface, None)  # None - без hover-эффекта
