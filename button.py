import pygame


class Button:
    def __init__(self, normal_image, hover_image, position, action=None):
        self.normal_image = normal_image
        self.hover_image = hover_image
        self.rect = pygame.Rect(position[0], position[1], normal_image.get_width(),
                                normal_image.get_height())
        self.action = action
        self.clicked = False

    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            surface.blit(self.hover_image, self.rect)
        else:
            surface.blit(self.normal_image, self.rect)

    def handle_event(self, event, mouse_pos, sound_manager):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos) and not self.clicked:
            self.clicked = True
            if self.action:
                sound_manager.play_button_click()
                self.action()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
