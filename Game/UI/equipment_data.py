from typing import Dict, Any, List

"""
Описание снаряжения и предметов для UI инвентаря (ACS).

Здесь храним только данные (id, имя, статы, путь к иконке),
а создание `InventoryItem` и работа со слотами остаются в `inventory.py`.
"""


# Список предметов, которые появляются в ACS‑инвентаре по умолчанию
DEFAULT_ACS_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "health_potion",
        "name": "Зелье здоровья",
        "description": "Восстанавливает 50 здоровья",
        "type": "consumable",
        "image_path": "Game/assets/images/items/health_potion.png",
        "stats": {"health_restore": 50},
        "max_stack": 10,
        "rarity": "common",
    },
    {
        "id": "mana_potion",
        "name": "Зелье маны",
        "description": "Восстанавливает 30 маны",
        "type": "consumable",
        "image_path": "Game/assets/images/items/mana_potion.png",
        "stats": {"mana_restore": 30},
        "max_stack": 10,
        "rarity": "common",
    },
    {
        "id": "iron_sword",
        "name": "Железный меч",
        "description": "Простой железный меч",
        "type": "weapon",
        "image_path": "Game/assets/images/items/iron_sword.png",
        "stats": {"attack": 10},
        "max_stack": 1,
        "rarity": "uncommon",
    },
    {
        "id": "leather_helmet",
        "name": "Кожаный шлем",
        "description": "Базовая защита головы",
        "type": "armor",
        "image_path": "Game/assets/images/items/leather_helmet.png",
        "stats": {"defense": 5},
        "max_stack": 1,
        "rarity": "common",
    },
    {
        "id": "gold_ring",
        "name": "Золотое кольцо",
        "description": "Увеличивает удачу",
        "type": "accessory",
        "image_path": "Game/assets/images/items/gold_ring.png",
        "stats": {"luck": 5},
        "max_stack": 1,
        "rarity": "rare",
    },
    # --- Реальные предметы, добавленные пользователем ---
    {
        "id": "steel_dagger",
        "name": "Стальной кинжал",
        "description": "Лёгкий стальной кинжал, быстрый и точный.",
        "type": "weapon",
        "image_path": "Game/assets/Images/game/playerData/steel_dagger.jpg",
        "stats": {"attack": 8, "attack_speed_bonus": 0.1},
        "max_stack": 1,
        "rarity": "uncommon",
    },
    {
        "id": "small_round_sun_shield",
        "name": "Малый круглый щит Солнца",
        "description": "Небольшой щит с символом Солнца, хорошо отражает удары.",
        "type": "shield",
        "image_path": "Game/assets/Images/game/playerData/small_round_sun_shield.jpg",
        "stats": {"defense": 12},
        "max_stack": 1,
        "rarity": "rare",
    },
    {
        "id": "steel_axe",
        "name": "Стальной топор",
        "description": "Тяжёлый стальной топор, наносящий мощные удары.",
        "type": "weapon",
        "image_path": "Game/assets/Images/game/playerData/steel_axe.jpg",
        "stats": {"attack": 15, "critical_chance_bonus": 2.0},
        "max_stack": 1,
        "rarity": "rare",
    },
    {
        "id": "steel_breastplate",
        "name": "Стальная кираса",
        "description": "Надёжная стальная кираса, значительно повышающая защиту.",
        "type": "armor",
        "image_path": "Game/assets/Images/game/playerData/steel_breastplate.jpg",
        "stats": {"defense": 20},
        "max_stack": 1,
        "rarity": "rare",
    },
    {
        "id": "robe_of_the_sun",
        "name": "Одеяние Солнца",
        "description": "Лёгкое магическое одеяние, усиливающее магию и ману.",
        "type": "armor",
        "image_path": "Game/assets/Images/game/playerData/robe_of_the_sun.jpg",
        "stats": {"defense": 8, "magic": 10, "max_mana_bonus": 30},
        "max_stack": 1,
        "rarity": "epic",
    },
    {
        "id": "bronze_helmet",
        "name": "Бронзовый шлем",
        "description": "Простой бронзовый шлем, дающий базовую защиту головы.",
        "type": "armor",
        "image_path": "Game/assets/Images/game/playerData/bronze_helmet.jpg",
        "stats": {"defense": 6},
        "max_stack": 1,
        "rarity": "common",
    },
    {
        "id": "golden_helmet",
        "name": "Золотой шлем",
        "description": "Украшенный золотом шлем, символ статуса и силы.",
        "type": "armor",
        "image_path": "Game/assets/Images/game/playerData/golden_helmet.jpg",
        "stats": {"defense": 10, "luck": 3},
        "max_stack": 1,
        "rarity": "epic",
    },
]


# Простая база данных предметов по id
ITEM_DATABASE: Dict[str, Dict[str, Any]] = {
    item["id"]: item for item in DEFAULT_ACS_ITEMS
}

