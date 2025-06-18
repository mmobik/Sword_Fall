import pygame
from core.config import config
from core.utils import load_image
from .menu import Menu
from .button import Button
from .slider import MusicSlider


class MusicSettingsMenu(Menu):
    def __init__(self, sound_manager, back_callback):
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self._bg_key = "SETTINGS_BG"
        self._static_surface = None
        self._last_mouse_pos = None
        self._last_language = config.current_language
        
        # Создаем ползунок музыки
        slider_x = config.WIDTH // 2 - 200
        slider_y = config.HEIGHT // 2 - 50
        slider_width = 400
        self.music_slider = MusicSlider(slider_x, slider_y, slider_width, sound_manager)
        
        self._create_buttons()
        self._pre_render_static()

    def _ensure_background(self):
        """Гарантирует, что фон будет загружен или создан"""
        if self._cached_bg is None:
            try:
                self._cached_bg = load_image(config.MENU_IMAGES[self._bg_key])
            except (KeyError, pygame.error, TypeError) as e:
                if config.DEBUG_MODE:
                    print(f"Ошибка загрузки фона настроек музыки: {e}")
                # Создаём простой фон если загрузка не удалась
                self._cached_bg = pygame.Surface(config.SCREEN_SIZE)
                self._cached_bg.fill((40, 40, 60))  # Тёмно-синий фон

    def _create_buttons(self):
        """Создаем кнопки с обработчиками"""
        self.buttons = []

        # Кнопка "Назад"
        try:
            back_btn = Button(
                load_image(config.get_image("BACK_BTN", "before")),
                load_image(config.get_image("BACK_BTN", "after")),
                (config.BACK_BUTTON_X, config.BACK_BUTTON_Y),
                self.back_callback,
                self.sound_manager
            )
            self.add_button(back_btn)
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка создания кнопки BACK_BTN: {e}")

    def update_textures(self):
        """Обновление текстур при смене языка"""
        if self._last_language != config.current_language:
            self._last_language = config.current_language
            self._static_surface = None
            self._create_buttons()
        self._pre_render_static()

    def handle_event(self, event):
        """Обрабатывает события меню"""
        # Передаем события ползунку
        self.music_slider.handle_event(event)
        
        # Передаем события кнопкам
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False

    def draw(self, surface, mouse_pos=None):
        """Отрисовка меню настроек музыки"""
        # Проверяем, нужно ли обновить кэш
        if self._static_surface is None:
            self._pre_render_static()
        
        # Если мышь не двигалась и язык не менялся - рисуем кэшированную статичную версию
        if mouse_pos == self._last_mouse_pos and self._last_language == config.current_language:
            surface.blit(self._static_surface, (0, 0))
            # Рисуем ползунок поверх
            self.music_slider.draw(surface)
            # Рисуем hover-эффекты кнопок если есть
            if mouse_pos:
                for button in self.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.draw(surface, mouse_pos)
            return

        self._last_mouse_pos = mouse_pos

        # Рисуем статичную часть
        surface.blit(self._static_surface, (0, 0))
        
        # Рисуем ползунок
        self.music_slider.draw(surface)

        # Поверх рисуем все кнопки с учетом hover-эффектов
        for button in self.buttons:
            button.draw(surface, mouse_pos)

    def update(self):
        """Обновление состояния меню"""
        self.music_slider.update()

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

        # Рисуем заголовок
        self._draw_title(self._static_surface)

        # Рисуем все кнопки в их обычном состоянии
        for button in self.buttons:
            button.draw(self._static_surface, None)  # None - без hover-эффекта

    def _draw_title(self, surface):
        """Рисует заголовок меню"""
        try:
            # Создаем шрифт для заголовка
            font = pygame.font.Font(None, 48)
            title_text = config.get_text("music_settings")
            title_color = config.COLORS["WHITE"]
            
            # Рендерим текст
            title_surface = font.render(title_text, True, title_color)
            title_rect = title_surface.get_rect()
            title_rect.centerx = config.WIDTH // 2
            title_rect.y = config.HEIGHT // 4
            
            # Рисуем текст
            surface.blit(title_surface, title_rect)
            
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка отрисовки заголовка: {e}") 