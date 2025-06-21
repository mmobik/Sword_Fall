"""
Тестовый скрипт для демонстрации системы характеристик игрока.
Запустите игру и используйте следующие клавиши для тестирования:

- H: Получить урон (10 HP)
- J: Восстановить здоровье (20 HP)
- K: Использовать выносливость (30 SP)
- L: Получить опыт (50 XP)
- R: Воскреситься (если мертв)
"""

import pygame
from level.player_stats import PlayerStats, StatModifier
from UI.player_ui import PlayerUI
from core.config import config

def test_stats_system():
    """Тестирует систему характеристик."""
    pygame.init()
    
    # Создаем экран
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест системы характеристик")
    
    # Создаем характеристики игрока
    player_stats = PlayerStats(max_health=100.0, max_stamina=100.0)
    
    # Создаем UI
    player_ui = PlayerUI(screen, player_stats)
    
    clock = pygame.time.Clock()
    running = True
    
    print("Тест системы характеристик")
    print("Клавиши:")
    print("H - Получить урон (10 HP)")
    print("J - Восстановить здоровье (20 HP)")
    print("K - Использовать выносливость (30 SP)")
    print("L - Получить опыт (50 XP)")
    print("R - Воскреситься")
    print("ESC - Выход")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_h:
                    damage = player_stats.take_damage(10.0)
                    print(f"Получен урон: {damage} HP")
                elif event.key == pygame.K_j:
                    heal = player_stats.heal(20.0)
                    print(f"Восстановлено: {heal} HP")
                elif event.key == pygame.K_k:
                    if player_stats.use_stamina(30.0):
                        print("Использовано 30 SP")
                    else:
                        print("Недостаточно выносливости!")
                elif event.key == pygame.K_l:
                    levels = player_stats.add_experience(50.0)
                    print(f"Получено 50 XP, уровней: {levels}")
                elif event.key == pygame.K_r:
                    if not player_stats.is_alive():
                        player_stats.health.revive()
                        print("Игрок воскрешен!")
                    else:
                        print("Игрок жив!")
        
        # Обновляем характеристики
        player_stats.update(dt)
        player_ui.update(dt)
        
        # Отрисовываем
        screen.fill((0, 0, 0))
        player_ui.draw()
        
        # Отрисовываем экран смерти если игрок мертв
        if not player_stats.is_alive():
            player_ui.draw_death_screen()
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_stats_system() 