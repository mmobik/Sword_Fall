"""
Модуль обработчика диалогов.

Содержит класс DialogueHandler для управления диалогами с NPC,
включая загрузку диалогов, управление состоянием и взаимодействие.
"""

from dialogues.npc_dialogues import KingDialogue, RoyalGuardDialogue


class DialogueHandler:
    """
    Класс для обработки диалогов с NPC.
    
    Управляет загрузкой диалогов, их отображением и переходом
    между репликами для различных типов NPC.
    """

    def __init__(self, game):
        """
        Инициализация обработчика диалогов.
        
        Args:
            game: Ссылка на основной объект игры.
        """
        self.game = game

    def try_interact_with_npc(self):
        """Пытается начать взаимодействие с активным NPC."""
        obj = self.game.active_npc_obj
        if obj is None:
            return
            
        npc_type = obj.properties.get('interactive_type', '').lower()
        npc_id = getattr(obj, 'id', id(obj))

        if npc_type == 'the guard' or npc_type == 'royal_guard':
            self._handle_guard_dialogue(npc_id)
        elif npc_type == 'king':
            self._handle_king_dialogue(npc_id)
        elif npc_type == 'doors':
            self.game.door_handler.interact(obj)
        # TODO: Добавить обработку других типов NPC

    def _handle_guard_dialogue(self, npc_id: int):
        """
        Обрабатывает диалог со стражником.
        
        Args:
            npc_id: Уникальный идентификатор NPC.
        """
        if self.game.show_dialogue:
            # Пока окно открыто, не даем открыть новую реплику
            return
            
        if npc_id not in self.game.npc_dialogues:
            self.game.npc_dialogues[npc_id] = RoyalGuardDialogue(npc_id)
            
        dialogue = self.game.npc_dialogues[npc_id]
        self.game.dialogue_text = dialogue.get_current_dialogue()
        self.game.dialogue_text_shown = ""
        self.game.dialogue_type_time = self.game.time()
        self.game.show_dialogue = True
        self.game.dialogue_start_time = self.game.time()
        dialogue.next_dialogue()

    def _handle_king_dialogue(self, npc_id: int):
        """
        Обрабатывает диалог с королем.
        
        Args:
            npc_id: Уникальный идентификатор NPC.
        """
        if npc_id not in self.game.npc_dialogues:
            self.game.npc_dialogues[npc_id] = KingDialogue(npc_id)
            
        dialogue = self.game.npc_dialogues[npc_id]
        
        if self.game.show_dialogue:
            next_text = dialogue.next_dialogue()
            if next_text is None:
                self.game.show_dialogue = False
                self.game.dialogue_text = ""
                self.game.dialogue_text_shown = ""
                self.game.active_npc_obj = None
            else:
                self.game.dialogue_text = next_text
                self.game.dialogue_text_shown = ""
                self.game.dialogue_type_time = self.game.time()
                self.game.dialogue_start_time = self.game.time()
        else:
            self.game.dialogue_text = dialogue.get_current_dialogue()
            self.game.dialogue_text_shown = ""
            self.game.dialogue_type_time = self.game.time()
            self.game.show_dialogue = True
            self.game.dialogue_start_time = self.game.time()
            dialogue.next_dialogue()
