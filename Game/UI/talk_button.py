import time
import pygame
from core.config import config

class TalkButton:
    def __init__(self, game):
        self.game = game

    def update_talk_button_state(self):
        prev = self.game.show_talk_button
        self.game.show_talk_button = False
        if not self.game.show_dialogue:
            self.game.active_npc_obj = None
        in_zone = False
        if not self.game.player or not self.game.interactive_objects:
            self.game.talk_button_target_alpha = 0
            self.game.talk_button_enter_time = None
            return
        player_rect = self.game.player.hitbox
        for obj in self.game.interactive_objects:
            obj_rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
            npc_type = obj.properties.get('interactive_type', '').lower()
            if ((npc_type == 'the guard' or npc_type == 'royal_guard') or npc_type == 'doors' or npc_type == 'king') and player_rect.colliderect(obj_rect.inflate(10, 10)):
                in_zone = True
                if self.game.active_npc_obj != obj and self.game.show_dialogue:
                    self.game.show_dialogue = False
                    self.game.dialogue_text = ""
                    self.game.dialogue_text_shown = ""
                    self.game.active_npc_obj = None
                self.game.active_npc_obj = obj
                break
        now = time.time()
        if in_zone:
            if self.game.talk_button_enter_time is None:
                self.game.talk_button_enter_time = now
            if (now - self.game.talk_button_enter_time) >= self.game.talk_button_show_delay and not self.game.show_dialogue:
                self.game.show_talk_button = True
        else:
            self.game.talk_button_enter_time = None
        if self.game.show_talk_button and not self.game.show_dialogue:
            self.game.talk_button_target_alpha = 255
        else:
            self.game.talk_button_target_alpha = 0

    def update_talk_button_alpha(self):
        dt = self.game.dt if hasattr(self.game, 'dt') else 1/144
        speed = self.game.talk_button_fade_speed * dt
        if self.game.talk_button_alpha < self.game.talk_button_target_alpha:
            self.game.talk_button_alpha = min(self.game.talk_button_target_alpha, self.game.talk_button_alpha + speed)
        elif self.game.talk_button_alpha > self.game.talk_button_target_alpha:
            self.game.talk_button_alpha = max(self.game.talk_button_target_alpha, self.game.talk_button_alpha - speed)

    def check_talk_button_click(self, mouse_pos):
        if not self.game.talk_button_rect or not self.game.talk_button_rect.collidepoint(mouse_pos):
            return False
        local_x = mouse_pos[0] - self.game.talk_button_rect.x
        local_y = mouse_pos[1] - self.game.talk_button_rect.y
        if (0 <= local_x < self.game.talk_button_img.get_width() and 
            0 <= local_y < self.game.talk_button_img.get_height()):
            pixel_color = self.game.talk_button_img.get_at((local_x, local_y))
            return pixel_color[3] > 0
        return False 