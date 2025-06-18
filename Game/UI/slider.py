import pygame
from core.config import config
from core.utils import load_image


class MusicSlider:
    def __init__(self, x, y, width, sound_manager):
        self.x = x
        self.y = y
        self.width = width
        self.height = 30
        self.sound_manager = sound_manager
        
        # Загружаем изображения ползунка
        self.slider_images = {}
        self._load_slider_images()
        
        # Параметры ползунка
        self.value = self.sound_manager.music_volume
        self.is_dragging = False
        self.rect = pygame.Rect(x, y, width, self.height)
        
        # Вычисляем позицию ползунка
        self.slider_pos = x + int(self.value * width)
        
    def _load_slider_images(self):
        """Загружает изображения ползунка для разных уровней громкости"""
        volume_levels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        
        for level in volume_levels:
            try:
                image_path = f"assets/images/menu/settings/music_change/{level}.jpg"
                self.slider_images[level] = load_image(image_path)
            except:
                if config.DEBUG_MODE:
                    print(f"Не удалось загрузить изображение ползунка для уровня {level}")
                # Создаем пустое изображение
                self.slider_images[level] = pygame.Surface((50, 30))
                self.slider_images[level].fill((100, 100, 100))
    
    def get_current_slider_image(self):
        """Возвращает изображение ползунка для текущего уровня громкости"""
        # Преобразуем значение громкости (0.0-1.0) в процент (0-100)
        volume_percent = int(self.value * 100)
        
        # Находим ближайший уровень из доступных изображений
        available_levels = sorted(self.slider_images.keys())
        closest_level = min(available_levels, key=lambda x: abs(x - volume_percent))
        
        return self.slider_images[closest_level]
    
    def handle_event(self, event):
        """Обрабатывает события мыши для ползунка"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Левая кнопка мыши
                if self.rect.collidepoint(event.pos):
                    self.is_dragging = True
                    self._update_value_from_pos(event.pos[0])
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_value_from_pos(event.pos[0])
    
    def _update_value_from_pos(self, x):
        """Обновляет значение ползунка на основе позиции мыши"""
        # Ограничиваем позицию в пределах ползунка
        x = max(self.x, min(self.x + self.width, x))
        
        # Вычисляем новое значение (0.0-1.0)
        self.value = (x - self.x) / self.width
        
        # Обновляем позицию ползунка
        self.slider_pos = x
        
        # Применяем новую громкость
        self.sound_manager.set_music_volume(self.value)
    
    def draw(self, surface):
        """Отрисовывает ползунок"""
        # Рисуем фон ползунка (простая линия)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)
        
        # Получаем изображение для текущего уровня громкости
        slider_image = self.get_current_slider_image()
        
        if slider_image:
            # Вычисляем позицию для отрисовки изображения
            image_rect = slider_image.get_rect()
            image_rect.centerx = self.slider_pos
            image_rect.centery = self.y + self.height // 2
            
            # Отрисовываем изображение
            surface.blit(slider_image, image_rect)
        
        # Рисуем индикатор текущей позиции
        pygame.draw.circle(surface, (255, 255, 255), (self.slider_pos, self.y + self.height // 2), 5)
    
    def update(self):
        """Обновляет состояние ползунка"""
        # Синхронизируем значение с sound_manager
        if abs(self.value - self.sound_manager.music_volume) > 0.01:
            self.value = self.sound_manager.music_volume
            self.slider_pos = self.x + int(self.value * self.width) 