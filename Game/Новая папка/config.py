"""
Конфигурационные параметры игры.

Содержит настройки экрана, пути к ресурсам, цвета,
параметры анимации и игрового уровня.
"""

# Настройки экрана
WIDTH = 1920
HEIGHT = 1080
GAME_NAME = "SwordFall"
FPS = 144
TARGET_FPS = 60

# Настройки кнопок
BUTTON_SPACING = 125
MENU_BUTTON_X = WIDTH // 3
SETTINGS_BUTTON_X = WIDTH // 2 - 200
SETTINGS_BUTTON_Y_START = HEIGHT // 2 - 200
BACK_BUTTON_X = WIDTH // 2 - 200
BACK_BUTTON_Y = HEIGHT - 300

# Настройка перехода
FADE_DURATION = 0.5

# Пути к игровым ресурсам
ASSETS = {
    "ICON": "assets/Images/Icons/Game_icon_1.jpg",  # Путь к иконке игры
    "BACKGROUND": "assets/Images/Game/Backgrounds/Levels/first_level.png",  # Путь к фоновому изображению уровня
    "IDLE_SHEET": "assets/Sprites/Idle.png",  # Путь к спрайт-листу для анимации покоя
    "RUN_SHEET": "assets/Sprites/Run.png"  # Путь к спрайт-листу для анимации бега
}

# Цвета, используемые в игре
GAME_COLORS = {
    "DARK_BLUE": (0, 33, 55),  # Темно-синий цвет для фона
    "BLUE": (46, 68, 116),  # Основной синий цвет
    "WHITE": (255, 255, 255)  # Белый цвет для интерфейса
}

# Параметры анимации
FRAME_SIZE = (128, 64)  # Размер одного кадра анимации

# Координаты кадров анимации в спрайт-листах
ANIMATION_FRAMES = {
    "IDLE": [
        (0, 0), (128, 0),
        (0, 64), (128, 64),
        (0, 128), (128, 128),
        (0, 192), (128, 192)
    ],
    "RUN": [
        (0, 0), (128, 0),
        (0, 64), (128, 64),
        (0, 128), (128, 128),
        (0, 192), (128, 192)
    ]
}

# Параметры игрового уровня
DEFAULT_LEVEL_WIDTH = WIDTH * 4  # Ширина уровня по умолчанию
DEFAULT_LEVEL_HEIGHT = HEIGHT * 4  # Высота уровня по умолчанию

# Параметры игрока
SPEED = 300  # Базовая скорость перемещения игрока
DEFAULT_ANIMATION_SPEED = 0.15  # Скорость смены кадров анимации
NO_ANIMATION = float('inf')  # Значение для отключения анимации
PLAYER_START_X = DEFAULT_LEVEL_WIDTH // 2  # Стартовая позиция игрока по X
PLAYER_START_Y = DEFAULT_LEVEL_HEIGHT // 2  # Стартовая позиция игрока по Y
