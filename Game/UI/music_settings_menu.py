import os
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

        # Кастомные хитбоксы для сегментов слайдера (шаблон для всех трёх полосок)
        # Для каждого трека: 11 сегментов (0, 10, ..., 100)
        self.slider_hitboxes = {
            "dark_fantasm": [  # Главное меню
                (566, 335, 60, 95),  # 0%
                (625, 335, 81, 95),  # 10%
                (705, 335, 92, 95),  # 20%
                (795, 335, 95, 95),  # 30%
                (890, 335, 95, 95),  # 40%
                (985, 335, 97, 95),  # 50%
                (1080, 335, 95, 95),  # 60%
                (1170, 335, 95, 95),  # 70%
                (1265, 335, 95, 95),  # 80%
                (1360, 335, 90, 95),  # 90%
                (1447, 335, 105, 95),  # 100%
            ],
            "house": [  # Игра
                (566, 450, 60, 95),  # 0%
                (625, 450, 81, 95),  # 10%
                (705, 450, 92, 95),  # 20%
                (795, 450, 95, 95),  # 30%
                (890, 450, 95, 95),  # 60%
                (985, 450, 97, 95),  # 50%
                (1080, 450, 95, 95),  # 9%
                (1170, 450, 95, 95),  # 70%
                (1265, 450, 95, 95),  # 80%
                (1360, 450, 90, 95),  # 90%
                (1447, 450, 105, 95),  # 100%
            ],
            "button": [  # Кнопки
                (566, 565, 60, 95),  # 0%
                (625, 565, 81, 95),  # 10%
                (705, 565, 92, 95),  # 20%
                (795, 565, 95, 95),  # 30%
                (890, 565, 95, 95),  # 60%
                (985, 565, 97, 95),  # 50%
                (1080, 565, 95, 95),  # 95%
                (1170, 565, 95, 95),  # 70%
                (1265, 565, 95, 95),  # 80%
                (1360, 565, 90, 95),  # 90%
                (1447, 565, 105, 95),  # 100%
            ],
        }

        # Анимация музыки
        self.music_animation_images = {}
        self._load_music_animation()

        self._load_images_and_tracks()
        self._create_buttons()
        self._pre_render_static()

    def _load_music_animation(self):
        """Загружает изображения для анимации музыки (теперь просто для совместимости)"""
        volume_levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for level in volume_levels:
            try:
                image_path = f"Game/assets/images/menu/settings/music_change/{level}.jpg"
                self.music_animation_images[level] = load_image(image_path)
            except (KeyError, pygame.error, TypeError, FileNotFoundError) as e:
                if config.DEBUG_MODE:
                    print(f"Не удалось загрузить изображение анимации музыки для уровня {level}: {e}")
                self.music_animation_images[level] = pygame.Surface((200, 100))
                self.music_animation_images[level].fill((100, 100, 100))

    def get_current_music_image(self):
        """Возвращает изображение для текущего уровня громкости (без анимации)"""
        volume_percent = int(self.sound_manager.music_volume * 100)
        available_levels = sorted(self.music_animation_images.keys())
        closest_level = min(available_levels, key=lambda x: abs(x - volume_percent))
        return self.music_animation_images[closest_level]

    def _load_images_and_tracks(self):
        self.track_images = []
        self.slider_images = {}
        folder = "Game/assets/images/menu/settings/music_change"
        lang = "rus" if config.current_language == "russian" else "eng"
        # Связь: название для UI -> имя файла
        self.track_file_map = {
            "main_menu": "dark_fantasm",
            "game": "house",
            "button": "button"
        }
        # Загружаем картинки для ползунка (0, 10, ..., 100, default)
        for level in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            self.slider_images[level] = load_image(os.path.join(folder, f"{level}.jpg"))
        self.slider_images['default'] = load_image(os.path.join(folder, "default.jpg"))
        # Новое размещение: относительно кнопки Music
        music_img = load_image(
            config.get_image("MUSIC_SETTINGS_BTN", "before")) if config.current_language == "english" else load_image(
            config.get_image("MUSIC_SETTINGS_BTN_RUS", "before"))
        music_rect = music_img.get_rect() if music_img else pygame.Rect(0, 0, 0, 0)
        music_rect.centerx = config.WIDTH // 2
        music_rect.y = 100
        offset_x = -630
        offset_y = 150
        spacing = 30
        start_x = music_rect.left + offset_x
        start_y = music_rect.bottom + offset_y
        # Добавляем кнопки для main_menu, game, button
        added = 0
        for ui_name, file_name in self.track_file_map.items():
            if ui_name == "button":
                btn_img_path = os.path.join(folder, f"buttons_{lang}.jpg")
            else:
                btn_img_path = os.path.join(folder, f"{ui_name}_{lang}.jpg")
            if os.path.exists(btn_img_path):
                img = load_image(btn_img_path)
                if img:
                    img_rect = img.get_rect()
                    img_rect.x = start_x
                    img_rect.y = start_y + added * (img_rect.height + spacing)
                    self.track_images.append((file_name, img, img_rect))
                    added += 1
        self.default_img = self.slider_images['default']
        self.music_btn_img = music_img
        self.music_btn_img_rus = load_image(config.get_image("MUSIC_SETTINGS_BTN_RUS", "before"))

    def _create_buttons(self):
        self.buttons = []
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
        if self._last_language != config.current_language:
            self._last_language = config.current_language
            self._static_surface = None
            self._load_images_and_tracks()
            self._create_buttons()
        self._pre_render_static()

    def draw(self, surface, mouse_pos=None):
        if self._static_surface is None:
            self._pre_render_static()
        surface.blit(self._static_surface, (0, 0))
        self._draw_title(surface)
        # Рисуем все треки и их ползунки
        for idx, (track_type, img, rect) in enumerate(self.track_images):
            surface.blit(img, rect)
            self._draw_slider(surface, track_type, rect)
        for button in self.buttons:
            button.draw(surface, mouse_pos)

    def _draw_title(self, surface):
        img = self.music_btn_img if config.current_language == "english" else self.music_btn_img_rus
        if img:
            rect = img.get_rect()
            rect.centerx = config.WIDTH // 2
            rect.y = 150
            surface.blit(img, rect)

    def _draw_slider(self, surface, track_type, track_rect):
        slider_x = track_rect.right + 40
        slider_y = track_rect.y
        if track_type == "button":
            value = self.sound_manager.sound_volume
        else:
            value = self.sound_manager.get_track_volume(track_type)
        volume_percent = int(value * 100)
        img_sample = self.slider_images[0] or self.slider_images['default']
        slider_w, slider_h = img_sample.get_width(), img_sample.get_height()
        img = self.slider_images.get(self._nearest_level(volume_percent), self.slider_images['default'])
        if img:
            img_rect = img.get_rect()
            img_rect.x = slider_x
            img_rect.y = slider_y
            surface.blit(img, img_rect)
        if config.DEBUG_MODE:
            font = pygame.font.Font(None, 24)
            levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            hitboxes = self.slider_hitboxes.get(track_type, None)
            for idx, level in enumerate(levels):
                if hitboxes and idx < len(hitboxes) and hitboxes[idx]:
                    seg_rect = pygame.Rect(*hitboxes[idx])
                else:
                    seg_w = slider_w // 11
                    seg_rect = pygame.Rect(slider_x + idx * seg_w, slider_y, seg_w, slider_h)
                pygame.draw.rect(surface, (0, 255, 0, 80), seg_rect, 2)
                text = font.render(str(level), True, (0, 255, 0))
                text_rect = text.get_rect(center=seg_rect.center)
                surface.blit(text, text_rect)

    @staticmethod
    def _nearest_level(percent):
        return min([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], key=lambda x: abs(x - percent))

    def handle_event(self, event, mouse_pos=None):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, (track_type, img, rect) in enumerate(self.track_images):
                slider_x = rect.right + 40
                slider_y = rect.y
                img_sample = self.slider_images[0] or self.slider_images['default']
                slider_w, slider_h = img_sample.get_width(), img_sample.get_height()
                levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                hitboxes = self.slider_hitboxes.get(track_type, None)
                for i, level in enumerate(levels):
                    if hitboxes and i < len(hitboxes) and hitboxes[i]:
                        seg_rect = pygame.Rect(*hitboxes[i])
                    else:
                        seg_w = slider_w // 11
                        seg_rect = pygame.Rect(slider_x + i * seg_w, slider_y, seg_w, slider_h)
                    if seg_rect.collidepoint(event.pos):
                        if track_type == "button":
                            self.sound_manager.set_sound_volume(level / 100.0)
                        else:
                            self.sound_manager.set_track_volume(track_type, level / 100.0)
                        self.sound_manager.play_sound("button_click")
                        break
        for button in self.buttons:
            button.handle_event(event, mouse_pos)

    def update(self, dt=1 / 60):
        pass

    def _pre_render_static(self):
        self._static_surface = pygame.Surface(config.SCREEN_SIZE)
        try:
            bg = load_image(config.MENU_IMAGES[self._bg_key])
            if bg is not None:
                self._static_surface.blit(bg, (0, 0))
            else:
                self._static_surface.fill((40, 40, 60))
        except (KeyError, pygame.error, TypeError) as e:
            if config.DEBUG_MODE:
                print(f"Ошибка загрузки фона настроек музыки: {e}")
            self._static_surface.fill((40, 40, 60))
        self._draw_title(self._static_surface)
        for button in self.buttons:
            button.draw(self._static_surface, None)
