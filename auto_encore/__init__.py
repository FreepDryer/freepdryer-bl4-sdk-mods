from __future__ import annotations

import time
from typing import Any

from mods_base import SliderOption, build_mod, get_pc, hook
from unrealsdk import find_all
from unrealsdk.hooks import Type
from unrealsdk.logging import error
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct


CM_PER_METER = 100.0
SCRIPT_BOSS_REPLAY_CLASS_PATH = (
    "GbxActorScriptClass'/Game/InteractiveObjects/GameSystemMachines/"
    "BossReplay/Script_BossReplay.Script_BossReplay_C'"
)
USE_TYPE_PRIMARY = 0
USE_TYPE_SECONDARY = 1
CHECK_INTERVAL_SEC = 0.05
ACTION_COOLDOWN_SEC = 0.75

auto_use_radius_meters: SliderOption = SliderOption(
    "Auto Use Radius (m)",
    6.0,
    0.1,
    25.0,
    0.1,
    False,
    description="Extra radius for auto-use around Boss Replay machines.",
)
use_type_option: SliderOption = SliderOption(
    "Use Type",
    USE_TYPE_PRIMARY,
    USE_TYPE_PRIMARY,
    USE_TYPE_SECONDARY,
    1,
    True,
    description="0 = primary use, 1 = secondary use.",
)

_last_check = 0.0
_last_action = 0.0


def get_player_controller_and_pawn() -> tuple[UObject | None, UObject | None]:
    pc = get_pc()
    if pc is None:
        return None, None

    for attr in ("Pawn", "AcknowledgedPawn", "OakCharacter", "Character"):
        pawn = getattr(pc, attr, None)
        if pawn is not None:
            return pc, pawn

    return pc, None


def is_current_player_actor(obj: UObject | None) -> bool:
    if obj is None:
        return False

    _, pawn = get_player_controller_and_pawn()
    return pawn is obj


def is_current_player_script(obj: UObject | None) -> bool:
    if obj is None:
        return False

    _, pawn = get_player_controller_and_pawn()
    if pawn is None:
        return False

    try:
        return obj.GetAssociatedActor() is pawn
    except Exception:
        return False


def is_boss_replay_actor(obj: UObject | None) -> bool:
    if obj is None:
        return False

    try:
        name = str(getattr(obj, "Name", ""))
        path = str(obj)
        if "IO_BossReplay_" in name or "IO_BossReplay_" in path:
            return True

        return get_boss_replay_script(obj) is not None
    except Exception:
        return False


def is_boss_replay_script(script: UObject | None) -> bool:
    if script is None:
        return False

    script_class = getattr(script, "Class", None)
    if str(script_class) == SCRIPT_BOSS_REPLAY_CLASS_PATH:
        return True

    return "Script_BossReplay_C" in str(script)


def get_boss_replay_script(obj: UObject | None) -> UObject | None:
    script_data = getattr(obj, "ScriptData", None)
    if script_data is None:
        return None

    instances = getattr(script_data, "Instances", None)
    if not instances:
        return None

    for script in instances:
        if is_boss_replay_script(script):
            return script

    return None


def get_distance_cm(a: UObject | None, b: UObject | None) -> float | None:
    if a is None or b is None:
        return None

    try:
        return float(a.GetDistanceTo(b))
    except Exception:
        return None


def find_nearest_boss_replay(pawn: UObject) -> tuple[UObject | None, UObject | None]:
    best_obj = None
    best_script = None
    best_distance_cm = None
    max_distance_cm = float(auto_use_radius_meters.value) * CM_PER_METER

    for obj in find_all("OakInteractiveObject", exact=False):
        try:
            if not is_boss_replay_actor(obj):
                continue

            distance_cm = get_distance_cm(pawn, obj)
            if distance_cm is None or distance_cm > max_distance_cm:
                continue

            script = get_boss_replay_script(obj)
            if script is None:
                continue

            if best_distance_cm is None or distance_cm < best_distance_cm:
                best_distance_cm = distance_cm
                best_obj = obj
                best_script = script

        except Exception as ex:
            error(f"[AutoEncore] Scan error: {ex}")

    return best_obj, best_script


def try_use_boss_replay(script: UObject, pc: UObject) -> bool:
    use_type = int(use_type_option.value)
    if use_type not in (USE_TYPE_PRIMARY, USE_TYPE_SECONDARY):
        return False

    try:
        script.GbxActorScriptEvt__UsableActorState_K2_OnUsed(pc, use_type, False)
        return True
    except Exception as ex:
        error(f"[AutoEncore] Failed to trigger boss replay: {ex}")
        return False


def auto_tick_common() -> None:
    global _last_check, _last_action

    now = time.time()
    if now - _last_check < CHECK_INTERVAL_SEC:
        return
    _last_check = now

    if now - _last_action < ACTION_COOLDOWN_SEC:
        return

    pc, pawn = get_player_controller_and_pawn()
    if pc is None or pawn is None:
        return

    boss_obj, script = find_nearest_boss_replay(pawn)
    if boss_obj is None or script is None:
        return

    if try_use_boss_replay(script, pc):
        _last_action = now


@hook(
    "/Game/PlayerCharacters/Temporary/_Shared/GbxScripts/"
    "Script_GbxSwimming.Script_GbxSwimming_C:CE_Query_GlobalWetness",
    Type.POST,
)
def auto_boss_replay_tick(
    obj: UObject,
    args: WrappedStruct,
    ret: Any,
    func: BoundFunction,
) -> None:
    del args, ret, func

    if not is_current_player_script(obj):
        return

    auto_tick_common()


build_mod()
