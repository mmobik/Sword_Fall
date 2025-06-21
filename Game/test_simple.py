"""
Простой тест системы характеристик.
Запустите этот скрипт для проверки работы системы.
"""

from level.player_stats import PlayerStats, StatModifier

def test_basic_stats():
    """Тестирует базовые функции системы характеристик."""
    print("=== Тест системы характеристик ===")
    
    # Создаем характеристики
    stats = PlayerStats(max_health=100.0, max_stamina=100.0)
    
    print(f"Начальное состояние:")
    print(f"  Здоровье: {stats.health.get_display_value()}")
    print(f"  Выносливость: {stats.stamina.get_display_value()}")
    print(f"  Опыт: {stats.experience.get_display_value()}")
    print(f"  Жив: {stats.is_alive()}")
    
    # Тест получения урона
    print("\n=== Тест урона ===")
    damage = stats.take_damage(25.0)
    print(f"Получен урон: {damage} HP")
    print(f"Здоровье после урона: {stats.health.get_display_value()}")
    
    # Тест восстановления
    print("\n=== Тест восстановления ===")
    heal = stats.heal(15.0)
    print(f"Восстановлено: {heal} HP")
    print(f"Здоровье после лечения: {stats.health.get_display_value()}")
    
    # Тест выносливости
    print("\n=== Тест выносливости ===")
    if stats.use_stamina(30.0):
        print("Использовано 30 SP")
    else:
        print("Недостаточно выносливости!")
    print(f"Выносливость: {stats.stamina.get_display_value()}")
    
    # Тест опыта
    print("\n=== Тест опыта ===")
    levels = stats.add_experience(50.0)
    print(f"Получено 50 XP, уровней: {levels}")
    print(f"Опыт: {stats.experience.get_display_value()}")
    
    # Тест смерти
    print("\n=== Тест смерти ===")
    damage = stats.take_damage(100.0)
    print(f"Получен смертельный урон: {damage} HP")
    print(f"Жив: {stats.is_alive()}")
    print(f"Здоровье: {stats.health.get_display_value()}")
    
    # Тест воскрешения
    print("\n=== Тест воскрешения ===")
    stats.health.revive()
    print(f"Воскрешен! Жив: {stats.is_alive()}")
    print(f"Здоровье: {stats.health.get_display_value()}")
    
    # Тест модификаторов
    print("\n=== Тест модификаторов ===")
    health_bonus = StatModifier(20.0, duration=5.0, source="potion")
    stats.health.add_modifier(health_bonus)
    print(f"Добавлен временный бонус +20 HP на 5 секунд")
    print(f"Здоровье с бонусом: {stats.health.get_display_value()}")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_basic_stats() 