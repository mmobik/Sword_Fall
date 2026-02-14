import random
import math

class Distribution_system:
    """Система распределения шансов"""
    
    def __init__(self):
        pass

    def roll_drop(self, chance: float) -> bool:
        """Случайное выпадение шанса, равномерно распределенное от 0 до 1"""
        chance = max(0.0, min(1.0, chance))
        return random.random() < chance
    
    # --- Равномерное распределение ---
    def uniform_expectation(self, min_value: int, max_value: int) -> float:
        """Математическое ожидание для равномерного распределения"""
        return (min_value + max_value) / 2
    
    def uniform_std(self, min_value: int, max_value: int) -> float:
        """Стандартное отклонение для равномерного распределения"""
        return math.sqrt((max_value - min_value) ** 2 / 12)
    
    def uniform_variance(self, min_value: int, max_value: int) -> float:
        """Дисперсия для равномерного распределения"""
        std = self.uniform_std(min_value, max_value)
        return std ** 2
    
    # --- Нормальное распределение ---
    def normal_expectation(self, mean: float) -> float:
        """
        Математическое ожидание для нормального распределения
        E = μ (параметр распределения)
        """
        return mean
    
    def normal_variance(self, std: float) -> float:
        """Дисперсия для нормального распределения (Var = σ²)"""
        return std ** 2
    
    def normal_std(self, variance: float) -> float:
        """Стандартное отклонение для нормального распределения (σ = √Var)"""
        return math.sqrt(variance)
    
    def normal_parameters_from_bounds(self, min_value: int, max_value: int):
        """
        Получить параметры нормального распределения из границ
        Предполагаем, что 99.7% значений лежат в [min, max]
        """
        mean = (min_value + max_value) / 2
        std = (max_value - min_value) / 6
        return mean, std
    
    # --- Методы дропа ---
    def drop_gold(self, min_value: int, max_value: int, distribution: str = "uniform") -> int:
        """Выпадения золота с возможность выбора распределения"""
        if distribution == "uniform":
            return random.randint(min_value, max_value)
        
        elif distribution == "normal":
            mean, std = self.normal_parameters_from_bounds(min_value, max_value)
            value = int(random.normalvariate(mean, std))
            return max(min_value, min(max_value, value))
        
        else:
            raise ValueError(f"Неизвестное распределение: {distribution}")

ds = Distribution_system()
