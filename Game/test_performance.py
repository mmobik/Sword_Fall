"""
Скрипт для тестирования производительности игры.
Сравнивает FPS с включенной и выключенной отладкой.
"""

import time
import pygame
from core.config import config
from level.player_stats import PlayerStats
from UI.player_ui import PlayerUI

def test_performance():
    """Тестирует производительность с разными настройками отладки."""
    pygame.init()
    
    # Создаем экран
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Тест производительности")
    
    # Создаем характеристики игрока
    player_stats = PlayerStats(max_health=100.0, max_stamina=100.0)
    
    # Создаем UI
    player_ui = PlayerUI(screen, player_stats)
    
    clock = pygame.time.Clock()
    
    print("Тест производительности")
    print("=" * 50)
    
    # Тест с отладкой ВКЛЮЧЕНА
    config.DEBUG_MODE = True
    print("Тест с DEBUG_MODE = True")
    
    start_time = time.time()
    frame_count = 0
    test_duration = 5.0  # 5 секунд
    
    while time.time() - start_time < test_duration:
        dt = clock.tick(60) / 1000.0
        
        # Симулируем движение игрока (расход выносливости)
        player_stats.use_stamina(0.1)
        player_stats.heal(0.05)
        
        # Обновляем характеристики
        player_stats.update(dt)
        player_ui.update(dt)
        
        # Отрисовываем
        screen.fill((0, 0, 0))
        player_ui.draw()
        pygame.display.flip()
        
        frame_count += 1
        
        # Обрабатываем события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
    
    fps_with_debug = frame_count / test_duration
    print(f"FPS с отладкой: {fps_with_debug:.1f}")
    
    # Тест с отладкой ВЫКЛЮЧЕНА
    config.DEBUG_MODE = False
    print("\nТест с DEBUG_MODE = False")
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < test_duration:
        dt = clock.tick(60) / 1000.0
        
        # Симулируем движение игрока (расход выносливости)
        player_stats.use_stamina(0.1)
        player_stats.heal(0.05)
        
        # Обновляем характеристики
        player_stats.update(dt)
        player_ui.update(dt)
        
        # Отрисовываем
        screen.fill((0, 0, 0))
        player_ui.draw()
        pygame.display.flip()
        
        frame_count += 1
        
        # Обрабатываем события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
    
    fps_without_debug = frame_count / test_duration
    print(f"FPS без отладки: {fps_without_debug:.1f}")
    
    # Результаты
    print("\nРезультаты:")
    print("=" * 50)
    print(f"FPS с отладкой:     {fps_with_debug:.1f}")
    print(f"FPS без отладки:    {fps_without_debug:.1f}")
    print(f"Улучшение:          {((fps_without_debug - fps_with_debug) / fps_with_debug * 100):.1f}%")
    
    pygame.quit()

if __name__ == "__main__":
    test_performance() 