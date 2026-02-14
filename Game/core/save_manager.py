"""
Модуль сохранения и загрузки состояния игры.

Сохраняет в JSON (в папке Game/userdata) базовое состояние:
- позиция игрока и текущая карта;
- состояние инвентаря (слоты и экипировка);
- прогресс диалогов с NPC.

Функции стараются быть максимально безопасными: при любой ошибке просто
выводится предупреждение в консоль и игра продолжает работать без сохранения.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from core.config import config
from dialogues.npc_dialogues import RoyalGuardDialogue, KingDialogue


SAVE_FILE_PATH = os.path.join("Game", "userdata", "savegame.json")


def _ensure_save_dir() -> None:
    """Гарантирует наличие директории для сохранений."""
    save_dir = os.path.dirname(SAVE_FILE_PATH)
    if save_dir and not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)


def _serialize_inventory(game) -> Dict[str, Any]:
    """Преобразует инвентарь в словарь для сохранения."""
    inventory = getattr(getattr(game, "player_ui", None), "inventory", None)
    if inventory and hasattr(inventory, "to_dict"):
        try:
            return inventory.to_dict()
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"[SAVE] Ошибка сериализации инвентаря: {e}")
    return {}


def _serialize_dialogues(game) -> Dict[str, Any]:
    """Сохраняет состояние диалогов с NPC."""
    result: Dict[str, Any] = {}
    npc_dialogues = getattr(game, "npc_dialogues", {}) or {}

    for npc_id, dialogue in npc_dialogues.items():
        npc_key = str(npc_id)

        if isinstance(dialogue, RoyalGuardDialogue):
            result[npc_key] = {
                "type": "royal_guard",
                "interaction_count": getattr(dialogue, "interaction_count", 0),
                "phase_index": getattr(dialogue, "phase_index", 0),
            }
        elif isinstance(dialogue, KingDialogue):
            result[npc_key] = {
                "type": "king",
                "interaction_count": getattr(dialogue, "interaction_count", 0),
                "phase_index": getattr(dialogue, "phase_index", 0),
                "current_chain_index": getattr(dialogue, "current_chain_index", 0),
                "current_chain_position": getattr(dialogue, "current_chain_position", 0),
                "in_dialogue_chain": getattr(dialogue, "in_dialogue_chain", False),
            }
        else:
            # Базовый NPCDialogue (если появятся другие типы)
            state = getattr(dialogue, "state", None)
            if state is not None:
                result[npc_key] = {
                    "type": "generic",
                    "state": state,
                }

    return result


def save_game_state(game) -> None:
    """
    Сохраняет текущее состояние игры в JSON.

    Должно вызываться при выходе из игры или возврате в главное меню.
    Загружает существующий файл и обновляет только измененные секции.
    """
    try:
        # Загружаем существующие данные, если файл есть
        existing_data: Dict[str, Any] = {}
        if os.path.exists(SAVE_FILE_PATH):
            try:
                with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except Exception as e:
                if config.DEBUG_MODE:
                    print(f"[SAVE] Не удалось загрузить существующий файл: {e}")
        
        # Начинаем с существующих данных
        data = existing_data.copy()

        # Обновляем позицию игрока и карту
        player = getattr(game, "player", None)
        if player is not None and hasattr(player, "hitbox"):
            data["player"] = {
                "map_path": getattr(config, "LEVEL_MAP_PATH", None),
                "position": [player.hitbox.x, player.hitbox.y],
            }

        # Инвентарь (всегда сохраняем, даже если пуст)
        inv_data = _serialize_inventory(game)
        data["inventory"] = inv_data  # Сохраняем всегда, даже если пуст

        # Диалоги
        dialogues_data = _serialize_dialogues(game)
        if dialogues_data:
            data["dialogues"] = dialogues_data

        # Если нечего сохранять — не создаём файл
        if not data:
            if config.DEBUG_MODE:
                print("[SAVE] Нет данных для сохранения.")
            return

        _ensure_save_dir()
        with open(SAVE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        if config.DEBUG_MODE:
            print(f"[SAVE] Состояние игры сохранено в {SAVE_FILE_PATH}")
    except Exception as e:
        if config.DEBUG_MODE:
            print(f"[SAVE] Ошибка при сохранении игры: {e}")


def _restore_inventory(game, data: Dict[str, Any]) -> None:
    """Восстанавливает инвентарь из словаря."""
    inventory = getattr(getattr(game, "player_ui", None), "inventory", None)
    if not inventory or not hasattr(inventory, "load_from_dict"):
        return

    try:
        inventory.load_from_dict(data)
    except Exception as e:
        if config.DEBUG_MODE:
            print(f"[LOAD] Ошибка восстановления инвентаря: {e}")


def _restore_dialogues(game, data: Dict[str, Any]) -> None:
    """Восстанавливает состояние диалогов с NPC."""
    restored: Dict[Any, Any] = {}

    for npc_id_str, dlg_data in (data or {}).items():
        dlg_type = dlg_data.get("type")
        try:
            # npc_id может быть как числом, так и строкой
            try:
                npc_id = int(npc_id_str)
            except ValueError:
                npc_id = npc_id_str

            if dlg_type == "royal_guard":
                dlg = RoyalGuardDialogue(npc_id)
                dlg.interaction_count = int(dlg_data.get("interaction_count", 0))
                dlg.phase_index = int(dlg_data.get("phase_index", 0))
            elif dlg_type == "king":
                dlg = KingDialogue(npc_id)
                dlg.interaction_count = int(dlg_data.get("interaction_count", 0))
                dlg.phase_index = int(dlg_data.get("phase_index", 0))
                dlg.current_chain_index = int(dlg_data.get("current_chain_index", 0))
                dlg.current_chain_position = int(dlg_data.get("current_chain_position", 0))
                dlg.in_dialogue_chain = bool(dlg_data.get("in_dialogue_chain", False))
            elif dlg_type == "generic":
                # Для потенциальных базовых диалогов
                from dialogues.npc_dialogues import NPCDialogue  # локальный импорт

                dlg = NPCDialogue(npc_id, dialogue_file="")
                dlg.state = int(dlg_data.get("state", 0))
            else:
                continue

            restored[npc_id] = dlg
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"[LOAD] Ошибка восстановления диалога NPC {npc_id_str}: {e}")

    if restored:
        game.npc_dialogues = restored


def load_game_state(game) -> bool:
    """
    Пытается загрузить сохранённое состояние игры.

    Возвращает True, если загрузка прошла успешно и состояние было применено.
    """
    if not os.path.exists(SAVE_FILE_PATH):
        if config.DEBUG_MODE:
            print(f"[LOAD] Файл сохранения не найден: {SAVE_FILE_PATH}")
        return False

    try:
        with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        if config.DEBUG_MODE:
            print(f"[LOAD] Ошибка чтения файла сохранения: {e}")
        return False

    try:
        # 1. Восстанавливаем карту и ресурсы
        player_data = data.get("player") or {}
        map_path = player_data.get("map_path") or getattr(config, "LEVEL_MAP_PATH", None)
        if map_path:
            setattr(config, "LEVEL_MAP_PATH", map_path)

        # Загружаем ресурсы (игрок, карта, UI и т.д.)
        if hasattr(game, "game_resources") and game.game_resources:
            game.game_resources.load_game_resources()

        # 2. Позиция игрока
        player = getattr(game, "player", None)
        position = player_data.get("position")
        if player is not None and position and len(position) == 2:
            x, y = int(position[0]), int(position[1])
            player.hitbox.x = x
            player.hitbox.y = y
            # Обновляем базовый rect, если он есть
            if hasattr(player, "rect"):
                player.rect.topleft = (x, y)
            if getattr(game, "camera", None):
                game.camera.update(player)

        # 3. Инвентарь
        inv_data = data.get("inventory")
        if inv_data:
            _restore_inventory(game, inv_data)

        # 4. Диалоги
        dlg_data = data.get("dialogues")
        if dlg_data:
            _restore_dialogues(game, dlg_data)

        if config.DEBUG_MODE:
            print(f"[LOAD] Состояние игры успешно загружено из {SAVE_FILE_PATH}")

        return True
    except Exception as e:
        if config.DEBUG_MODE:
            print(f"[LOAD] Ошибка при восстановлении состояния игры: {e}")
        return False

