import pygame
import config
from player import Player
from camera import Camera
from level_manager import create_level

pygame.init()

# Настройки и инициализация экрана
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
pygame.display.set_caption(config.GAME_NAME)
icon = pygame.image.load(config.ASSETS["ICON"])
pygame.display.set_icon(icon)


level_width, level_height, background = create_level()


# Создаем игрока в центре уровня
camera = Camera(level_width, level_height)
player = Player(level_width // 2, level_height // 2)
# noinspection PyTypeChecker
all_sprites = pygame.sprite.Group(player)

# Главный игровой цикл
clock = pygame.time.Clock()
running = True
while running:
    dt = clock.tick(config.FPS) / 1000

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновление всех спрайтов и камеры
    all_sprites.update(dt, level_width, level_height)
    camera.update(player)

    # Рисуем только видимую часть фона
    screen.blit(background, (0, 0), (camera.offset.x, camera.offset.y, config.WIDTH, config.HEIGHT))

    # Рисуем все спрайты с учетом позиции камеры
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite.rect))

    pygame.display.flip()

pygame.quit()
