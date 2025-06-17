import pygame
import pytmx
from core.config import config


class LevelRenderer:
    def __init__(self, tmx_data, camera):
        self.tmx_data = tmx_data
        self.camera = camera
        self.tileset_images = {}
        self.chunk_size = 32
        self.chunk_width = self.chunk_size * self.tmx_data.tilewidth
        self.chunk_height = self.chunk_size * self.tmx_data.tileheight
        self.chunks_info = {}
        self.overlap_layers = []  # Слои, которые рисуются поверх игрока

        # Находим слои с overlap_player = True
        for layer in self.tmx_data.layers:
            if hasattr(layer, "properties") and layer.properties.get("overlap_player", False):
                self.overlap_layers.append(layer)

        self._create_all_chunks()

    def _get_chunk_coords(self, tile_x, tile_y):
        return tile_x // self.chunk_size, tile_y // self.chunk_size

    def _create_chunk(self, chunk_x, chunk_y):
        chunk = pygame.Surface((self.chunk_width, self.chunk_height), pygame.SRCALPHA)
        x_1 = chunk_x * self.chunk_size
        y_1 = chunk_y * self.chunk_size
        x_2 = (chunk_x + 1) * self.chunk_size
        y_2 = (chunk_y + 1) * self.chunk_size

        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if x_1 <= x < x_2 and y_1 <= y < y_2:
                        x_offset = (x - x_1) * self.tmx_data.tilewidth
                        y_offset = (y - y_1) * self.tmx_data.tileheight
                        tileset_path, rect, flags = image

                        if tileset_path not in self.tileset_images:
                            try:
                                self.tileset_images[tileset_path] = pygame.image.load(tileset_path).convert_alpha()
                            except FileNotFoundError:
                                print(f"Ошибка: Не удалось найти файл тайлсета '{tileset_path}'")
                                continue

                        tileset_image = self.tileset_images[tileset_path]
                        tile_surface = tileset_image.subsurface(rect)

                        # Правильная обработка трансформаций (как в Tiled)
                        if flags.flipped_diagonally:
                            tile_surface = pygame.transform.rotate(tile_surface, -90)
                            if flags.flipped_horizontally or flags.flipped_vertically:
                                tile_surface = pygame.transform.flip(tile_surface, flags.flipped_horizontally,
                                                                     flags.flipped_vertically)
                        else:
                            if flags.flipped_horizontally or flags.flipped_vertically:
                                tile_surface = pygame.transform.flip(tile_surface, flags.flipped_horizontally,
                                                                     flags.flipped_vertically)

                        chunk.blit(tile_surface, (x_offset, y_offset))

        self.chunks_info[(chunk_x, chunk_y)] = chunk

    def _create_all_chunks(self):
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    chunk_x, chunk_y = self._get_chunk_coords(x, y)
                    if (chunk_x, chunk_y) not in self.chunks_info:
                        self._create_chunk(chunk_x, chunk_y)

    def render(self, surface, player_pos=None):
        camera_x = self.camera.offset.x
        camera_y = self.camera.offset.y

        # Отрисовка обычных слоёв (под игроком)
        for chunk_x in range(int(camera_x // self.chunk_width),
                             int((camera_x + config.VIRTUAL_WIDTH) // self.chunk_width) + 1):
            for chunk_y in range(int(camera_y // self.chunk_height),
                                 int((camera_y + config.VIRTUAL_HEIGHT) // self.chunk_height) + 1):
                if (chunk_x, chunk_y) in self.chunks_info:
                    chunk = self.chunks_info[(chunk_x, chunk_y)]
                    chunk_screen_x = chunk_x * self.chunk_width - camera_x
                    chunk_screen_y = chunk_y * self.chunk_height - camera_y
                    surface.blit(chunk, (chunk_screen_x, chunk_screen_y))

        # Отрисовка слоёв overlap_player (если игрок зашёл за них)
        if player_pos:
            for layer in self.overlap_layers:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, image in layer.tiles():
                        tile_rect = pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                self.tmx_data.tilewidth, self.tmx_data.tileheight)
                        if tile_rect.collidepoint(player_pos):
                            # Отрисовка тайла поверх игрока
                            tile_surface = self._get_tile_surface(image)
                            surface.blit(tile_surface, (tile_rect.x - camera_x, tile_rect.y - camera_y))

    def render_overlap_tiles(self, surface, player_pos):
        camera_x = self.camera.offset.x
        camera_y = self.camera.offset.y

        for layer in self.overlap_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    tile_rect = pygame.Rect(
                        x * self.tmx_data.tilewidth,
                        y * self.tmx_data.tileheight,
                        self.tmx_data.tilewidth,
                        self.tmx_data.tileheight
                    )
                    if tile_rect.collidepoint(player_pos):
                        try:
                            tile_surface = self._get_tile_surface(image)
                            surface.blit(
                                tile_surface,
                                (tile_rect.x - camera_x, tile_rect.y - camera_y)
                            )
                        except Exception as e:
                            print(f"Ошибка при отрисовке тайла: {e}")

    def _get_tile_surface(self, image):
        tileset_path, rect, flags = image

        if tileset_path not in self.tileset_images:
            try:
                self.tileset_images[tileset_path] = pygame.image.load(tileset_path).convert_alpha()
            except FileNotFoundError:
                print(f"Ошибка: Не удалось найти файл тайлсета '{tileset_path}'")
                return pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)

        tileset_image = self.tileset_images[tileset_path]
        tile_surface = tileset_image.subsurface(rect)

        # Применяем трансформации
        if flags.flipped_diagonally:
            tile_surface = pygame.transform.rotate(tile_surface, -90)
            if flags.flipped_horizontally or flags.flipped_vertically:
                tile_surface = pygame.transform.flip(tile_surface,
                                                     flags.flipped_horizontally,
                                                     flags.flipped_vertically)
        else:
            if flags.flipped_horizontally or flags.flipped_vertically:
                tile_surface = pygame.transform.flip(tile_surface,
                                                     flags.flipped_horizontally,
                                                     flags.flipped_vertically)

        return tile_surface