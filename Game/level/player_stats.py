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
from typing import Optional, Dict, Any
import pygame
import math


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
    
    def set_max_health(self, new_max_health: float):
        """Устанавливает новое максимальное здоровье."""
        old_max = self.max_value
        old_current = self.current_value

        # Сохраняем процент текущего здоровья
        health_percentage = old_current / old_max if old_max > 0 else 1.0

        # Обновляем базовое значение, чтобы BaseStat._recalculate_value()
        # не откатывало max_value обратно к старому base_value
        self.base_value = new_max_health

        # Пересчитываем максимум с учетом модификаторов
        self._recalculate_value()

        # Обновляем текущее здоровье, сохраняя процент
        new_current = self.max_value * health_percentage
        if abs(new_current - self.current_value) > 0.001:
            self.current_value = new_current
            self._notify_observers(old_current, self.current_value)


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
    
    def set_max_stamina(self, new_max_stamina: float):
        """Устанавливает новое максимальное количество выносливости."""
        old_max = self.max_value
        old_current = self.current_value

        # Сохраняем процент текущей выносливости
        stamina_percentage = old_current / old_max if old_max > 0 else 1.0

        # Обновляем базовое значение, чтобы пересчет учитывал новый максимум
        self.base_value = new_max_stamina

        # Пересчитываем максимум с учетом модификаторов
        self._recalculate_value()

        # Обновляем текущее значение, сохраняя процент
        new_current = self.max_value * stamina_percentage
        if abs(new_current - self.current_value) > 0.001:
            self.current_value = new_current
            self._notify_observers(old_current, self.current_value)

        print(f"[STAMINA] Макс. выносливость изменена: {old_max} -> {self.max_value}")
        print(f"[STAMINA] Текущая выносливость: {old_current} -> {self.current_value}")


class ManaStat(BaseStat):
    """Характеристика маны."""
    
    def __init__(self, max_mana: float, regen_rate: float = 5.0):
        super().__init__("mana", max_mana, max_mana)
        self.regen_rate = regen_rate
    
    def use_mana(self, amount: float) -> bool:
        """Использует ману. Возвращает True если достаточно."""
        from core.config import config
        if config.DEBUG_MODE:
            print(f"[MANA DEBUG] Попытка использовать {amount:.2f} MP (текущее: {self.current_value:.1f})")
        
        if self.current_value < amount:
            if config.DEBUG_MODE:
                print(f"[MANA DEBUG] Недостаточно маны!")
            return False
        
        old_value = self.current_value
        self.current_value -= amount
        
        if config.DEBUG_MODE:
            print(f"[MANA DEBUG] Мана использована: {old_value:.1f} -> {self.current_value:.1f}")
        
        self._notify_observers(old_value, self.current_value)
        return True
    
    def update(self, dt: float):
        """Обновляет ману с регенерацией."""
        super().update(dt)
        
        # Регенерация маны
        if self.current_value < self.max_value:
            old_value = self.current_value
            self.current_value = min(self.max_value, self.current_value + self.regen_rate * dt)
            self._notify_observers(old_value, self.current_value)
    
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"{int(self.current_value)}/{int(self.max_value)}"
    
    def get_mana_percentage(self) -> float:
        """Возвращает процент маны."""
        return self.current_value / self.max_value if self.max_value > 0 else 0.0
    
    def set_max_mana(self, new_max_mana: float):
        """Устанавливает новое максимальное количество маны."""
        old_max = self.max_value
        old_current = self.current_value

        # Сохраняем процент текущей маны
        mana_percentage = old_current / old_max if old_max > 0 else 1.0

        # Обновляем базовое значение, чтобы пересчет учитывал новый максимум
        self.base_value = new_max_mana

        # Пересчитываем максимум с учетом модификаторов
        self._recalculate_value()

        # Обновляем текущее значение, сохраняя процент
        new_current = self.max_value * mana_percentage
        if abs(new_current - self.current_value) > 0.001:
            self.current_value = new_current
            self._notify_observers(old_current, self.current_value)

        print(f"[MANA] Макс. мана изменена: {old_max} -> {self.max_value}")
        print(f"[MANA] Текущая мана: {old_current} -> {self.current_value}")


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


class DamageStat(BaseStat):
    """Характеристика урона."""
    
    def __init__(self, base_damage: float = 10.0):
        super().__init__("damage", base_damage)
        
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"{int(self.current_value)}"
    
    def get_base_damage(self) -> float:
        """Возвращает базовый урон."""
        return self.base_value
    
    def get_total_damage(self) -> float:
        """Возвращает общий урон с модификаторами."""
        return self.current_value


