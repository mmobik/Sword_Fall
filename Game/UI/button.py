import pygame


class Button:
    def __init__(self, normal_image, hover_image, position, action=None, sound_manager=None):
        self.normal_image = normal_image
        self.hover_image = hover_image
        self.position = position
        self.rect = pygame.Rect(position[0], position[1],
                                normal_image.get_width(),
                                normal_image.get_height())
        self.action = action
        self.sound_manager = sound_manager
        self.is_hovered = False
        self.is_clicked = False
        self._last_hover_state = False  # Для отслеживания изменений hover-состояния

    def draw(self, surface, mouse_pos=None):
        """Отрисовка кнопки с оптимизацией"""
        current_hover = mouse_pos and self.rect.collidepoint(mouse_pos)
        
        # Всегда рисуем кнопку, но с правильным состоянием
        if current_hover:
            surface.blit(self.hover_image, self.position)
        else:
            surface.blit(self.normal_image, self.position)

    def handle_event(self, event, mouse_pos):
        """Обработка событий кнопки"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_clicked = True
                if self.sound_manager:
                    self.sound_manager.play_sound('button_click')

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_clicked and self.rect.collidepoint(mouse_pos):
                if self.action:
                    self.action()
            self.is_clicked = False