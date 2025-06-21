"""
Модуль загрузки игровых ресурсов.

Содержит класс GameResources для централизованной загрузки всех игровых ресурсов:
карт, игрока, камеры, коллизий и других объектов.
"""

import pytmx
import pygame
from level.player import Player
from level.camera import Camera
from level.level_renderer import LevelRenderer
from level.collisions import CollisionHandler
from core.config import config
from core.pathutils import resource_path
from core.sound_manager import SoundManager


class GameResources:
    """
    Класс для загрузки и управления игровыми ресурсами.
    
    Обеспечивает централизованную загрузку всех необходимых ресурсов
    для корректной работы игры.
    """

    def __init__(self, game):
        """
        Инициализация загрузчика ресурсов.
        
        Args:
            game: Ссылка на основной объект игры.
        """
        self.game = game

    def load_game_resources(self):
        """
        Загружает все игровые ресурсы.
        
        Включает загрузку карты, создание игрока, камеры,
        обработчика коллизий и других игровых объектов.
        """
        try:
            if config.DEBUG_MODE:
                print("Загрузка карты...")

            self.game.level = pytmx.TiledMap(resource_path(config.LEVEL_MAP_PATH))
            map_width = self.game.level.width * self.game.level.tilewidth
            map_height = self.game.level.height * self.game.level.tileheight

            if config.DEBUG_MODE:
                print(f"Карта загружена. Размер: {map_width}x{map_height}")

            # Загрузка коллизий
            self.game.collision_handler = CollisionHandler()
            self.game.collision_objects = self.game.collision_handler.load_collision_objects(self.game.level)
            self.game.interactive_objects = []

            # Загрузка интерактивных объектов
            for layer in self.game.level.layers:
                if hasattr(layer, 'name') and hasattr(layer, '__iter__'):
                    for obj in layer:
                        if hasattr(obj, 'properties') and obj.properties.get('interactive', False):
                            self.game.interactive_objects.append(obj)

            if config.DEBUG_MODE:
                print(f"Загружено объектов коллизий: {len(self.game.collision_objects)}")

            # Создаем менеджер звука
            self.sound_manager = SoundManager()
            if config.DEBUG_MODE:
                print(f"[RESOURCES DEBUG] Создан sound_manager: {self.sound_manager}")
            
            # Устанавливаем ссылку на game в sound_manager для доступа к глобальному состоянию
            self.sound_manager.game = self.game
            if config.DEBUG_MODE:
                print(f"[RESOURCES DEBUG] Установлен game в sound_manager: {self.sound_manager.game}")
                print(f"[RESOURCES DEBUG] inventory_open_state: {getattr(self.game, 'inventory_open_state', 'NOT_FOUND')}")

            # Создание игрока
            if config.DEBUG_MODE:
                print("Создание игрока...")

            spawn_x, spawn_y = self._find_spawn_point()

            # Передаем ссылку на game в sound_manager, чтобы Player мог получить game
            self.game.sound_manager.game = self.game
            self.game.player = Player(spawn_x, spawn_y, self.game.sound_manager)

            if config.DEBUG_MODE:
                print(f"Игрок создан. Позиция: {self.game.player.hitbox.topleft}")
                print(f"Размер спрайта: {self.game.player.image.get_size()}")
                print(f"Размер хитбокса: {self.game.player.hitbox.size}")

            # Сохраняем состояние инвентаря в глобальное поле игры ПЕРЕД созданием нового UI
            if hasattr(self.game, 'player_ui') and self.game.player_ui:
                self.game.inventory_open_state = self.game.player_ui.inventory.inventory_open
                if config.DEBUG_MODE:
                    print(f"[RESOURCES DEBUG] Сохраняем состояние инвентаря в game: {self.game.inventory_open_state}")
            else:
                self.game.inventory_open_state = False
                if config.DEBUG_MODE:
                    print(f"[RESOURCES DEBUG] player_ui не существует, используем False")

            if config.DEBUG_MODE:
                print(f"[RESOURCES DEBUG] Перед созданием UI: inventory_open_state={self.game.inventory_open_state}")

            # Инициализация UI игрока
            from UI.player_ui import PlayerUI
            self.game.player_ui = PlayerUI(self.game.virtual_screen, self.game.player.stats)
            
            # Подписываем UI на изменения характеристик
            self.game.player.stats.add_observer(self.game.player_ui)
            
            if config.DEBUG_MODE:
                print(f"[RESOURCES DEBUG] UI игрока создан: {self.game.player_ui}")
                print(f"[RESOURCES DEBUG] Статистика игрока: HP={self.game.player.stats.health.current_value}/{self.game.player.stats.health.max_value}")
                print(f"[RESOURCES DEBUG] UI подписан на изменения характеристик")

            self.game.all_sprites = pygame.sprite.Group()
            # Player наследуется от pygame.sprite.Sprite, поэтому можно добавлять в группу
            self.game.all_sprites.add(self.game.player)  # type: ignore
            self.game.camera = Camera(map_width, map_height)
            self.game.level_renderer = LevelRenderer(self.game.level, self.game.camera)

            # Обновление игрока и камеры
            self.game.player.update(0, map_width, map_height, self.game.collision_objects)
            if self.game.camera and self.game.player:
                self.game.camera.update(self.game.player)

        except Exception as e:
            if config.DEBUG_MODE:
                print(f"Ошибка загрузки ресурсов: {e}")
            raise

    def _find_spawn_point(self) -> tuple[int, int]:
        """
        Находит точку спавна игрока на карте.
        
        Returns:
            Кортеж (x, y) с координатами точки спавна.
        """
        spawn_x = 200
        spawn_y = 200

        # Поиск точки спавна
        spawn_found = False
        spawn_point_name = getattr(self.game, 'next_spawn_point_name', None)

        if spawn_point_name:
            for layer in self.game.level.layers:
                if hasattr(layer, 'name') and layer.name == "PlayerSpawn":
                    for obj in layer:
                        if (hasattr(obj, 'properties') and
                            obj.properties.get("object_type") == spawn_point_name) or \
                                (hasattr(obj, 'name') and obj.name == spawn_point_name):
                            spawn_x = int(obj.x)
                            spawn_y = int(obj.y)
                            spawn_found = True
                            break
                    if spawn_found:
                        break
            self.game.next_spawn_point_name = None

        if not spawn_found:
            for layer in self.game.level.layers:
                if hasattr(layer, 'name') and layer.name == "PlayerSpawn":
                    for obj in layer:
                        if (hasattr(obj, 'properties') and
                                obj.properties.get("object_type") == "player_spawn"):
                            spawn_x = int(obj.x)
                            spawn_y = int(obj.y)
                            if config.DEBUG_MODE:
                                print(f"Найден спавн игрока: ({spawn_x}, {spawn_y})")
                            break
                    break
            else:
                if config.DEBUG_MODE:
                    print(f"Спавн не найден, используем fallback: ({spawn_x}, {spawn_y})")

        return spawn_x, spawn_y

    def load_new_map(self, map_path: str):
        """
        Загружает новую карту.
        
        Args:
            map_path: Путь к новой карте.
        """
        setattr(config, 'LEVEL_MAP_PATH', map_path)
        self.load_game_resources()
        self.game.waiting_for_first_update = True
        self.game.wait_for_key_release = True
