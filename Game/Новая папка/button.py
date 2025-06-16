import pygame


class Button:
    def __init__(self, normal_image, hover_image, position, action=None):
        self.normal_image = normal_image
        self.hover_image = hover_image
        self.position = position
        self.rect = pygame.Rect(position[0], position[1],
                                normal_image.get_width(),
                                normal_image.get_height())
        self.action = action
        self.is_hovered = False
        self.is_clicked = False

    def handle_event(self, event, mouse_pos, sound_manager):
        """Обрабатывает события мыши для кнопки"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(mouse_pos):
                self.is_clicked = True
                if sound_manager:
                    sound_manager.play_sound('button_click')

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_clicked and self.rect.collidepoint(mouse_pos):
                self.is_clicked = False
                if self.action:
                    self.action()
            else:
                self.is_clicked = False

    def draw(self, surface, mouse_pos):
        """Отрисовывает кнопку с учетом состояния"""
        current_image = self.hover_image if self.rect.collidepoint(mouse_pos) else self.normal_image
        surface.blit(current_image, self.position)