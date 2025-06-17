import pygame
import pytmx
from camera import Camera
from player import Player
import config
from level_renderer import LevelRenderer
from collisions import CollisionHandler


def main():
    pygame.init()

    # Инициализация экрана
    virtual_screen = pygame.Surface((config.VIRTUAL_WIDTH, config.VIRTUAL_HEIGHT))
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.GAME_NAME)

    # Загрузка иконки
    try:
        icon = pygame.image.load(config.ASSETS["ICON"])
        pygame.display.set_icon(icon)
    except FileNotFoundError:
        print("Иконка не загружена")

    # Загрузка карты
    level = pytmx.TiledMap(config.LEVEL_MAP_PATH)
    map_width = level.width * level.tilewidth
    map_height = level.height * level.tileheight

    # Загрузка коллизий
    collision_handler = CollisionHandler()
    collision_objects = collision_handler.load_collision_objects(level)

    # Создание игрока
    spawn_layer = level.get_layer_by_name("PlayerSpawn")
    player_spawn = next(
        (obj for obj in spawn_layer if obj.properties.get("object_type") == "player_spawn"),
        None
    )
    player = Player(
        player_spawn.x if player_spawn else config.PLAYER_START_X,
        player_spawn.y if player_spawn else config.PLAYER_START_Y
    )

    # Проверка размера хитбокса
    if player.hitbox.width > map_width or player.hitbox.height > map_height:
        raise ValueError("Хитбокс игрока больше уровня! Проверьте размеры в config.py")

    all_sprites = pygame.sprite.GroupSingle(player)
    camera = Camera(map_width, map_height)
    level_renderer = LevelRenderer(level, camera)

    # Главный цикл
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(config.FPS) / 1000

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновление
        all_sprites.update(dt, map_width, map_height, collision_objects)
        camera.update(player)

        # Отрисовка
        virtual_screen.fill(config.BG_COLOR)
        level_renderer.render(virtual_screen)

        # Дебаг-отрисовка
        if config.DEBUG_MODE:
            # Границы уровня - УДАЛЯЕМ ОТРИСОВКУ
            # pygame.draw.rect(virtual_screen, (255, 255, 0),
            #                 camera.apply(pygame.Rect(0, 0, map_width, map_height)), 2)
            # Хитбокс игрока
            pygame.draw.rect(virtual_screen, (0, 255, 0), camera.apply(player.hitbox), 1)
            # Объекты коллизий
            for obj in collision_objects:
                pygame.draw.rect(virtual_screen, (255, 0, 0), camera.apply(obj['rect']), 1)

        # Отрисовка спрайтов
        for sprite in all_sprites:
            virtual_screen.blit(sprite.image, camera.apply(sprite.rect))

        level_renderer.render_overlap_tiles(
            virtual_screen,
            (player.hitbox.centerx, player.hitbox.centery)
        )
        # Масштабирование
        scaled_screen = pygame.transform.scale(virtual_screen, (config.WIDTH, config.HEIGHT))
        screen.blit(scaled_screen, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