class DefenseStat(BaseStat):
    """Характеристика защиты."""
    
    def __init__(self, base_defense: float = 5.0):
        super().__init__("defense", base_defense)
        
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"{int(self.current_value)}"


class MagicStat(BaseStat):
    """Характеристика магии."""
    
    def __init__(self, base_magic: float = 0.0):
        super().__init__("magic", base_magic)
        
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"{int(self.current_value)}"


class LuckStat(BaseStat):
    """Характеристика удачи."""
    
    def __init__(self, base_luck: float = 1.0):
        super().__init__("luck", base_luck)
        
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        return f"{int(self.current_value)}"


class Attribute:
    """Класс для основных атрибутов игрока."""
    
    def __init__(self, name: str, display_name: str, base_value: int = 10, 
                 description: str = "", short_name: str = "", category: str = "physical"):
        self.name = name
        self.display_name = display_name
        self.short_name = short_name or display_name[:3]
        self.base_value = base_value
        self.current_value = base_value
        self.description = description
        self.category = category
        self.modifiers = []  # Для временных бонусов
        
    def increase(self, amount: int = 1):
        """Увеличивает значение атрибута."""
        self.base_value += amount
        self.current_value += amount
        
    def add_modifier(self, value: int, duration: float = None, source: str = "unknown"):
        """Добавляет временный модификатор."""
        modifier = {"value": value, "duration": duration, "source": source, "time_remaining": duration}
        self.modifiers.append(modifier)
        self._recalculate()
        
    def remove_modifier(self, source: str):
        """Удаляет модификаторы по источнику."""
        self.modifiers = [m for m in self.modifiers if m["source"] != source]
        self._recalculate()
        
    def update(self, dt: float):
        """Обновляет временные модификаторы."""
        for modifier in self.modifiers[:]:
            if modifier["duration"] is not None:
                modifier["time_remaining"] -= dt
                if modifier["time_remaining"] <= 0:
                    self.modifiers.remove(modifier)
        self._recalculate()
        
    def _recalculate(self):
        """Пересчитывает текущее значение."""
        total = self.base_value
        for modifier in self.modifiers:
            total += modifier["value"]
        self.current_value = total
        
    def get_value(self) -> int:
        """Возвращает текущее значение."""
        return self.current_value
    
    def get_modifier(self) -> int:
        """Возвращает модификатор атрибута (значение - 10) / 2, округление в меньшую сторону."""
        return math.floor((self.current_value - 10) / 2)
    
    def get_display_value(self) -> str:
        """Возвращает значение для отображения."""
        modifier = self.get_modifier()
        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        return f"{self.display_name}: {self.current_value} ({modifier_str})"
    
    def get_tooltip(self) -> str:
        """Возвращает подсказку для атрибута."""
        modifier = self.get_modifier()
        modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        return f"{self.display_name} [{self.short_name}]: {self.current_value} (Модификатор: {modifier_str})\n{self.description}"


