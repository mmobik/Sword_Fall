import json
import os

class NPCDialogue:
    def __init__(self, npc_id, dialogue_file):
        self.npc_id = npc_id
        self.dialogue_file = dialogue_file
        self.state = 0
        self.dialogues = self._load_dialogues()

    def _load_dialogues(self):
        if not os.path.exists(self.dialogue_file):
            return []
        with open(self.dialogue_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('dialogues', [])

    def get_current_dialogue(self):
        if self.state < len(self.dialogues):
            return self.dialogues[self.state]
        return None

    def next_dialogue(self):
        if self.state < len(self.dialogues) - 1:
            self.state += 1
            return self.dialogues[self.state]
        else:
            self.state = len(self.dialogues)  # Окончание диалога
            return None

    def is_finished(self):
        return self.state >= len(self.dialogues)

class RoyalGuardDialogue(NPCDialogue):
    def __init__(self, npc_id):
        super().__init__(npc_id, os.path.join(os.path.dirname(__file__), 'royal_guard.json')) 