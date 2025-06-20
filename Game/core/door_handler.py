"""
Модуль обработчика дверей.

Содержит класс DoorInteractionHandler для обработки взаимодействия
с дверями и перехода между локациями.
"""


class DoorInteractionHandler:
    """
    Класс для обработки интерактивных дверей и перехода между локациями.
    
    Управляет переходом игрока между различными картами через двери,
    включая остановку звуков и установку точки спавна.
    """

    def __init__(self, game):
        """
        Инициализация обработчика дверей.
        
        Args:
            game: Ссылка на основной объект игры.
        """
        self.game = game

    def interact(self, obj):
        """
        Обрабатывает взаимодействие с дверью.
        
        Args:
            obj: Объект двери из карты.
        """
        # Остановить звук шагов перед переходом
        player = getattr(self.game, 'player', None)
        if player:
            steps_channel = getattr(player, '_steps_channel', None)
            if steps_channel:
                steps_channel.stop()
                setattr(player, '_steps_channel', None)
            player.is_walking = False

        # Путь к новой карте можно хранить в свойстве объекта или задать явно
        new_map_path = obj.properties.get('target_map',
                                          'assets/Tiles/Audience Hall .tmx')

        # Если у двери указано spawn_point_name, передаем его
        spawn_point_name = obj.properties.get('spawn_point_name',
                                              'royal_door_spawn')
        self.game.next_spawn_point_name = spawn_point_name
        self.game.load_new_map(new_map_path)
