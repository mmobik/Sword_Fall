from typing import Iterable

from level.player_stats import PlayerStats, StatModifier, BaseStat  # type: ignore
from UI.items import InventoryItem
from UI.equipment_data import ITEM_DATABASE

"""
Логика влияния снаряжения (экипированных предметов) на общие характеристики игрока.

Идея:
- Все надетые предметы находятся в `Inventory.equipment_slots`.
- При любом изменении экипировки мы пересчитываем бонусы:
  1) убираем ВСЕ старые модификаторы от снаряжения (источник начинается с 'equip:')
  2) проходим по всем надетым предметам и добавляем новые модификаторы.

Так мы избегаем сложной логики добавления/удаления по одному предмету.
"""


# Какие поля из stats предмета на какие характеристики влияют
EQUIPMENT_STAT_MAPPING = {
    # ключ в item.stats      -> (имя стата в PlayerStats.stats, is_percentage)
    "attack": ("damage", False),
    "defense": ("defense", False),
    "magic": ("magic", False),
    "luck": ("luck_stat", False),
    # Бонус к максимальной мане / здоровью можно хранить как плоский модификатор
    "max_mana_bonus": ("mana", False),
    "max_health_bonus": ("health", False),
}


def _clear_equipment_modifiers(player_stats: PlayerStats) -> None:
    """
    Удаляет все модификаторы, добавленные экипированными предметами.

    Мы считаем, что все такие модификаторы имеют source, начинающийся с 'equip:'.
    """
    for stat in player_stats.stats.values():
        if not isinstance(stat, BaseStat):
            continue
        # Фильтруем модификаторы по source
        stat.modifiers = [
            m for m in stat.modifiers if not str(getattr(m, "source", "")).startswith("equip:")
        ]
        stat._recalculate_value()


def _apply_item_modifiers(player_stats: PlayerStats, item: InventoryItem) -> None:
    """
    Применяет модификаторы от одного предмета к характеристикам игрока.
    """
    if not item or not item.stats:
        return

    source = f"equip:{item.id}"

    for stat_key, value in item.stats.items():
        mapping = EQUIPMENT_STAT_MAPPING.get(stat_key)
        if not mapping:
            # Этот ключ мы сейчас не обрабатываем (например, attack_speed_bonus и т.п.)
            continue

        stat_name, is_percentage = mapping
        stat = player_stats.get_stat(stat_name)
        if not stat:
            continue

        modifier = StatModifier(
            value=float(value),
            duration=None,
            source=source,
            is_percentage=is_percentage,
        )
        stat.add_modifier(modifier)


def recalculate_equipment_bonuses(player_stats: PlayerStats, equipped_items: Iterable[InventoryItem]) -> None:
    """
    Полностью пересчитывает бонусы от экипированных предметов.

    - Сначала убираем все старые модификаторы от экипировки
    - Затем проходим по всем предметам в equipment_slots и применяем их статы
    """
    _clear_equipment_modifiers(player_stats)

    for item in equipped_items:
        if not item:
            continue
        _apply_item_modifiers(player_stats, item)

