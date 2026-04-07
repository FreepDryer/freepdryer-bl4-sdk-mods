from typing import Any 
from mods_base import hook, build_mod,get_pc, keybind, BoolOption, SliderOption
from unrealsdk import find_all
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct 
from unrealsdk.hooks import Type, Block
import math, unrealsdk

def notify(text): 
    print(f"[test] {text}")

def print_function_info(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    print(f"Object : {obj} - \nArgs : {args} - \nReturn : {ret} - \nFunction Called : {func}")

distance : SliderOption = SliderOption("Forward Teleport Distance", 250, 1.0, 50000, 1, True, description="Changes the distance of the forward teleport.")
godmode : bool = False
#Repair kit vars
maxCharges : int = 0
usedCharges : int = 0

@keybind("Teleport Forward")
def shortTeleport() -> None:
    transform = get_pc().OakCharacter.GetTransform()
    curPos = transform.Translation
    curQur = get_pc().GetTransform().Rotation
    pitch = math.asin(2 * (curQur.W * curQur.Y - curQur.Z * curQur.X))
    yaw = math.atan2(2 * (curQur.W * curQur.Z + curQur.X * curQur.Y), 1 - 2*(math.pow(curQur.Y,2) + math.pow(curQur.Z,2)))

    destination = curPos
    destination.Z += math.sin(-pitch) * distance.value
    destination.X += math.cos(yaw) * math.cos(pitch) * distance.value
    destination.Y += math.sin(yaw) * math.cos(pitch) * distance.value
    
    transform.Translation = destination
    sSweep = unrealsdk.make_struct("HitResult")
    bSweep = False
    bTeleport = True

    get_pc().OakCharacter.K2_SetActorTransform(transform, bSweep, sSweep, bTeleport)
    return None

@keybind("Insta Revive")
def reviveSelf() -> None:
    get_pc().OakCharacter.StopDownState(1)
    return None

@keybind("God Mode") # Bonk Utilities
def GodMode() -> None:
    global godmode
    if not godmode:
        get_pc().OakCharacter.bCanBeDamaged = False
        godmode = True
        notify("God Mode On")
    else:
        get_pc().OakCharacter.bCanBeDamaged = True
        godmode = False
        notify("God Mode Off")
    return None

@keybind("Kill Enemies") # Bonk Utilities
def KillEnemies() -> None:
    get_pc().ServerActivateDevPerk(3)
    notify("All Enemies Killed")
    return None


@hook("/Game/UI/Scripts/ui_script_repair_kit.ui_script_repair_kit_C:GainChargeRepairKit", Type.POST)
def GainRepairKitCharge(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    global maxCharges, usedCharges
    usedCharges = min(0, usedCharges - 1)
    notify(f"Recieved a charge {maxCharges} : {usedCharges}")


@hook("/Script/OakGame.OakCharacter:StartUsingRepairKit", Type.PRE)
def instaHeal(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    global maxCharges, usedCharges
    repairKit = get_pc().OakCharacter.EquippedInventorySlots.items[6].InstancedInventory
    maxCharges = repairKit.MaxCharges.Value
    if repairKit and maxCharges > usedCharges and repairKit.ActiveCharges == 0:
        get_pc().OakCharacter.StartRepair()
        get_pc().OakCharacter.NotifyCanUseRepairKit(True)
        usedCharges += 1
        notify(f"Expended a charge {maxCharges} : {usedCharges}")
    else:
        notify(f"{maxCharges} : {usedCharges}")
    return Block

@hook("/Script/OakGame.OakPlayerController:ServerUseJunkObject", Type.POST)
def ex(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    print_function_info(obj,args,ret,func)



build_mod()