"""
Модуль для работы с экипировкой (устарел).
Все предметы теперь загружаются из JSON файлов через items.items_loader.
Этот файл оставлен для обратной совместимости, но не содержит данных.
"""

from typing import Dict, Any, List

# Пустые списки для обратной совместимости
DEFAULT_ACS_ITEMS: List[Dict[str, Any]] = []
ITEM_DATABASE: Dict[str, Dict[str, Any]] = {}
