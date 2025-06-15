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

# Пути к изображениям меню
MENU_IMAGES = {
    # Главное меню
    "MAIN_BG": "Images/Main_menu/Backgrounds/Background.jpg",
    "START_BTN": "Images/Main_menu/Buttons/Start/Start_{state}.jpg",  # {state} заменится на before/after
    "SETTINGS_BTN": "Images/Main_menu/Buttons/Settings/Settings_{state}.jpg",
    "EXIT_BTN": "Images/Main_menu/Buttons/Exit/Exit_{state}.jpg",

    # Меню настроек
    "SETTINGS_BG": "Images/Main_menu/Backgrounds/Settings_Background.jpg",
    "GAME_SETTINGS_BTN": "Images/Settings_menu/Settings_game_{state}.jpg",
    "GRAPHICS_SETTINGS_BTN": "Images/Settings_menu/Settings_graphics_{state}.jpg",
    "LANGUAGE_SETTINGS_BTN": "Images/Settings_menu/Settings_language_{state}.jpg",
    "BACK_BTN": "Images/Settings_menu/Settings_back_{state}.jpg",

    # Меню языка
    "LANGUAGE_BG": "Images/Main_menu/Backgrounds/Settings_Background.jpg",
    "ENGLISH_BTN": "Images/Settings_menu/eng_language_{state}.jpg",
    "RUSSIAN_BTN": "Images/Settings_menu/rus_language_{state}.jpg",
    "LANG_BACK_BTN": "Images/Settings_menu/Settings_back_{state}.jpg"
}


def get_image_path(key, state=None):
    """Возвращает путь к изображению с подстановкой состояния (before/after)"""
    path = MENU_IMAGES[key]
    if state and "{state}" in path:
        return path.format(state=state)
    return path