class PlayerStats:
    """Управляет всеми характеристиками игрока."""
    
    def __init__(self, max_health: float = 100.0, max_stamina: float = 100.0, max_mana: float = 50.0, game=None):
        # Основные характеристики
        self.health = HealthStat(max_health)
        self.stamina = StaminaStat(max_stamina)
        self.mana = ManaStat(max_mana)
        self.experience = ExperienceStat()
        self.damage = DamageStat()
        self.defense = DefenseStat()
        self.magic = MagicStat()
        self.luck = LuckStat()
        
        # === ФИЗИЧЕСКИЕ ХАРАКТЕРИСТИКИ ===
        self.attributes = {
            # Физические характеристики
            "strength": Attribute(
                "strength",
                "Сила",
                10,
                "Физическая мощь, мускульная сила. Влияет на урон в ближнем бою, "
                "проверки на подъем/слом, лазание, а также на максимальное здоровье.",
                "Сил",
                "physical",
            ),
            "dexterity": Attribute(
                "dexterity",
                "Ловкость",
                10,
                "Координация, реакция, проворство. Влияет на броню (Уклонение), инициативу, "
                "атаки дальнего боя, скрытность, ловкость рук.",
                "Лов",
                "physical",
            ),
            "constitution": Attribute(
                "constitution",
                "Телосложение",
                10,
                "Запас сил, стойкость, сопротивляемость усталости. Влияет на выносливость и "
                "сопротивления ядам/болезням, концентрацию при ранении.",
                "Вын",
                "physical",
            ),
            "speed": Attribute(
                "speed",
                "Скорость",
                10,
                "Быстрота движения, скорость бега, резкость рывков. Влияет на скорость "
                "передвижения, уклонение от зонных эффектов, количество атак.",
                "Спд",
                "physical",
            ),
            
            # === МЕНТАЛЬНЫЕ ХАРАКТЕРИСТИКИ ===
            "intelligence": Attribute(
                "intelligence",
                "Интеллект",
                10,
                "Логика, память, аналитические способности. Влияет на количество навыков, "
                "магические школы разума и на максимальный запас маны.",
                "Инт",
                "mental",
            ),
            "wisdom": Attribute(
                "wisdom", "Мудрость", 10,
                "Внимательность, интуиция, сила воли, восприятие. Влияет на сопротивление ментальным эффектам, магию жрецов/друидов, восприятие.",
                "Мдр", "mental"
            ),
            "charisma": Attribute(
                "charisma", "Харизма", 10,
                "Сила личности, обаяние, способность вести за собой. Влияет на магию бардов, торговлю, лидерство, запугивание.",
                "Хар", "mental"
            ),
            "willpower": Attribute(
                "willpower", "Воля", 10,
                "Психическая устойчивость, целеустремленность, самоконтроль. Влияет на сопротивление хаосу, панике, контролю разума.",
                "Вл", "mental"
            ),
            
            # === ДУХОВНЫЕ ХАРАКТЕРИСТИКИ ===
            "luck": Attribute(
                "luck", "Удача", 10,
                "Случайное везение. Влияет на переброс проваленных проверок, шанс критического попадания/уклонения.",
                "Удч", "spiritual"
            ),
            "perception": Attribute(
                "perception", "Восприятие", 10,
                "Острота чувств, внимание к деталям. Влияет на замечание скрытого, поиск ловушек, следопытство.",
                "Вс", "spiritual"
            ),
            "determination": Attribute(
                "determination", "Решительность", 10,
                "Способность действовать в стрессовой ситуации, хладнокровие. Влияет на инициативу в нестандартных ситуациях, проверки против страха.",
                "Рш", "spiritual"
            ),
            "spirit": Attribute(
                "spirit",
                "Дух",
                10,
                "Внутренняя энергия, связь с нематериальным миром, эссенция. Влияет на силу "
                "призывов и духовные эффекты.",
                "Дх",
                "spiritual",
            ),
            
            # === ПРОИЗВОДНЫЕ ХАРАКТЕРИСТИКИ ===
            "honor": Attribute(
                "honor", "Честь", 10,
                "Известность, социальный вес, достоинство. Влияет на отношение фракций, цены у торговцев, переговоры.",
                "Чст", "derived"
            ),
            "ingenuity": Attribute(
                "ingenuity", "Изворотливость", 10,
                "Смекалка, находчивость, способность использовать окружение. Влияет на импровизированные действия, использование подручных средств.",
                "Изв", "derived"
            ),
            "empathy": Attribute(
                "empathy", "Эмпатия", 10,
                "Понимание эмоций других, способность к сопереживанию и манипуляции. Влияет на проверки обмана, убеждения, понимания мотивов.",
                "Эп", "derived"
            )
        }
        
        # Дополнительные параметры
        self.carry_capacity = 50.0  # Грузоподъемность
        self.attack_speed = 1.0     # Скорость атаки
        self.stealth = 1.0          # Скрытность
        self.movement_speed = 1.0   # Скорость движения
        self.critical_chance = 5.0  # Шанс критического удара (%)
        self.dodge_chance = 10.0    # Шанс уклонения (%)
        
        # Система прокачки
        self.skill_points = 60  # Очки для прокачки атрибутов (15 для теста)
        self.attribute_points_per_level = 3  # Очков за уровень
        
        # Категории для ползунка
        self.attribute_categories = ["Физические", "Ментальные", "Духовные", "Производные"]
        
        # Сохраняем ссылку на game
        self.game = game
        
        # Словарь для быстрого доступа ко всем характеристикам
        self.stats = {
            "health": self.health,
            "stamina": self.stamina,
            "mana": self.mana,
            "experience": self.experience,
            "damage": self.damage,
            "defense": self.defense,
            "magic": self.magic,
            "luck_stat": self.luck,
        }
        
        # Пересчитываем характеристики на основе атрибутов
        self._recalculate_stats_from_attributes()
    
    def _recalculate_stats_from_attributes(self):
        """Пересчитывает характеристики на основе атрибутов."""
        # Получаем значения атрибутов
        strength = self.attributes["strength"].get_value()
        dexterity = self.attributes["dexterity"].get_value()
        constitution = self.attributes["constitution"].get_value()
        intelligence = self.attributes["intelligence"].get_value()
        luck_attr = self.attributes["luck"].get_value()
        perception = self.attributes["perception"].get_value()
        spirit = self.attributes["spirit"].get_value()
        
        # Получаем модификаторы
        strength_mod = self.attributes["strength"].get_modifier()
        dexterity_mod = self.attributes["dexterity"].get_modifier()
        constitution_mod = self.attributes["constitution"].get_modifier()
        intelligence_mod = self.attributes["intelligence"].get_modifier()
        luck_mod = self.attributes["luck"].get_modifier()
        perception_mod = self.attributes["perception"].get_modifier()
        
        # === ФИКСИРУЕМ ВЛИЯНИЕ НА ХАРАКТЕРИСТИКИ ===

        # 1. Здоровье: теперь зависит ОТ СИЛЫ
        # Каждый пункт силы дает +15 к максимальному здоровью
        new_health_max = 100 + (strength * 15)
        self.health.set_max_health(new_health_max)
        
        # 2. Мана: теперь зависит ОТ ИНТЕЛЛЕКТА
        # Каждый пункт интеллекта дает +10 к максимальной мане
        new_mana_max = 50 + (intelligence * 10)
        self.mana.set_max_mana(new_mana_max)
        
        # 3. Выносливость: зависит ОТ ТЕЛОСЛОЖЕНИЯ
        # Каждый пункт телосложения дает +10 к максимальной выносливости
        new_stamina_max = 100 + (constitution * 10)
        self.stamina.set_max_stamina(new_stamina_max)
        
        # 4. Урон: зависит ОТ СИЛЫ
        # База 10 + 1.5 за каждый пункт силы + 3 за каждый модификатор
        new_damage = 10 + (strength * 1.5) + (strength_mod * 3)
        self.damage.base_value = new_damage
        
        # 5. Защита: зависит ОТ ВОСПРИЯТИЯ
        # База 5 + 0.8 за каждый пункт восприятия + 2 за каждый модификатор
        new_defense = 5 + (perception * 0.8) + (perception_mod * 2)
        self.defense.base_value = new_defense
        
        # 6. Магия: зависит ОТ ИНТЕЛЛЕКТА
        # База 0 + 2 за каждый пункт интеллекта + 6 за каждый модификатор
        new_magic = max(0, intelligence * 2 + intelligence_mod * 6)
        self.magic.base_value = new_magic
        
        # 7. Удача: зависит от атрибута удачи
        new_luck = 1 + (luck_attr * 0.6)
        self.luck.base_value = new_luck
        
        # === ДОПОЛНИТЕЛЬНЫЕ ПАРАМЕТРЫ ===
        
        # Грузоподъемность: база 50 + 8 за каждый пункт силы
        self.carry_capacity = 50 + (strength * 8)
        
        # Скорость атаки: база 1.0 + 0.06 за модификатор ловкости
        self.attack_speed = max(0.5, 1.0 + (dexterity_mod * 0.06))
        
        # Скрытность: база 1.0 + 0.12 за модификатор ловкости
        self.stealth = 1.0 + (dexterity_mod * 0.12)
        
        # Скорость движения
        speed_mod = self.attributes["speed"].get_modifier()
        self.movement_speed = max(0.5, 1.0 + (speed_mod * 0.07))
        
        # Шанс крита
        self.critical_chance = max(0, 5 + (luck_mod * 3.5))
        
        # Шанс уклонения
        self.dodge_chance = max(0, 10 + (dexterity_mod * 2.5))
        
        # Пересчитываем ВСЕ характеристики (это важно!)
        for stat in self.stats.values():
            stat._recalculate_value()
        
        # Пересчитываем производные атрибуты
        charisma = self.attributes["charisma"].get_value()
        wisdom = self.attributes["wisdom"].get_value()
        
        # Честь
        honor_value = (charisma + wisdom) // 2
        self.attributes["honor"].base_value = honor_value
        
        # Изворотливость
        ingenuity_value = (intelligence + dexterity) // 2
        self.attributes["ingenuity"].base_value = ingenuity_value
        
        # Эмпатия
        empathy_value = (charisma + wisdom) // 2
        self.attributes["empathy"].base_value = empathy_value
        
        for attr_name in ["honor", "ingenuity", "empathy"]:
            self.attributes[attr_name]._recalculate()
        
        
    def add_experience(self, amount: float) -> int:
        """Игрок получает опыт."""
        old_level = self.experience.level
        levels_gained = self.experience.add_experience(amount)
        
        if levels_gained > 0:
            # Даем очки прокачки за каждый полученный уровень
            self.skill_points += levels_gained * self.attribute_points_per_level
            
            # Восстанавливаем здоровье, ману и выносливость при повышении уровня
            self.health.heal(self.health.max_value * 0.5)  # 50% от максимума
            self.mana.current_value = self.mana.max_value  # Полное восстановление
            self.stamina.current_value = self.stamina.max_value  # Полное восстановление
            
            print(f"[LEVEL UP] Уровень {old_level} → {self.experience.level}")
            print(f"[LEVEL UP] Получено очков прокачки: {levels_gained * self.attribute_points_per_level}")
            print(f"[LEVEL UP] Всего очков: {self.skill_points}")
            print(f"[LEVEL UP] Характеристики восстановлены!")
        
        return levels_gained
    
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
        """Обновляет все характеристики и атрибуты."""
        # Обновляем характеристики
        for stat in self.stats.values():
            stat.update(dt)
        
        # Обновляем атрибуты
        for attribute in self.attributes.values():
            attribute.update(dt)
    
    def get_stat(self, stat_name: str) -> Optional[BaseStat]:
        """Возвращает характеристику по имени."""
        return self.stats.get(stat_name)
    
    def get_attribute(self, attribute_name: str) -> Optional[Attribute]:
        """Возвращает атрибут по имени."""
        return self.attributes.get(attribute_name)
    
    def get_attributes_by_category(self, category: str) -> Dict[str, Attribute]:
        """Возвращает атрибуты по категории."""
        return {name: attr for name, attr in self.attributes.items() if attr.category == category}
    
    def is_alive(self) -> bool:
        """Проверяет, жив ли игрок."""
        return self.health.is_alive
    
    def take_damage(self, damage: float) -> float:
        """Игрок получает урон."""
        # Учитываем защиту и шанс уклонения
        import random
        dodge_roll = random.randint(1, 100)
        if dodge_roll <= self.dodge_chance:
            print(f"[COMBAT] Игрок уклонился от атаки!")
            return 0.0
        
        # Учитываем защиту
        actual_damage = max(0, damage - self.defense.current_value * 0.5)
        return self.health.take_damage(actual_damage)
    
    def heal(self, amount: float) -> float:
        """Игрок восстанавливается."""
        return self.health.heal(amount)
    
    def use_stamina(self, amount: float) -> bool:
        """Игрок использует выносливость."""
        return self.stamina.use_stamina(amount)
    
    def use_mana(self, amount: float) -> bool:
        """Игрок использует ману."""
        return self.mana.use_mana(amount)
    
    def get_all_stats_display(self) -> dict:
        """Возвращает все характеристики для отображения."""
        stats_display = {}
        
        # Основные характеристики
        for name, stat in self.stats.items():
            stats_display[name] = stat.get_display_value()
        
        # Дополнительные параметры
        stats_display["carry_capacity"] = f"{int(self.carry_capacity)} кг"
        stats_display["attack_speed"] = f"{self.attack_speed:.2f}"
        stats_display["stealth"] = f"{self.stealth:.1f}"
        stats_display["movement_speed"] = f"{self.movement_speed:.2f}"
        stats_display["critical_chance"] = f"{self.critical_chance:.1f}%"
        stats_display["dodge_chance"] = f"{self.dodge_chance:.1f}%"
        
        return stats_display
    
    def get_skill_points(self) -> int:
        """Возвращает количество очков прокачки."""
        return self.skill_points
    
    def spend_skill_point(self, attribute_name: str) -> bool:
        """Тратит очко прокачки на атрибут. Возвращает True если успешно."""
        if self.skill_points <= 0:
            return False
        
        if attribute_name in self.attributes:
            # ВАЖНО: У нас нет метода increase_attribute, нужно использовать другой метод
            # Увеличиваем атрибут
            old_value = self.attributes[attribute_name].get_value()
            self.attributes[attribute_name].increase(1)  # Используем метод increase у Attribute
            
            # Пересчитываем характеристики
            self._recalculate_stats_from_attributes()
            
            self.skill_points -= 1
            
            print(f"[STATS] Прокачан атрибут {self.attributes[attribute_name].display_name}: {old_value} -> {self.attributes[attribute_name].get_value()}")
            print(f"[STATS] Осталось очков: {self.skill_points}")
            
            return True
        
        return False
    
    def get_attribute_categories(self) -> list:
        """Возвращает список категорий атрибутов."""
        return self.attribute_categories