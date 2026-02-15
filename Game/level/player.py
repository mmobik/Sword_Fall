"""
Класс игрока.

Интегрирован с системой характеристик (`PlayerStats`) и системой
движения (`PlayerMovementHandler`). Следует принципам SOLID:

- Логика характеристик вынесена в `PlayerStats`
- Логика движения вынесена в `PlayerMovementHandler`
- Класс `Player` отвечает за анимацию, связку систем и публичный API
"""

from __future__ import annotations

from typing import Optional, List, Tuple, Dict

import pygame

from core.config import config
from level.player_stats import PlayerStats
from level.spritesheet import SpriteSheet
from level.player_movement import PlayerMovementHandler
from core.combat_system import CombatSystem
from core.pathutils import resource_path


class Player(pygame.sprite.Sprite):
    """
    Игрок с поддержкой характеристик, анимаций и движения.

    Публичный API класса используется во многих местах игры:
    - `core/game_resources.py` (создание игрока)
    - `core/game_loop.py` (урон, лечение, опыт, воскрешение)
    - `core/rendering.py` и `game.py` (дебаг‑информация, отрисовка)
    - `level/player_movement.py` (управление движением)
    """

    def __init__(
        self,
        x: int,
        y: int,
        sound_manager: Optional[object] = None,
        game: Optional[object] = None,
        stats: Optional[PlayerStats] = None,
    ) -> None:
        """
        Создает объект игрока.

        Args:
            x: начальная координата X (в пикселях).
            y: начальная координата Y (в пикселях).
            sound_manager: менеджер звука (может быть None
                при использовании в простых тестах/утилитах).
            game: ссылка на основной объект игры (если есть).
            stats: уже созданный объект PlayerStats (опционально).
        """
        super().__init__()

        # Базовые ссылки
        self.sound_manager = sound_manager
        # Пытаемся аккуратно получить ссылку на game
        self.game = game or getattr(sound_manager, "game", None)

        # Характеристики игрока
        self.stats: PlayerStats = stats or PlayerStats(game=self.game)

        # Движение / состояние
        self.speed: float = float(config.PLAYER_SPEED)
        self.is_walking: bool = False
        self._was_walking: bool = False
        self._steps_channel: Optional[pygame.mixer.Channel] = None

        # Боевая система (инициализируем до загрузки анимаций, так как они зависят от неё)
        self.combat_system = CombatSystem(player=self)
        self._last_sprite_state: Optional[str] = None  # Отслеживание изменения состояния спрайта

        # --- Анимации ---
        self.state_name: str = "idle_front"
        self.current_frame: int = 0
        self._frame_time: float = 0.0
        self._animations: Dict[str, Dict[str, object]] = {}
        self._load_animations()

        # Текущий спрайт / прямоугольники
        if self.state_name in self._animations:
            self.image: pygame.Surface = self._animations[self.state_name]["frames"][0]  # type: ignore[index]
        else:
            # Fallback – простой квадрат, если что‑то пошло не так с ресурсами
            self.image = pygame.Surface(config.FRAME_SIZE, pygame.SRCALPHA)
            self.image.fill((255, 0, 255))

        # --- Прямоугольники спрайта и хитбокса ---
        # Координаты (x, y) трактуем как позицию НОГ персонажа (midbottom),
        # как было в предыдущей версии Player.
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.midbottom = (x, y)

        # Хитбокс рассчитываем относительно rect (спрайта)
        hb_cfg = config.PLAYER_HITBOX
        hitbox_width = hb_cfg["WIDTH"]
        hitbox_height = hb_cfg["HEIGHT"]

        # X: центр спрайта + смещение
        # Y: от верха спрайта + смещение
        hitbox_x = self.rect.centerx - hitbox_width // 2 + hb_cfg["X_OFFSET"]
        hitbox_y = self.rect.top + hb_cfg["Y_OFFSET"]

        self.hitbox: pygame.Rect = pygame.Rect(
            hitbox_x,
            hitbox_y,
            hitbox_width,
            hitbox_height,
        )

        # Обработчик движения
        self._movement_handler = PlayerMovementHandler(self)

        # Состояние атаки
        self.is_attacking: bool = False
        self.attack_direction: str = "right"  # "right" или "left"
        self._attack_animations: Dict[str, Dict[str, object]] = {}
        self._load_attack_animations()

        # Индикаторы урона / лечения
        self._indicators: List[Dict[str, object]] = []
        self._indicator_font = pygame.font.Font(None, 24)

    # ------------------------------------------------------------------
    # Инициализация анимаций
    # ------------------------------------------------------------------
    def _load_animations(self) -> None:
        """Загружает анимации игрока на основе `config.PLAYER_STATES`."""
        # Получаем текущее состояние спрайта (armed/unarmed)
        inventory = self._get_inventory()
        sprite_state = self.combat_system.get_sprite_state(inventory) if inventory else "unarmed"
        
        frame_w, frame_h = config.FRAME_SIZE
        
        # Получаем базовые состояния из конфига
        base_states = config.PLAYER_STATES
        
        for state, params in base_states.items():
            # Определяем путь к спрайту в зависимости от состояния
            if sprite_state == "armed":
                # Используем путь из боевой системы для armed состояния
                sheet_path = self.combat_system.get_sprite_path(inventory, state)
            else:
                # Используем путь из конфига для unarmed состояния
                sheet_path = params["sprite_sheet"]
            
            frames_xy: List[Tuple[int, int]] = params["frames"]  # type: ignore[assignment]
            anim_speed: float = float(params.get("animation_speed", 0.15))

            # Используем resource_path для корректной работы с путями
            full_sheet_path = resource_path(sheet_path)
            sheet = SpriteSheet(full_sheet_path, width=frame_w, height=frame_h)
            frames: List[pygame.Surface] = []
            for x, y in frames_xy:
                frames.append(sheet.get_image(x, y, frame_w, frame_h))

            self._animations[state] = {
                "frames": frames,
                "animation_speed": anim_speed,
            }
        
        # Сохраняем текущее состояние для отслеживания изменений
        self._last_sprite_state = sprite_state
    
    def _get_inventory(self):
        """Получает объект инвентаря из game."""
        if self.game and hasattr(self.game, 'player_ui'):
            return getattr(self.game.player_ui, 'inventory', None)
        return None
    
    def reload_animations(self) -> None:
        """
        Перезагружает анимации при изменении экипировки.
        Вызывается автоматически при обнаружении изменения состояния.
        """
        inventory = self._get_inventory()
        if inventory:
            self.combat_system.update_equipment(inventory)
        
        current_state = self.combat_system.get_sprite_state(inventory) if inventory else "unarmed"
        
        # Перезагружаем только если состояние изменилось
        if current_state != self._last_sprite_state:
            if config.DEBUG_MODE:
                print(f"[PLAYER] Изменение состояния спрайта: {self._last_sprite_state} -> {current_state}")
            
            # Сохраняем текущее состояние анимации
            old_state = self.state_name
            old_frame = self.current_frame
            
            # Перезагружаем анимации
            self._load_animations()
            
            # Загружаем анимации атаки, если оружие экипировано
            if current_state == "armed":
                self._load_attack_animations()
            elif current_state == "unarmed":
                # Очищаем анимации атаки при снятии оружия
                self._attack_animations.clear()
                if self.is_attacking:
                    self.is_attacking = False
            
            # Восстанавливаем состояние анимации, если оно существует
            if old_state in self._animations:
                self.set_state(old_state)
                # Пытаемся восстановить кадр (если возможно)
                if old_frame < len(self._animations[old_state]["frames"]):  # type: ignore[index]
                    self.current_frame = old_frame
                    self.image = self._animations[old_state]["frames"][old_frame]  # type: ignore[index]
    
    def _load_attack_animations(self) -> None:
        """
        Загружает анимации атаки из Attacks.png.
        Первые 18 кадров - атака вправо, следующие 18 - атака влево.
        Размер кадра: 128x64, чтение слева направо и вниз.
        """
        inventory = self._get_inventory()
        if not inventory or not self.combat_system.is_armed(inventory):
            # Если оружие не экипировано, не загружаем анимации атаки
            return
        
        attack_sprite_path = "Game/assets/Sprites/player/armed/Attacks.png"
        full_path = resource_path(attack_sprite_path)
        
        frame_w, frame_h = config.FRAME_SIZE  # 128x64
        
        try:
            # Загружаем весь спрайт для определения размеров
            temp_sheet = pygame.image.load(full_path).convert_alpha()
            sheet_width = temp_sheet.get_width()
            sheet_height = temp_sheet.get_height()
            
            # Количество кадров в строке
            frames_per_row = sheet_width // frame_w
            total_rows = sheet_height // frame_h
            
            if config.DEBUG_MODE:
                print(f"[PLAYER] Загрузка анимаций атаки: {frames_per_row} кадров в строке, {total_rows} строк, размер {sheet_width}x{sheet_height}")
            
            # Загружаем кадры напрямую из изображения
            attack_right_frames: List[pygame.Surface] = []
            attack_left_frames: List[pygame.Surface] = []
            
            for frame_idx in range(36):  # Всего 36 кадров (18+18)
                row = frame_idx // frames_per_row
                col = frame_idx % frames_per_row
                x = col * frame_w
                y = row * frame_h
                
                # Извлекаем кадр напрямую
                frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                frame.blit(temp_sheet, (0, 0), (x, y, frame_w, frame_h))
                
                if frame_idx < 18:
                    # Первые 18 кадров - атака вправо
                    attack_right_frames.append(frame)
                else:
                    # Следующие 18 кадров - атака влево
                    attack_left_frames.append(frame)
            
            # Сохраняем анимации
            self._attack_animations["attack_right"] = {
                "frames": attack_right_frames,
                "animation_speed": 0.08,  # Быстрая анимация атаки
            }
            self._attack_animations["attack_left"] = {
                "frames": attack_left_frames,
                "animation_speed": 0.08,
            }
            
            if config.DEBUG_MODE:
                print(f"[PLAYER] Анимации атаки загружены: {len(attack_right_frames)} кадров вправо, {len(attack_left_frames)} кадров влево")
                
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"[PLAYER] Ошибка загрузки анимаций атаки: {e}")
            # Создаем пустые анимации в случае ошибки
            self._attack_animations["attack_right"] = {"frames": [], "animation_speed": 0.08}
            self._attack_animations["attack_left"] = {"frames": [], "animation_speed": 0.08}
    
    def start_attack(self, direction: str = "right") -> bool:
        """
        Начинает атаку в указанном направлении.
        
        Args:
            direction: Направление атаки ("right" или "left").
            
        Returns:
            True, если атака начата, False если оружие не экипировано или уже идет атака.
        """
        inventory = self._get_inventory()
        if not inventory or not self.combat_system.is_armed(inventory):
            return False
        
        if self.is_attacking:
            return False  # Уже идет атака
        
        # Перезагружаем анимации атаки, если они еще не загружены
        if not self._attack_animations.get("attack_right", {}).get("frames"):
            self._load_attack_animations()
        
        # Проверяем, что анимации загружены
        attack_state = f"attack_{direction}"
        if attack_state not in self._attack_animations or not self._attack_animations[attack_state].get("frames"):
            if config.DEBUG_MODE:
                print(f"[PLAYER] Анимация атаки {attack_state} не загружена")
            return False
        
        self.is_attacking = True
        self.attack_direction = direction
        
        # Устанавливаем состояние атаки
        self.set_state(attack_state)
        self.current_frame = 0
        self._frame_time = 0.0
        
        # Устанавливаем первый кадр анимации
        anim = self._attack_animations[attack_state]
        frames = anim.get("frames", [])
        if frames:
            self.image = frames[0]
        
        return True
    
    def _update_attack_animation(self, dt: float) -> None:
        """Обновляет анимацию атаки."""
        if not self.is_attacking:
            return
        
        attack_state = f"attack_{self.attack_direction}"
        anim = self._attack_animations.get(attack_state)
        
        if not anim or not anim.get("frames"):
            # Анимация не загружена или закончилась
            self.is_attacking = False
            # Возвращаемся к обычному состоянию
            if self.attack_direction == "right":
                self.set_state("idle_right")
            else:
                self.set_state("idle_left")
            return
        
        frames: List[pygame.Surface] = anim["frames"]  # type: ignore[assignment]
        speed: float = anim["animation_speed"]  # type: ignore[assignment]
        
        if not frames:
            self.is_attacking = False
            return
        
        self._frame_time += dt
        if self._frame_time >= speed:
            self._frame_time -= speed
            self.current_frame += 1
            
            if self.current_frame >= len(frames):
                # Анимация закончилась
                self.is_attacking = False
                self.current_frame = 0
                # Возвращаемся к обычному состоянию
                # Определяем idle состояние на основе направления атаки
                if self.attack_direction == "right":
                    self.set_state("idle_right")
                else:
                    self.set_state("idle_left")
            else:
                self.image = frames[self.current_frame]

    def set_state(self, new_state: str) -> None:
        """Устанавливает новое анимационное состояние."""
        if new_state == self.state_name:
            return
        
        # Проверяем, является ли это состоянием атаки
        if new_state.startswith("attack_"):
            # Состояние атаки обрабатывается отдельно
            if new_state in self._attack_animations:
                self.state_name = new_state
                self.current_frame = 0
                self._frame_time = 0.0
                anim = self._attack_animations[new_state]
                if anim.get("frames"):
                    self.image = anim["frames"][0]  # type: ignore[index]
            return
        
        if new_state not in self._animations:
            # Неизвестное состояние – игнорируем, чтобы не падать
            return

        self.state_name = new_state
        self.current_frame = 0
        self._frame_time = 0.0
        self.image = self._animations[self.state_name]["frames"][0]  # type: ignore[index]

    def _update_animation(self, dt: float) -> None:
        """Обновляет текущую анимацию."""
        anim = self._animations.get(self.state_name)
        if not anim:
            return

        frames: List[pygame.Surface] = anim["frames"]  # type: ignore[assignment]
        speed: float = anim["animation_speed"]  # type: ignore[assignment]

        if not frames or speed <= 0:
            return

        self._frame_time += dt
        if self._frame_time >= speed:
            self._frame_time -= speed
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]

    # ------------------------------------------------------------------
    # Публичные методы, используемые другими модулями
    # ------------------------------------------------------------------
    def is_alive(self) -> bool:
        """Возвращает, жив ли игрок (обертка над PlayerStats)."""
        return self.stats.is_alive()

    def revive(self) -> None:
        """Воскрешает игрока через систему характеристик."""
        self.stats.health.revive()
        # Сбрасываем базовое состояние анимации
        self.set_state("idle_front")

    def take_damage(self, amount: float, source: str = "unknown") -> float:
        """
        Наносит урон игроку.

        Возвращает фактический полученный урон.
        """
        actual = self.stats.take_damage(amount)
        if actual > 0:
            self._add_indicator(-actual, (255, 0, 0))
        return actual

    def heal(self, amount: float, source: str = "unknown") -> float:
        """
        Восстанавливает здоровье игрока.

        Возвращает фактическое восстановленное значение.
        """
        actual = self.stats.heal(amount)
        if actual > 0:
            self._add_indicator(actual, (0, 255, 0))
        return actual

    def add_experience(self, amount: float) -> int:
        """
        Добавляет опыт игроку.

        Возвращает количество полученных уровней.
        """
        return self.stats.add_experience(amount)

    # ------------------------------------------------------------------
    # Логика обновления
    # ------------------------------------------------------------------
    def _handle_stamina_consumption(self, dt: float) -> None:
        """
        Обработка расхода выносливости при движении.

        Небольшая, но достаточная реализация для интеграции с системой
        характеристик: при движении тратится выносливость, при полном
        истощении скорость немного падает.
        """
        # Базовая скорость
        base_speed = float(config.PLAYER_SPEED)

        if self.is_walking and dt > 0:
            # 10 единиц выносливости в секунду при постоянном движении
            stamina_cost = 10.0 * dt
            if not self.stats.use_stamina(stamina_cost):
                # Не хватает выносливости – замедляемся
                self.speed = base_speed * 0.5
                return

        # Если не идем или выносливость есть – нормальная скорость
        self.speed = base_speed

    def update(
        self,
        dt: float,
        level_width: int,
        level_height: int,
        collision_objects: list,
    ) -> None:
        """
        Главный метод обновления игрока.

        Args:
            dt: дельта‑время кадра в секундах.
            level_width: ширина уровня в пикселях.
            level_height: высота уровня в пикселях.
            collision_objects: список объектов коллизий.
        """
        # Обновляем характеристики (регенерация и модификаторы)
        self.stats.update(dt)

        # Обработка выносливости / скорости
        self._handle_stamina_consumption(dt)

        # Движение (меняет только hitbox)
        self._movement_handler.handle_movement(
            dt, level_width, level_height, collision_objects
        )

        # Синхронизуем спрайт с хитбоксом так же, как в старой версии Player:
        # rect.midbottom зависит от hitbox.centerx и hitbox.bottom с учетом оффсетов
        hb_cfg = config.PLAYER_HITBOX
        self.rect.midbottom = (
            self.hitbox.centerx - hb_cfg["X_OFFSET"],
            self.hitbox.bottom - hb_cfg["Y_OFFSET"],
        )

        # Проверяем изменение экипировки и перезагружаем анимации при необходимости
        inventory = self._get_inventory()
        if inventory:
            current_state = self.combat_system.get_sprite_state(inventory)
            if current_state != self._last_sprite_state:
                self.reload_animations()
                # Перезагружаем анимации атаки при смене экипировки на armed
                if current_state == "armed":
                    self._load_attack_animations()
                elif current_state == "unarmed":
                    # Очищаем анимации атаки при снятии оружия
                    self._attack_animations.clear()
                    if self.is_attacking:
                        self.is_attacking = False

        # Обновление анимации атаки (приоритет над обычной анимацией)
        if self.is_attacking:
            self._update_attack_animation(dt)
        else:
            # Обычная анимация
            self._update_animation(dt)

        # Обновляем индикаторы урона/лечения
        self._update_indicators(dt)

    # ------------------------------------------------------------------
    # Индикаторы урона / лечения
    # ------------------------------------------------------------------
    def _add_indicator(self, value: float, color: Tuple[int, int, int]) -> None:
        """Создает новый плавающий индикатор над игроком."""
        # Позиция в мировых координатах (центр хитбокса)
        pos = (self.hitbox.centerx, self.hitbox.top)
        self._indicators.append(
            {
                "value": value,
                "color": color,
                "pos": list(pos),
                "age": 0.0,
                "lifetime": 1.0,
            }
        )

    def _update_indicators(self, dt: float) -> None:
        """Обновляет положение и время жизни индикаторов."""
        if not self._indicators:
            return

        for ind in self._indicators:
            ind["age"] = float(ind["age"]) + dt  # type: ignore[assignment]
            # Медленный подъем вверх
            pos = ind["pos"]  # type: ignore[assignment]
            pos[1] -= 30 * dt

        # Удаляем устаревшие индикаторы
        self._indicators = [
            ind for ind in self._indicators if float(ind["age"]) < float(ind["lifetime"])
        ]

    def draw_indicators(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает индикаторы урона / лечения.

        Поверхность – это виртуальный экран (`game.virtual_screen`).
        """
        if not self._indicators:
            return

        # Пытаемся учесть камеру, если есть ссылка на game
        camera = getattr(self.game, "camera", None)
        offset_x = getattr(getattr(camera, "offset", None), "x", 0)
        offset_y = getattr(getattr(camera, "offset", None), "y", 0)

        for ind in self._indicators:
            value = float(ind["value"])
            color: Tuple[int, int, int] = ind["color"]  # type: ignore[assignment]
            pos = ind["pos"]  # type: ignore[assignment]

            text = f"{int(value)}" if value > 0 else f"{int(value)}"
            text_surface = self._indicator_font.render(text, True, color)

            screen_x = pos[0] - offset_x - text_surface.get_width() // 2
            screen_y = pos[1] - offset_y - text_surface.get_height()

            surface.blit(text_surface, (screen_x, screen_y))

