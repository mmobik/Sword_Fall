from dialogues.npc_dialogues import KingDialogue, RoyalGuardDialogue

class DialogueHandler:
    def __init__(self, game):
        self.game = game

    def try_interact_with_npc(self):
        obj = self.game.active_npc_obj
        if obj is None:
            return
        npc_type = obj.properties.get('interactive_type', '').lower()
        npc_id = getattr(obj, 'id', id(obj))
        
        if npc_type == 'the guard' or npc_type == 'royal_guard':
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
        elif npc_type == 'king':
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
        elif npc_type == 'doors':
            self.game.door_handler.interact(obj)
        # Здесь можно добавить обработку других типов NPC 