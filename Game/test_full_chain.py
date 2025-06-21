"""
Тест всей цепочки: урон -> статистика -> UI
Проверяет, что изменения правильно передаются через все компоненты.
"""

from level.player_stats import PlayerStats
from level.player import Player
from UI.player_ui import PlayerUI
import pygame
from core.config import config

def test_full_chain():
    """Тестирует всю цепочку передачи изменений."""
    pygame.init()
    
    # Создаем экран
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест полной цепочки")
    
    # Включаем режим отладки
    config.set_debug_mode(True)
    
    print("=== Тест полной цепочки ===")
    
    # Создаем характеристики
    player_stats = PlayerStats(max_health=100.0, max_stamina=100.0)
    print(f"1. Созданы характеристики: HP={player_stats.health.current_value}/{player_stats.health.max_value}")
    
    # Создаем UI
    player_ui = PlayerUI(screen, player_stats)
    print(f"2. Создан UI и подписан на изменения")
    
    # Создаем игрока
    player = Player(100, 100, None)
    player.stats = player_stats  # Привязываем статистику к игроку
    print(f"3. Создан игрок с привязанной статистикой")
    
    # Тест получения урона через игрока
    print("\n=== Тест урона через игрока ===")
    damage = player.take_damage(25.0)
    print(f"Игрок получил урон: {damage} HP")
    print(f"Текущее здоровье: {player.stats.health.get_display_value()}")
    
    # Тест восстановления через игрока
    print("\n=== Тест восстановления через игрока ===")
    heal = player.heal(15.0)
    print(f"Игрок восстановился: {heal} HP")
    print(f"Текущее здоровья: {player.stats.health.get_display_value()}")
    
    # Тест выносливости через игрока
    print("\n=== Тест выносливости через игрока ===")
    if player.stats.use_stamina(30.0):
        print("Использовано 30 SP")
    else:
        print("Недостаточно выносливости!")
    print(f"Текущая выносливость: {player.stats.stamina.get_display_value()}")
    
    # Тест опыта через игрока
    print("\n=== Тест опыта через игрока ===")
    levels = player.add_experience(50.0)
    print(f"Получено 50 XP, уровней: {levels}")
    print(f"Текущий опыт: {player.stats.experience.get_display_value()}")
    
    print("\n=== Тест завершен ===")
    print("Проверьте, что в консоли появились сообщения:")
    print("- [UI DEBUG] UI создан и подписан на изменения характеристик")
    print("- [STATS DEBUG] Добавление наблюдателя")
    print("- [PLAYER DEBUG] Получение урона")
    print("- [STATS DEBUG] Уведомление наблюдателей")
    print("- [UI DEBUG] Изменение характеристики")

if __name__ == "__main__":
    test_full_chain() 