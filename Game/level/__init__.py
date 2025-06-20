# level/__init__.py
"""
Модуль игрового уровня (level).

Этот модуль содержит все компоненты, связанные с игровым уровнем и игровым процессом:
- Игрок и его характеристики
- Система камеры и следования за игроком
- Обработка спрайтов и анимаций
- Рендеринг уровня и тайлов
- Система коллизий и физики
- Обработка движения игрока

Импортируемые классы:
- Player: основной класс игрока с анимациями и состоянием
- Camera: система камеры для следования за игроком
- SpriteSheet: обработка спрайтшитов и анимаций
- LevelRenderer: рендеринг уровня, тайлов и объектов
- CollisionHandler: обработка коллизий между объектами
- PlayerMovementHandler: управление движением игрока

Все компоненты уровня доступны для импорта из других модулей игры.
"""

from .player import Player
from .camera import Camera
from .spritesheet import SpriteSheet
from .level_renderer import LevelRenderer
from .collisions import CollisionHandler
from .player_movement import PlayerMovementHandler
