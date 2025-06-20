# UI/__init__.py
"""
Модуль пользовательского интерфейса (UI).

Этот модуль содержит все компоненты пользовательского интерфейса игры:
- Базовые элементы интерфейса (кнопки, меню)
- Главное меню игры
- Меню настроек и конфигурации
- Меню выбора языка
- Меню настроек музыки и звука
- Специализированные элементы управления

Импортируемые классы:
- Menu: базовый класс для всех меню
- Button: универсальный компонент кнопки
- MainMenu: главное меню игры с навигацией
- SettingsMenu: меню настроек игры
- LanguageMenu: меню выбора языка интерфейса
- MusicSettingsMenu: меню настроек музыки и звука

Все компоненты UI доступны для импорта из других модулей игры.
"""

from .menu import Menu
from .button import Button
from .main_menu import MainMenu
from .settings_menu import SettingsMenu
from .language_menu import LanguageMenu
from .music_settings_menu import MusicSettingsMenu
