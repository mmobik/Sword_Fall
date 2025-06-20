# core/__init__.py
"""
Основной модуль ядра игры (core).

Этот модуль содержит все основные компоненты игрового движка:
- Конфигурация и настройки игры
- Управление звуком и музыкой
- Управление состоянием игры
- Обработка диалогов и панелей диалогов
- Обработка взаимодействий с дверями
- Главный игровой цикл
- Управление игровыми ресурсами
- Система рендеринга
- Утилиты и вспомогательные функции

Все компоненты импортируются здесь для удобного доступа из других модулей.
"""

from .config import *
from .sound_manager import SoundManager
from .game_state_manager import GameStateManager
from .utils import *
from .dialogue_panel import DialoguePanel
from .door_handler import DoorInteractionHandler
from .game_loop import GameLoop
from .dialogue_handler import DialogueHandler
from .game_resources import GameResources
from .rendering import Renderer
