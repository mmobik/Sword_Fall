import pygame
from core.config import config
from core.utils import load_image
from .menu import Menu
from .button import Button


class LanguageMenu(Menu):
    def __init__(self, sound_manager, back_callback, language_callback):
        """
        Меню выбора языка с полной оптимизацией
        :param sound_manager: менеджер звуков
        :param back_callback: функция возврата назад
        :param language_callback: функция смены языка
        """
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self.language_callback = language_callback
        self._bg_key = self._get_background_key()
        self._last_mouse_pos = None  # Для оптимизации отрисовки
        self._last_language = config.current_language  # Отслеживаем смену языка
        self._static_surface = None  # Кэш статичной части
        self._create_buttons()
        self._pre_render_static()  # Предварительный рендеринг

    def _get_background_key(self):
        """Определяем ключ фона с fallback-логикой"""
        return "LANGUAGE_BG" if "LANGUAGE_BG" in config.MENU_IMAGES else "SETTINGS_BG"

    def _create_buttons(self):
        """Создаем кнопки выбора языка"""
        self.buttons = []

        # Параметры кнопок
        button_width = 586
        button_x = (config.WIDTH - button_width) // 2
        button_spacing = 150

        # Кнопка английского языка
        english_btn = Button(
            load_image(config.get_image("ENGLISH_BTN", "before")),
            load_image(config.get_image("ENGLISH_BTN", "after")),
            (button_x, config.HEIGHT // 2 - button_spacing),
            lambda: self._change_language("english"),
            self.sound_manager
        )

        # Кнопка русского языка
        russian_btn = Button(
            load_image(config.get_image("RUSSIAN_BTN", "before")),
            load_image(config.get_image("RUSSIAN_BTN", "after")),
            (button_x, config.HEIGHT // 2),
            lambda: self._change_language("russian"),
            self.sound_manager
        )

        # Кнопка назад
        back_btn = Button(
            load_image(config.get_image("LANG_BACK_BTN", "before")),
            load_image(config.get_image("LANG_BACK_BTN", "after")),
            (config.BACK_BUTTON_X, config.BACK_BUTTON_Y),
            self.back_callback,
            self.sound_manager
        )

        self.add_button(english_btn)
        self.add_button(russian_btn)
        self.add_button(back_btn)

    def _change_language(self, lang):
        """Обработчик смены языка"""
        if config.current_language != lang:
            self.language_callback(lang)
            # Не вызываем update_textures здесь - это сделает game.py

    def update_textures(self):
        """Обновление текстур при смене языка"""
        # Проверяем, действительно ли изменился язык
        if self._last_language != config.current_language:
            self._last_language = config.current_language
            self._cached_bg = None  # Сбрасываем кэш фона
            self._static_surface = None  # Сбрасываем кэш статичной части
            self._bg_key = self._get_background_key()

            # Пересоздаем кнопки с новыми текстурами
            self._create_buttons()
            self._pre_render_static()

    def draw(self, surface, mouse_pos=None):
        """
        Оптимизированная отрисовка меню
        :param surface: поверхность для рисования
        :param mouse_pos: позиция мыши (None для статичной отрисовки)
        """
        # Проверяем, нужно ли обновить кэш
        if self._static_surface is None:
            self._pre_render_static()
        
        # Если мышь не двигалась и язык не менялся - рисуем кэшированную версию
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

    def _pre_render_static(self):
        """Создаем кэш статичной части меню"""
        self._static_surface = pygame.Surface(config.SCREEN_SIZE)

        # Загружаем и рисуем фон
        try:
            bg = load_image(config.MENU_IMAGES[self._bg_key])
            if bg is not None:
                self._static_surface.blit(bg, (0, 0))
            else:
                self._static_surface.fill((30, 30, 50))  # Фон по умолчанию
        except (KeyError, pygame.error) as e:
            print(f"Ошибка загрузки фона: {e}")
            self._static_surface.fill((30, 30, 50))  # Фон по умолчанию

        # Рисуем все кнопки в их обычном состоянии
        for button in self.buttons:
            button.draw(self._static_surface, None)  # None - без hover-эффекта