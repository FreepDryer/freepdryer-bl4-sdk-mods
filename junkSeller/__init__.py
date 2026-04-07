from typing import Any 
from mods_base import keybind, hook, build_mod,get_pc, BoolOption
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct 
from unrealsdk.hooks import Type
import unrealsdk

trashFlags = [4,5]

sellJunk : BoolOption = BoolOption("Sell Junk on Pickup?", True, "On", "Off")
wantSellAll : BoolOption = BoolOption("Should Sell All Trash on Pickup?", False, "All Trash in Inventory", "Only Pickup Trash")

def notify(text): 
    print(f"[JunkSeller] {text}")

def sellJunkItems(sellAll : bool = True) -> None:
    bpackItems = get_pc().PlayerState.BackpackItems.items
    if sellAll:
        sell_items = [trashItem.InventoryItem.Handle.Handle for trashItem in bpackItems if trashItem.InventoryItem.item.State.Flags in trashFlags]
    else:
        sell_items = [trashItem.InventoryItem.Handle.Handle for trashItem in bpackItems if trashItem.InventoryItem.item.State.Flags == trashFlags[0]]
    machine : list = unrealsdk.find_all("OakVendingMachine", False)[0]
    if not machine:
        notify("Could not sell junk item(s)")
    if len(sell_items) <= 0:
        notify("No items in backpack to sell!")
    
    currency = unrealsdk.make_struct('SToken')
    currency.Name = 'Cash'
    cashHash = [x for x in get_pc().CurrencyManager.currencies if x.type.name == 'Cash'][0]
    currency.Hash = cashHash.type.Hash
    
    for sItem in sell_items:
        handle = unrealsdk.make_struct('InventoryItemHandle')
        handle.Handle = sItem
        get_pc().ServerSellItem(machine, handle, 'backpack', currency)

@hook("/Script/OakGame.OakPlayerController:ServerUseJunkObject", Type.POST)
def sellPickedJunk(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if args.bAutoTrash and sellJunk.value:
        if wantSellAll.value :  sellJunkItems(True)
        else :                  sellJunkItems(False)
            
@keybind("Sell All Junk Items")
def sellAllJunkItems() -> None:
    sellJunkItems(True)

build_mod()