from .menu import Menu
from .button import Button
from Game.core import config, load_image


class LanguageMenu(Menu):
    def __init__(self, sound_manager, back_callback, language_callback):
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self.language_callback = language_callback

        # Центрирование кнопок по горизонтали
        button_width = 586
        button_x = (config.WIDTH - button_width) // 2

        # Кнопка английского языка
        self.add_button(Button(
            load_image(config.get_image_path("ENGLISH_BTN", "before")),
            load_image(config.get_image_path("ENGLISH_BTN", "after")),
            (button_x, config.HEIGHT // 2 - 100),
            lambda: self.select_language("english")
        ))

        # Кнопка русского языка
        self.add_button(Button(
            load_image(config.get_image_path("RUSSIAN_BTN", "before")),
            load_image(config.get_image_path("RUSSIAN_BTN", "after")),
            (button_x, config.HEIGHT // 2 + 50),
            lambda: self.select_language("russian")
        ))

        # Кнопка "Назад"
        self.add_button(Button(
            load_image(config.get_image_path("LANG_BACK_BTN", "before")),
            load_image(config.get_image_path("LANG_BACK_BTN", "after")),
            (config.BACK_BUTTON_X, config.BACK_BUTTON_Y),
            self.back_callback
        ))

    def select_language(self, lang):
        """Выбор языка и возврат в меню настроек"""
        print(f"Selected language: {lang}")
        self.language_callback(lang)  # Сохраняем выбор языка
        self.back_callback()  # Возвращаемся в меню настроек

    def draw(self, surface, mouse_pos):
        """Отрисовка меню языка"""
        surface.blit(load_image(config.MENU_IMAGES["LANGUAGE_BG"]), (0, 0))
        super().draw(surface, mouse_pos)
