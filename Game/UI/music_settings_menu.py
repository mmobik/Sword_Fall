import pygame
from core.config import config
from core.utils import load_image
from .menu import Menu
from .button import Button


class MusicSettingsMenu(Menu):
    def __init__(self, sound_manager, back_callback):
        super().__init__(sound_manager)
        self.back_callback = back_callback
        self._bg_key = "SETTINGS_BG"
        self._static_surface = None
        self._last_mouse_pos = None
        self._last_language = config.current_language
        
        # Анимация музыки
        self.music_animation_images = {}
        self.music_animation_timer = 0
        self.music_animation_speed = 0.1  # Секунды между кадрами
        self._load_music_animation()
        
        self._load_images()
        self._create_buttons()
        self._pre_render_static()

    def _load_music_animation(self):
        """Загружает изображения для анимации музыки"""
        volume_levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        
        for level in volume_levels:
            try:
                image_path = f"assets/images/menu/settings/music_change/{level}.jpg"
                self.music_animation_images[level] = load_image(image_path)
            except:
                if config.DEBUG_MODE:
                    print(f"Не удалось загрузить изображение анимации музыки для уровня {level}")
                # Создаем пустое изображение
                self.music_animation_images[level] = pygame.Surface((200, 100))
                self.music_animation_images[level].fill((100, 100, 100))

    def get_current_music_image(self):
        """Возвращает текущее изображение анимации музыки на основе громкости"""
        # Преобразуем значение громкости (0.0-1.0) в процент (0-100)
        volume_percent = int(self.sound_manager.music_volume * 100)
        
        # Находим ближайший уровень из доступных изображений
        available_levels = sorted(self.music_animation_images.keys())
        closest_level = min(available_levels, key=lambda x: abs(x - volume_percent))
        
        return self.music_animation_images[closest_level]

    def _load_images(self):
        self.music_images = {}
        self.default_img = load_image("assets/images/menu/settings/music_change/default.jpg")
        for level in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            path = f"assets/images/menu/settings/music_change/{level}.jpg"
            self.music_images[level] = load_image(path)
        # Кнопка music (before, локализованная)
        self.music_btn_img = load_image(config.get_image("MUSIC_SETTINGS_BTN", "before"))
        self.music_btn_img_rus = load_image(config.get_image("MUSIC_SETTINGS_BTN_RUS", "before"))

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
            self._load_images()
            self._create_buttons()
        self._pre_render_static()

    def draw(self, surface, mouse_pos=None):
        """Отрисовка меню настроек музыки"""
        # Проверяем, нужно ли обновить кэш
        if self._static_surface is None:
            self._pre_render_static()
        
        # Если мышь не двигалась и язык не менялся - рисуем кэшированную статичную версию
        if mouse_pos == self._last_mouse_pos and self._last_language == config.current_language:
            surface.blit(self._static_surface, (0, 0))
            # Рисуем анимацию музыки поверх
            self._draw_music_animation(surface, mouse_pos)
            # Рисуем hover-эффекты кнопок если есть
            if mouse_pos:
                for button in self.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.draw(surface, mouse_pos)
            return

        self._last_mouse_pos = mouse_pos

        # Рисуем статичную часть
        surface.blit(self._static_surface, (0, 0))
        
        # Рисуем анимацию музыки
        self._draw_music_animation(surface, mouse_pos)

        # Поверх рисуем все кнопки с учетом hover-эффектов
        for button in self.buttons:
            button.draw(surface, mouse_pos)

    def _draw_title(self, surface):
        # Только картинка-кнопка, без текста!
        img = self.music_btn_img if config.current_language == "english" else self.music_btn_img_rus
        if img:
            rect = img.get_rect()
            rect.centerx = config.WIDTH // 2
            rect.y = config.HEIGHT // 4
            surface.blit(img, rect)

    def _draw_music_animation(self, surface, mouse_pos):
        img = self.default_img
        hovered_level = None
        if mouse_pos and self.default_img:
            img_rect = self.default_img.get_rect()
            img_rect.centerx = config.WIDTH // 2
            img_rect.centery = config.HEIGHT // 2
            seg_w = img_rect.width // 11
            for idx, level in enumerate([0,10,20,30,40,50,60,70,80,90,100]):
                seg_rect = pygame.Rect(img_rect.x + idx*seg_w, img_rect.y, seg_w, img_rect.height)
                if seg_rect.collidepoint(mouse_pos):
                    hovered_level = level
                    break
        if hovered_level is not None and self.music_images[hovered_level]:
            img = self.music_images[hovered_level]
        if img:
            img_rect = img.get_rect()
            img_rect.centerx = config.WIDTH // 2
            img_rect.centery = config.HEIGHT // 2
            surface.blit(img, img_rect)

    def update(self, dt=1/60):
        pass

    def _pre_render_static(self):
        self._static_surface = pygame.Surface(config.SCREEN_SIZE)
        try:
            bg = load_image(config.MENU_IMAGES[self._bg_key])
            if bg is not None:
                self._static_surface.blit(bg, (0, 0))
            else:
                self._static_surface.fill((40, 40, 60))
        except:
            self._static_surface.fill((40, 40, 60))
        self._draw_title(self._static_surface)
        for button in self.buttons:
            button.draw(self._static_surface, None)

    def handle_event(self, event, mouse_pos=None):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверяем клик по сегменту
            img = self.default_img
            if img:
                img_rect = img.get_rect()
                img_rect.centerx = config.WIDTH // 2
                img_rect.centery = config.HEIGHT // 2
                seg_w = img_rect.width // 11
                for idx, level in enumerate([0,10,20,30,40,50,60,70,80,90,100]):
                    seg_rect = pygame.Rect(img_rect.x + idx*seg_w, img_rect.y, seg_w, img_rect.height)
                    if seg_rect.collidepoint(event.pos):
                        self.sound_manager.set_music_volume(level / 100.0)
                        break
        # Передаём событие кнопке Back
        for button in self.buttons:
            button.handle_event(event, mouse_pos) 