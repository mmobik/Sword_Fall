import pygame
from Game.core.config import config
from Game.core.utils import load_image
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
        self._create_buttons()
        self._last_mouse_pos = None  # Для оптимизации отрисовки

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
            self.update_textures()

    def update_textures(self):
        """Обновление текстур при смене языка"""
        self._cached_bg = None  # Сбрасываем кэш фона
        self._bg_key = self._get_background_key()

        # Пересоздаем кнопки с новыми текстурами
        self._create_buttons()

    def draw(self, surface, mouse_pos=None):
        """
        Оптимизированная отрисовка меню
        :param surface: поверхность для рисования
        :param mouse_pos: позиция мыши (None для статичной отрисовки)
        """
        # Загружаем фон если нужно
        if self._cached_bg is None:
            try:
                self._cached_bg = load_image(config.MENU_IMAGES[self._bg_key])
            except (KeyError, pygame.error) as e:
                print(f"Ошибка загрузки фона: {e}")
                self._cached_bg = pygame.Surface(config.SCREEN_SIZE)
                self._cached_bg.fill((30, 30, 50))  # Фон по умолчанию

        # Отрисовываем фон
        surface.blit(self._cached_bg, (0, 0))

        # Оптимизация: рисуем только hover-кнопки если мышь двигалась
        if mouse_pos != self._last_mouse_pos:
            self._last_mouse_pos = mouse_pos
            for button in self.buttons:
                if mouse_pos and button.rect.collidepoint(mouse_pos):
                    button.draw(surface, mouse_pos)
        else:
            # Статичная отрисовка всех кнопок если мышь не двигалась
            for button in self.buttons:
                button.draw(surface, mouse_pos)