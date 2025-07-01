"""
Модуль для работы с путями к ресурсам.

Содержит функцию resource_path для универсального поиска ресурсов
как в dev-режиме, так и в exe-файле (PyInstaller).
"""

import sys
import os


def resource_path(relative_path):
    """
    Получить абсолютный путь к ресурсу, работает для dev и для PyInstaller.
    :param relative_path: относительный путь к ресурсу внутри проекта
    :return: абсолютный путь
    """
    if hasattr(sys, '_MEIPASS'):  # PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    # Найти корень проекта (где лежит папка Game)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isdir(os.path.join(current_dir, "Game")) and current_dir != os.path.dirname(current_dir):
        current_dir = os.path.dirname(current_dir)
    return os.path.join(current_dir, relative_path) 