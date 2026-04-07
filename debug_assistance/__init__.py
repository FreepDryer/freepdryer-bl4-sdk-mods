from typing import Any 
from mods_base import build_mod, keybind, unrealsdk, get_pc
from .niagara import *

should_log_calls : bool = False

def notify(text: str) -> None:
    print(f"[Debug Assist] {text}")
    return None


def print_function_info(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    print(f"Object : {obj} - \nArgs : {args} - \nReturn : {ret} - \nFunction Called : {func}")




@keybind("Toggle Unreal Calls", description=("Pressing the bound key will toggle unrealsdk.hooks.log_all_calls. File will be stored in its default location." + 
"Borderlands 4\\OakGame\\Binaries\\Win64\\Plugins\\unrealsdk.calls.tsv"))
def ToggleCalls() -> None:
    global should_log_calls
    if not should_log_calls:
        should_log_calls = True
        unrealsdk.hooks.log_all_calls(True)
        notify("Calls are logged")
        
    else:
        should_log_calls = False
        unrealsdk.hooks.log_all_calls(False)
        notify("Calls are no longer logged")
    return None
def getIOTD():
    iotds = []
    pc = get_pc()
    for machine in unrealsdk.find_all("OakVendingMachine",False):
        if not machine or machine == machine.Class.ClassDefaultObject:
            continue
        current_iotd = machine.GetIOTDForPlayer(pc)
        if current_iotd:
            iotds.append(current_iotd)
    return iotds

@keybind("Print all item rarity info")
def PrintItems():
    items = unrealsdk.find_all("InventoryPickup", False)
    iotd = getIOTD()
    for item in items:
        if not item or item == item.Class.ClassDefaultObject or item in iotd:
            continue
        notify(item.AttractEffectComponent.OverrideParameters)
        notify(LootBeam.from_InventoryPickup(item))


build_mod()