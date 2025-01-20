class Menu:
    def __init__(self, sound_manager):
        self.buttons = []
        self.sound_manager = sound_manager

    def add_button(self, button):
        self.buttons.append(button)

    def draw(self, surface, mouse_pos):
        for button in self.buttons:
            button.draw(surface, mouse_pos)

    def handle_event(self, event, mouse_pos, sound_manager):
        for button in self.buttons:
            button.handle_event(event, mouse_pos, sound_manager)
