import json
import os
from core.pathutils import resource_path


class NPCDialogue:
    def __init__(self, npc_id, dialogue_file):
        self.npc_id = npc_id
        self.dialogue_file = dialogue_file
        self.state = 0
        self.dialogues = self._load_dialogues()

    def _load_dialogues(self):
        if not os.path.exists(resource_path(self.dialogue_file)):
            return []
        with open(resource_path(self.dialogue_file), 'r', encoding='utf-8') as f:
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
        with open(resource_path(self.dialogue_file), 'r', encoding='utf-8') as f:
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

    @staticmethod
    def is_finished():
        # Стражник всегда что-то говорит, но после final_start только финальные реплики
        return False


class KingDialogue:
    def __init__(self, npc_id):
        self.npc_id = npc_id
        self.dialogue_file = os.path.join(os.path.dirname(__file__), 'king.json')
        self._load_dialogues()
        self.interaction_count = 0
        self.phase = 'initial'
        self.phase_index = 0
        # Новые поля для цепочек диалогов
        self.current_chain_index = 0  # Индекс текущей цепочки в фазе
        self.current_chain_position = 0  # Позиция в текущей цепочке
        self.in_dialogue_chain = False  # Флаг, что мы в процессе цепочки диалогов

    def _load_dialogues(self):
        with open(resource_path(self.dialogue_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        king_data = data['interactive']['king']
        self.dialog_flow = king_data['dialog_flow']
        self.thresholds = king_data['interaction_thresholds']

    def get_current_dialogue(self):
        phase = self._get_phase()
        lines = self.dialog_flow[phase]

        # Если мы в процессе цепочки диалогов
        if self.in_dialogue_chain and self.current_chain_index < len(lines):
            chain_data = lines[self.current_chain_index]
            if isinstance(chain_data, dict) and 'chain' in chain_data:
                chain = chain_data['chain']
                if self.current_chain_position < len(chain):
                    return chain[self.current_chain_position]

        # Обычный режим (для обратной совместимости)
        idx = self.phase_index % len(lines)
        line = lines[idx]
        if isinstance(line, dict) and 'chain' in line:
            return line['chain'][0] if line['chain'] else ""
        return line

    def next_dialogue(self):
        prev_phase = self._get_phase()
        self.interaction_count += 1
        new_phase = self._get_phase()

        if new_phase != prev_phase:
            self.phase_index = 0
            self.current_chain_index = 0
            self.current_chain_position = 0
            self.in_dialogue_chain = False
        else:
            # Если мы в процессе цепочки диалогов
            if self.in_dialogue_chain:
                phase = self._get_phase()
                lines = self.dialog_flow[phase]
                if self.current_chain_index < len(lines):
                    chain_data = lines[self.current_chain_index]
                    if isinstance(chain_data, dict) and 'chain' in chain_data:
                        chain = chain_data['chain']
                        self.current_chain_position += 1
                        # Если достигли конца цепочки
                        if self.current_chain_position >= len(chain):
                            self.in_dialogue_chain = False
                            self.current_chain_position = 0
                            self.phase_index += 1
                            return None  # Сигнал для закрытия диалога
                        return chain[self.current_chain_position]
            else:
                # Начинаем новую цепочку
                phase = self._get_phase()
                lines = self.dialog_flow[phase]
                if self.phase_index < len(lines):
                    line = lines[self.phase_index]
                    if isinstance(line, dict) and 'chain' in line:
                        self.in_dialogue_chain = True
                        self.current_chain_index = self.phase_index
                        self.current_chain_position = 0
                        chain = line['chain']
                        if chain:
                            return chain[0]
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

    @staticmethod
    def is_finished():
        return False
