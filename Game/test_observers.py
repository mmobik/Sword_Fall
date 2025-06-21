"""
Тест системы наблюдателей для характеристик.
Проверяет, что UI получает уведомления об изменениях.
"""

from level.player_stats import PlayerStats
from UI.player_ui import PlayerUI
import pygame
from core.config import config

def test_observers():
    """Тестирует систему наблюдателей."""
    pygame.init()
    
    # Создаем экран
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест наблюдателей")
    
    # Включаем режим отладки
    config.set_debug_mode(True)
    
    # Создаем характеристики
    player_stats = PlayerStats(max_health=100.0, max_stamina=100.0)
    
    # Создаем UI
    player_ui = PlayerUI(screen, player_stats)
    
    print("=== Тест системы наблюдателей ===")
    print("Начальное состояние:")
    print(f"  Здоровье: {player_stats.health.get_display_value()}")
    
    # Тест получения урона
    print("\n=== Тест урона ===")
    damage = player_stats.take_damage(25.0)
    print(f"Получен урон: {damage} HP")
    print(f"Здоровье после урона: {player_stats.health.get_display_value()}")
    
    # Тест восстановления
    print("\n=== Тест восстановления ===")
    heal = player_stats.heal(15.0)
    print(f"Восстановлено: {heal} HP")
    print(f"Здоровье после лечения: {player_stats.health.get_display_value()}")
    
    # Тест выносливости
    print("\n=== Тест выносливости ===")
    if player_stats.use_stamina(30.0):
        print("Использовано 30 SP")
    else:
        print("Недостаточно выносливости!")
    print(f"Выносливость: {player_stats.stamina.get_display_value()}")
    
    print("\n=== Тест завершен ===")
    print("Проверьте, что в консоли появились сообщения:")
    print("- [STATS DEBUG] Добавление наблюдателя")
    print("- [STATS DEBUG] Уведомление наблюдателей")
    print("- [UI DEBUG] Изменение характеристики")

if __name__ == "__main__":
    test_observers() 