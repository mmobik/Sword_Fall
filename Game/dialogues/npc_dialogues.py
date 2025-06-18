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

class RoyalGuardDialogue:
    def __init__(self, npc_id):
        self.npc_id = npc_id
        self.dialogue_file = os.path.join(os.path.dirname(__file__), 'royal_guard.json')
        self._load_dialogues()
        self.interaction_count = 0
        self.phase = 'initial'
        self.phase_index = 0

    def _load_dialogues(self):
        with open(self.dialogue_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        guard_data = data['interactive']['royal_guard']
        self.dialog_flow = guard_data['dialog_flow']
        self.thresholds = guard_data['interaction_thresholds']

    def get_current_dialogue(self):
        # Определяем фазу по количеству взаимодействий
        phase = self._get_phase()
        lines = self.dialog_flow[phase]
        idx = self.phase_index % len(lines)
        return lines[idx]

    def next_dialogue(self):
        prev_phase = self._get_phase()
        self.interaction_count += 1
        new_phase = self._get_phase()
        if new_phase != prev_phase:
            self.phase_index = 0
        else:
            self.phase_index += 1

    def _get_phase(self):
        if self.interaction_count >= self.thresholds['final_start']:
            return 'final'
        elif self.interaction_count >= self.thresholds['angry_start']:
            return 'angry'
        elif self.interaction_count >= self.thresholds['repeat_start']:
            return 'repeat'
        else:
            return 'initial'

    def is_finished(self):
        # Стражник всегда что-то говорит, но после final_start только финальные реплики
        return False 