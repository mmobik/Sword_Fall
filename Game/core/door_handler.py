from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.game import Game

class DoorInteractionHandler:
    """Класс для обработки интерактивных дверей и перехода между локациями."""
    def __init__(self, game: 'Game'):
        self.game = game

    def interact(self, obj):
        # Остановить звук шагов перед переходом
        player = getattr(self.game, 'player', None)
        if player:
            steps_channel = getattr(player, '_steps_channel', None)
            if steps_channel:
                steps_channel.stop()
                setattr(player, '_steps_channel', None)
            player.is_walking = False
        # Путь к новой карте можно хранить в свойстве объекта или задать явно
        new_map_path = obj.properties.get('target_map', 'assets/Tiles/Audience Hall .tmx')
        self.game._load_new_map(new_map_path) 