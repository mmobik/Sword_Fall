"""
Модуль панели диалогов.

Содержит класс DialoguePanel для отображения диалоговых панелей
с NPC, включая изображения персонажей и текст диалогов.
"""

import pygame
from core.config import config


class DialoguePanel:
    """
    Класс для отображения диалоговых панелей.
    
    Обеспечивает рендеринг панели диалога с изображением NPC,
    именем персонажа и текстом диалога.
    """

    def __init__(self, game):
        """
        Инициализация панели диалогов.
        
        Args:
            game: Ссылка на основной объект игры.
        """
        self.game = game

    def render(self):
        """Отрисовывает панель диалога с NPC."""
        panel_w, panel_h = self.game.dialogue_panel_img.get_size()
        x = (config.VIRTUAL_WIDTH - panel_w) // 2
        y = config.VIRTUAL_HEIGHT - panel_h - config.DIALOGUE_PANEL["OFFSET_Y"]

        # Отрисовка изображения NPC
        if self.game.active_npc_obj:
            npc_type = self.game.active_npc_obj.properties.get(
                'interactive_type', '').lower()

            if ((npc_type == 'the guard' or npc_type == 'royal_guard') and
                    self.game.guard_img):
                guard_w, guard_h = self.game.guard_img.get_size()
                guard_x = x - guard_w + 50
                guard_y = y - guard_h // 1.65
                self.game.virtual_screen.blit(self.game.guard_img, (guard_x, guard_y))

            elif npc_type == 'king' and self.game.king_img:
                king_w, king_h = self.game.king_img.get_size()
                king_x = x - king_w + 50
                king_y = y - king_h // 1.65
                self.game.virtual_screen.blit(self.game.king_img, (king_x, king_y))

        # Отрисовка панели диалога
        self.game.virtual_screen.blit(self.game.dialogue_panel_img, (x, y))

        # Отрисовка имени NPC
        npc_name = "Стражник"
        if self.game.active_npc_obj:
            npc_type = self.game.active_npc_obj.properties.get(
                'interactive_type', '').lower()
            if npc_type == 'king':
                npc_name = "Король"

        name_font = pygame.font.SysFont(
            'Arial', config.DIALOGUE_PANEL["FONT_SIZE"] + 8, bold=True)
        name_surface = name_font.render(
            npc_name, True, config.DIALOGUE_PANEL["FONT_COLOR"])
        name_x = x + config.DIALOGUE_PANEL["TEXT_OFFSET_X"]
        name_y = y
        self.game.virtual_screen.blit(name_surface, (name_x, name_y))

        # Отрисовка текста диалога
        if self.game.dialogue_text_shown:
            text_surface = self.game.dialogue_font.render(
                self.game.dialogue_text_shown,
                True,
                config.DIALOGUE_PANEL["FONT_COLOR"]
            )
            text_x = x + config.DIALOGUE_PANEL["TEXT_OFFSET_X"]
            text_y = name_y + name_surface.get_height() + 8
            self.game.virtual_screen.blit(text_surface, (text_x, text_y))
