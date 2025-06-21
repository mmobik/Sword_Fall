import pygame
from level.spritesheet import SpriteSheet
from level.player_movement import PlayerMovementHandler
from level.player_stats import PlayerStats, StatModifier
from core.config import config


class Player(pygame.sprite.Sprite):
    """
    Класс, представляющий игрока.
    """

    def __init__(self, x: int, y: int, sound_manager=None, *groups) -> None:
        super().__init__(*groups)
        self.state_name = "idle_front"
        self.state = config.PLAYER_STATES[self.state_name]
        self.sprite_sheet = SpriteSheet(self.state["sprite_sheet"], *config.FRAME_SIZE)
        self.frames = self.state["frames"]
        self.animation_speed = self.state["animation_speed"]
        self.animation_time = 0
        self.current_frame = 0
        self.image = self._get_frame()

        # Основной rect спрайта (ставим в позицию "ног" персонажа)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)  # Базовая точка - ноги персонажа

        # Хитбокс рассчитываем относительно rect
        hitbox_width = config.PLAYER_HITBOX["WIDTH"]
        hitbox_height = config.PLAYER_HITBOX["HEIGHT"]

        # Позиция хитбокса:
        # X: центр спрайта + смещение
        # Y: от верха спрайта + смещение
        hitbox_x = self.rect.centerx - hitbox_width // 2 + config.PLAYER_HITBOX["X_OFFSET"]
        hitbox_y = self.rect.top + config.PLAYER_HITBOX["Y_OFFSET"]

        self.hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

        self.speed = config.PLAYER_SPEED
        self.movement_handler = PlayerMovementHandler(self)
        self.sound_manager = sound_manager
        self.is_walking = False

        # Система характеристик
        game = None
        if sound_manager and hasattr(sound_manager, 'game'):
            game = sound_manager.game
        self.stats = PlayerStats(max_health=100.0, max_stamina=100.0, game=game)
        
        # Настройки движения и выносливости
        self.stamina_cost_per_second = 10.0  # Расход выносливости в секунду при движении
        self.last_movement_time = 0.0
        
        # Эффекты и модификаторы
        self.active_effects = {}
        
        # Состояние игрока
        self.is_invulnerable = False
        self.invulnerability_duration = 0.1  # Уменьшено для тестирования (было 1.0)
        self.invulnerability_timer = 0.0
        
        # Индикаторы урона/лечения
        self.damage_indicators = []
        self.heal_indicators = []

        if config.DEBUG_MODE:
            print(f"Игрок создан: rect={self.rect}, hitbox={self.hitbox}")
            print(f"Смещение хитбокса: X={config.PLAYER_HITBOX['X_OFFSET']}, Y={config.PLAYER_HITBOX['Y_OFFSET']}")

    def _get_frame(self):
        if not hasattr(self, 'sprite_sheet') or not self.sprite_sheet:
            if config.DEBUG_MODE:
                print(f"Ошибка: спрайт-лист не загружен для состояния {self.state_name}")
            return pygame.Surface(config.FRAME_SIZE, pygame.SRCALPHA)

        x, y = self.frames[self.current_frame]
        frame = self.sprite_sheet.get_image(x, y, *config.FRAME_SIZE)
        if not frame:
            frame = pygame.Surface((64, 64), pygame.SRCALPHA)
            frame.fill((255, 0, 0))  # Красный квадрат\

        if frame:
            return pygame.transform.flip(frame, self.state.get("flip", False), False)
        return pygame.Surface(config.FRAME_SIZE, pygame.SRCALPHA)

    def set_state(self, state_name):
        if state_name == self.state_name:
            return
        if state_name in config.PLAYER_STATES:
            if config.DEBUG_MODE:
                print(f"Установка состояния: {state_name}")
            self.state_name = state_name
            self.state = config.PLAYER_STATES[self.state_name]
            self.sprite_sheet = SpriteSheet(self.state["sprite_sheet"], *config.FRAME_SIZE)
            self.frames = self.state["frames"]
            self.animation_speed = self.state["animation_speed"]
            self.animation_time = 0
            self.current_frame = 0
            self.image = self._get_frame()
            if config.DEBUG_MODE:
                print(f"Новое состояние установлено: {state_name}, кадров: {len(self.frames)}")
        else:
            if config.DEBUG_MODE:
                print(f"Ошибка: состояние {state_name} не найдено в конфигурации")

    def update(self, dt, level_width, level_height, collision_objects):
        # Обновляем характеристики
        self.stats.update(dt)
        
        # Обновляем неуязвимость
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
        
        # Сначала двигаем hitbox
        self.movement_handler.handle_movement(dt, level_width, level_height, collision_objects)

        # Затем синхронизируем rect (спрайт) с hitbox
        self.rect.midbottom = (
            self.hitbox.centerx - config.PLAYER_HITBOX["X_OFFSET"],
            self.hitbox.bottom - config.PLAYER_HITBOX["Y_OFFSET"]
        )

        # Расходуем выносливость при движении
        self._handle_stamina_consumption(dt)

        self._animate(dt)
        
        # Обновляем индикаторы
        self._update_indicators(dt)

    def _handle_stamina_consumption(self, dt):
        """Обрабатывает расход выносливости при движении."""
        if self.is_walking:
            stamina_cost = self.stamina_cost_per_second * dt
            
            if not self.stats.use_stamina(stamina_cost):
                # Если выносливости недостаточно, замедляем игрока
                self.speed = config.PLAYER_SPEED * 0.5
                if config.DEBUG_MODE:
                    print(f"[PLAYER DEBUG] Недостаточно выносливости, скорость снижена")
            else:
                self.speed = config.PLAYER_SPEED
        else:
            # Восстанавливаем нормальную скорость
            self.speed = config.PLAYER_SPEED

    def _update_indicators(self, dt):
        """Обновляет индикаторы урона и лечения."""
        # Обновляем индикаторы урона
        for indicator in self.damage_indicators[:]:
            indicator['timer'] -= dt
            indicator['y'] -= 30 * dt  # Движение вверх
            if indicator['timer'] <= 0:
                self.damage_indicators.remove(indicator)
        
        # Обновляем индикаторы лечения
        for indicator in self.heal_indicators[:]:
            indicator['timer'] -= dt
            indicator['y'] -= 30 * dt  # Движение вверх
            if indicator['timer'] <= 0:
                self.heal_indicators.remove(indicator)

    def _animate(self, dt):
        # Останавливаем анимацию, если игрок мертв
        if not self.is_alive():
            return
            
        self.animation_time += dt
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self._get_frame()

    # Методы для работы с характеристиками
    
    def take_damage(self, damage: float, source: str = "unknown") -> float:
        """Игрок получает урон."""
        # Для тестирования можно отключить неуязвимость
        if self.is_invulnerable and source != "test":
            if config.DEBUG_MODE:
                print(f"[PLAYER DEBUG] Игрок неуязвим, урон заблокирован: {damage} HP")
            return 0.0
        
        if config.DEBUG_MODE:
            print(f"[PLAYER DEBUG] Получение урона: {damage} HP")
        
        actual_damage = self.stats.take_damage(damage)
        
        if actual_damage > 0:
            # Активируем неуязвимость только если это не тестовый урон
            if source != "test":
                self.is_invulnerable = True
                self.invulnerability_timer = self.invulnerability_duration
                
                if config.DEBUG_MODE:
                    print(f"[PLAYER DEBUG] Активирована неуязвимость на {self.invulnerability_duration} сек")
            
            # Добавляем индикатор урона
            self.damage_indicators.append({
                'damage': actual_damage,
                'x': self.rect.centerx,
                'y': self.rect.top,
                'timer': 1.0
            })
            
            # Воспроизводим звук урона
            if self.sound_manager:
                # Здесь можно добавить звук получения урона
                pass
        
        return actual_damage
    
    def heal(self, amount: float, source: str = "unknown") -> float:
        """Игрок восстанавливается."""
        if config.DEBUG_MODE:
            print(f"[PLAYER DEBUG] Восстановление: {amount} HP")
        
        actual_heal = self.stats.heal(amount)
        
        if actual_heal > 0:
            # Добавляем индикатор лечения
            self.heal_indicators.append({
                'heal': actual_heal,
                'x': self.rect.centerx,
                'y': self.rect.top,
                'timer': 1.0
            })
            
            # Воспроизводим звук лечения
            if self.sound_manager:
                # Здесь можно добавить звук лечения
                pass
        
        return actual_heal
    
    def add_experience(self, amount: float) -> int:
        """Игрок получает опыт."""
        levels_gained = self.stats.add_experience(amount)
        
        if levels_gained > 0:
            # Здесь можно добавить эффекты повышения уровня
            # Например, восстановление здоровья, звуки и т.д.
            if self.sound_manager:
                # Звук повышения уровня
                pass
        
        return levels_gained
    
    def add_effect(self, effect_name: str, modifier: StatModifier):
        """Добавляет эффект к игроку."""
        self.active_effects[effect_name] = modifier
        self.stats.health.add_modifier(modifier)
    
    def remove_effect(self, effect_name: str):
        """Удаляет эффект с игрока."""
        if effect_name in self.active_effects:
            modifier = self.active_effects[effect_name]
            self.stats.health.remove_modifier(modifier.source)
            del self.active_effects[effect_name]
    
    def is_alive(self) -> bool:
        """Проверяет, жив ли игрок."""
        return self.stats.is_alive()
    
    def revive(self, health_percentage: float = 0.5):
        """Воскрешает игрока."""
        self.stats.health.revive(health_percentage)
        self.is_invulnerable = False
        self.invulnerability_timer = 0.0
    
    def get_health_percentage(self) -> float:
        """Возвращает процент здоровья."""
        return self.stats.health.get_health_percentage()
    
    def get_stamina_percentage(self) -> float:
        """Возвращает процент выносливости."""
        return self.stats.stamina.get_stamina_percentage()
    
    def get_level(self) -> int:
        """Возвращает уровень игрока."""
        return self.stats.experience.level
    
    def draw_indicators(self, screen: pygame.Surface):
        """Отрисовывает индикаторы урона и лечения."""
        # Отрисовываем индикаторы урона
        for indicator in self.damage_indicators:
            damage_text = f"-{int(indicator['damage'])}"
            font = pygame.font.Font(None, 24)
            text_surface = font.render(damage_text, True, (255, 0, 0))
            
            # Тень
            shadow_surface = font.render(damage_text, True, (0, 0, 0))
            screen.blit(shadow_surface, (indicator['x'] + 1, indicator['y'] + 1))
            screen.blit(text_surface, (indicator['x'], indicator['y']))
        
        # Отрисовываем индикаторы лечения
        for indicator in self.heal_indicators:
            heal_text = f"+{int(indicator['heal'])}"
            font = pygame.font.Font(None, 24)
            text_surface = font.render(heal_text, True, (0, 255, 0))
            
            # Тень
            shadow_surface = font.render(heal_text, True, (0, 0, 0))
            screen.blit(shadow_surface, (indicator['x'] + 1, indicator['y'] + 1))
            screen.blit(text_surface, (indicator['x'], indicator['y']))
