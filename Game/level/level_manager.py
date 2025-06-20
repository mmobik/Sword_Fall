import pytmx
import pygame
from level.level_renderer import LevelRenderer
from level.collisions import CollisionHandler
from level.player import Player
from level.camera import Camera
from core.config import config


class LevelManager:
    def __init__(self, level_path):
        self.tmx_data = pytmx.util_pygame.load_pygame(level_path)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.collision_handler = CollisionHandler()
        self.collision_objects = self.collision_handler.load_collision_objects(self.tmx_data)
        self.player = self._init_player()
        self.camera = Camera(self.width, self.height)
        self.renderer = LevelRenderer(self.tmx_data, self.camera)

    def _init_player(self):
        # Поиск стартовой позиции игрока в объектном слое
        for layer in self.tmx_data.layers:
            if hasattr(layer, "name") and layer.name == config.PLAYER_SETTINGS["PLAYER_LAYER_NAME"]:
                for obj in layer:
                    if obj.name == config.PLAYER_SETTINGS["PLAYER_OBJECT_NAME"]:
                        return Player(int(obj.x), int(obj.y))
        # Если не найдено, ставим по центру
        return Player(self.width // 2, self.height // 2)

    def update(self, dt):
        self.player.update(dt, self.width, self.height, self.collision_objects)
        self.camera.update(self.player)

    def render(self, surface):
        self.renderer.render(surface, self.player.hitbox.center)
        # Отрисовка игрока
        surface.blit(self.player.image, self.camera.apply(self.player.rect))
        # Отрисовка хитбокса игрока в режиме дебага
        if getattr(config, 'DEBUG_MODE', False):
            hitbox_rect = self.camera.apply(self.player.hitbox)
            pygame.draw.rect(surface, config.DEBUG_COLORS["HITBOX"], hitbox_rect, 2)
        self.renderer.render_overlap_tiles(surface, self.player.hitbox.center)

    def get_level_size(self):
        """Возвращает размеры текущего уровня"""
        if self.tmx_data:
            return (self.tmx_data.width * self.tmx_data.tilewidth,
                    self.tmx_data.height * self.tmx_data.tileheight)
        return config.DEFAULT_LEVEL_WIDTH, config.DEFAULT_LEVEL_HEIGHT
