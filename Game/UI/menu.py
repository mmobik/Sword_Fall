import pygame
from core.config import config
from core.utils import load_image


class Menu:
    def __init__(self, sound_manager):
        self.buttons = []
        self.sound_manager = sound_manager
        self._cached_bg = None
        self._bg_key = None
        self._last_mouse_pos = None
        self._last_language = config.current_language

    def _ensure_background(self):
        """Гарантирует наличие фона (должен переопределяться в дочерних классах)"""
        if self._cached_bg is None and self._bg_key:
            try:
                self._cached_bg = load_image(config.MENU_IMAGES[self._bg_key])
            except:
                self._cached_bg = pygame.Surface(config.SCREEN_SIZE)
                self._cached_bg.fill((0, 0, 0))

    def add_button(self, button):
        self.buttons.append(button)

    def draw(self, surface, mouse_pos=None):
        """Безопасная отрисовка с гарантией наличия фона"""
        self._ensure_background()

        # Проверяем, изменился ли язык
        if self._last_language != config.current_language:
            self._last_language = config.current_language
            self._cached_bg = None
        self._ensure_background()

        if self._cached_bg:
            surface.blit(self._cached_bg, (0, 0))
        else:
            surface.fill((0, 0, 0))  # Чёрный фон если нет изображения

        # Оптимизация: рисуем кнопки только если мышь двигалась или изменился язык
        if mouse_pos != self._last_mouse_pos or self._last_language != config.current_language:
            self._last_mouse_pos = mouse_pos
        for button in self.buttons:
            button.draw(surface, mouse_pos)

    def handle_event(self, event, mouse_pos):
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            for button in self.buttons:
                button.handle_event(event, mouse_pos)

    def update_textures(self):
        """Обновление текстур (должен переопределяться)"""
        self._cached_bg = None
        self._last_language = config.current_language
        self._ensure_background()