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
    if hasattr(sys, '_MEIPASS'):  # type: ignore[attr-defined]
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path) 