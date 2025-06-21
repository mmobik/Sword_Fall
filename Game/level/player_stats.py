"""
Система характеристик игрока.
Следует принципам SOLID:
- Single Responsibility: каждый класс отвечает за одну характеристику
- Open/Closed: легко расширяется новыми характеристиками
- Liskov Substitution: все характеристики взаимозаменяемы
- Interface Segregation: четкие интерфейсы для каждой характеристики
- Dependency Inversion: зависимости от абстракций
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from dataclasses import dataclass
import pygame


class StatObserver(ABC):
    """Абстрактный наблюдатель за изменениями характеристик."""
    
    @abstractmethod
    def on_stat_changed(self, stat_name: str, old_value: float, new_value: float):
        """Вызывается при изменении характеристики."""
        pass


class StatModifier:
    """Модификатор характеристики."""
    
    def __init__(self, value: float, duration: Optional[float] = None, 
                 source: str = "unknown", is_percentage: bool = False):
        self.value = value
        self.duration = duration
        self.source = source
        self.is_percentage = is_percentage
        self.time_remaining = duration if duration else None
    
    def update(self, dt: float) -> bool:
        """Обновляет модификатор. Возвращает True если модификатор активен."""
        if self.duration is not None and self.time_remaining is not None:
            self.time_remaining -= dt
            return self.time_remaining > 0
        return True


class BaseStat(ABC):
    """Базовая абстрактная характеристика."""
    
    def __init__(self, name: str, base_value: float, max_value: Optional[float] = None):
        self.name = name
        self.base_value = base_value
        self.current_value = base_value
        self.max_value = max_value or base_value
        self.modifiers: list[StatModifier] = []
        self.observers: list[StatObserver] = []
    
    def add_observer(self, observer: StatObserver):
        """Добавляет наблюдателя."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: StatObserver):
        """Удаляет наблюдателя."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, old_value: float, new_value: float):
        """Уведомляет всех наблюдателей об изменении."""
        for observer in self.observers:
            observer.on_stat_changed(self.name, old_value, new_value)
    
    def add_modifier(self, modifier: StatModifier):
        """Добавляет модификатор."""
        self.modifiers.append(modifier)
        self._recalculate_value()
    
    def remove_modifier(self, source: str):
        """Удаляет модификаторы по источнику."""
        self.modifiers = [m for m in self.modifiers if m.source != source]
        self._recalculate_value()
    
    def update(self, dt: float):
        """Обновляет характеристику."""
        # Удаляем истекшие модификаторы
        self.modifiers = [m for m in self.modifiers if m.update(dt)]
        self._recalculate_value()
    
    def _recalculate_value(self):
        """Пересчитывает значение характеристики."""
        old_value = self.current_value
        # Базовое значение
        total_value = self.base_value
        total_percentage = 0.0
        # Применяем модификаторы
        for modifier in self.modifiers:
            if modifier.is_percentage:
                total_percentage += modifier.value
            else:
                total_value += modifier.value
        # Применяем процентные модификаторы
        total_value *= (1 + total_percentage)
        # Пересчитываем max_value
        self.max_value = total_value
        # Ограничиваем только сверху
        if self.current_value > self.max_value:
            self.current_value = self.max_value
        # Уведомляем наблюдателей
        if abs(old_value - self.current_value) > 0.001:
            self._notify_observers(old_value, self.current_value)
    
    @abstractmethod
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        pass


class HealthStat(BaseStat):
    """Характеристика здоровья."""
    
    def __init__(self, max_health: float):
        super().__init__("health", max_health, max_health)
        self.is_alive = True
    
    def take_damage(self, damage: float) -> float:
        """Получает урон. Возвращает фактический урон."""
        from core.config import config
        if config.DEBUG_MODE:
            print(f"[HEALTH DEBUG] Попытка получить урон: {damage:.1f} HP (текущее: {self.current_value:.1f})")
        
        if not self.is_alive:
            if config.DEBUG_MODE:
                print(f"[HEALTH DEBUG] Игрок мертв, урон не применяется")
            return 0.0
        
        old_value = self.current_value
        actual_damage = min(damage, self.current_value)
        self.current_value -= actual_damage
        
        if self.current_value <= 0:
            self.current_value = 0
            self.is_alive = False
        
        if config.DEBUG_MODE:
            print(f"[HEALTH DEBUG] Урон применен: {old_value:.1f} -> {self.current_value:.1f} (фактический урон: {actual_damage:.1f})")
        
        self._notify_observers(old_value, self.current_value)
        return actual_damage
    
    def heal(self, amount: float) -> float:
        """Восстанавливает здоровье. Возвращает фактическое восстановление."""
        if not self.is_alive:
            return 0.0
        
        old_value = self.current_value
        actual_heal = min(amount, self.max_value - self.current_value)
        self.current_value += actual_heal
        
        self._notify_observers(old_value, self.current_value)
        return actual_heal
    
    def revive(self, health_percentage: float = 0.5):
        """Воскрешает игрока с указанным процентом здоровья."""
        self.is_alive = True
        self.current_value = self.max_value * health_percentage
        self._notify_observers(0, self.current_value)
    
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"{int(self.current_value)}/{int(self.max_value)}"
    
    def get_health_percentage(self) -> float:
        """Возвращает процент здоровья."""
        return self.current_value / self.max_value if self.max_value > 0 else 0.0


class StaminaStat(BaseStat):
    """Характеристика выносливости."""
    
    def __init__(self, max_stamina: float, regen_rate: float = 10.0):
        super().__init__("stamina", max_stamina, max_stamina)
        self.regen_rate = regen_rate
        self.is_exhausted = False
    
    def use_stamina(self, amount: float) -> bool:
        """Использует выносливость. Возвращает True если достаточно."""
        from core.config import config
        if config.DEBUG_MODE:
            print(f"[STAMINA DEBUG] Попытка использовать {amount:.2f} SP (текущее: {self.current_value:.1f})")
        
        if self.current_value < amount:
            if config.DEBUG_MODE:
                print(f"[STAMINA DEBUG] Недостаточно выносливости!")
            return False
        
        old_value = self.current_value
        self.current_value -= amount
        self.is_exhausted = self.current_value <= 0
        
        if config.DEBUG_MODE:
            print(f"[STAMINA DEBUG] Выносливость использована: {old_value:.1f} -> {self.current_value:.1f}")
        
        self._notify_observers(old_value, self.current_value)
        return True
    
    def update(self, dt: float):
        """Обновляет выносливость с регенерацией."""
        super().update(dt)
        
        # Регенерация выносливости
        if self.current_value < self.max_value and not self.is_exhausted:
            old_value = self.current_value
            self.current_value = min(self.max_value, self.current_value + self.regen_rate * dt)
            self._notify_observers(old_value, self.current_value)
    
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"{int(self.current_value)}/{int(self.max_value)}"
    
    def get_stamina_percentage(self) -> float:
        """Возвращает процент выносливости."""
        return self.current_value / self.max_value if self.max_value > 0 else 0.0


class ExperienceStat(BaseStat):
    """Характеристика опыта."""
    
    def __init__(self, level: int = 1, experience: float = 0.0):
        super().__init__("experience", experience)
        self.level = level
        self.experience_to_next = self._calculate_exp_to_next()
    
    def add_experience(self, amount: float) -> int:
        """Добавляет опыт. Возвращает количество полученных уровней."""
        old_value = self.current_value
        self.current_value += amount
        
        levels_gained = 0
        while self.current_value >= self.experience_to_next:
            self.current_value -= self.experience_to_next
            self.level += 1
            levels_gained += 1
            self.experience_to_next = self._calculate_exp_to_next()
        
        self._notify_observers(old_value, self.current_value)
        return levels_gained
    
    def _calculate_exp_to_next(self) -> float:
        """Рассчитывает опыт для следующего уровня."""
        return self.level * 100  # Простая формула
    
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"Level {self.level} ({int(self.current_value)}/{int(self.experience_to_next)} XP)"


class PlayerStats:
    """Управляет всеми характеристиками игрока."""
    
    def __init__(self, max_health: float = 100.0, max_stamina: float = 100.0, game=None):
        self.health = HealthStat(max_health)
        self.stamina = StaminaStat(max_stamina)
        self.experience = ExperienceStat()
        
        # Сохраняем ссылку на game, если передана
        self.game = game
        # Словарь для быстрого доступа к характеристикам
        self.stats = {
            "health": self.health,
            "stamina": self.stamina,
            "experience": self.experience
        }
    
    def add_observer(self, observer: StatObserver):
        """Добавляет наблюдателя ко всем характеристикам."""
        from core.config import config
        if config.DEBUG_MODE:
            print(f"[STATS DEBUG] Добавление наблюдателя: {type(observer).__name__}")
        
        for stat in self.stats.values():
            stat.add_observer(observer)
    
    def remove_observer(self, observer: StatObserver):
        """Удаляет наблюдателя со всех характеристик."""
        for stat in self.stats.values():
            stat.remove_observer(observer)
    
    def update(self, dt: float):
        """Обновляет все характеристики."""
        for stat in self.stats.values():
            stat.update(dt)
    
    def get_stat(self, stat_name: str) -> Optional[BaseStat]:
        """Возвращает характеристику по имени."""
        return self.stats.get(stat_name)
    
    def is_alive(self) -> bool:
        """Проверяет, жив ли игрок."""
        return self.health.is_alive
    
    def take_damage(self, damage: float) -> float:
        """Игрок получает урон."""
        return self.health.take_damage(damage)
    
    def heal(self, amount: float) -> float:
        """Игрок восстанавливается."""
        return self.health.heal(amount)
    
    def use_stamina(self, amount: float) -> bool:
        """Игрок использует выносливость."""
        return self.stamina.use_stamina(amount)
    
    def add_experience(self, amount: float) -> int:
        """Игрок получает опыт."""
        return self.experience.add_experience(amount) 