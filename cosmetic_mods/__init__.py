
#Not working atm, weapon get stuck
holsteredWeapon = None
holstered = False

@keybind("Holster Weapon")
def holsterWeapon() -> None:
    activeWeapon = get_pc().OakCharacter.ActiveWeapons.Slots[0].Weapon
    if not activeWeapon:
        notify("No weapon found")
        return
    global holstered

    if holstered:
        # get_pc().OakCharacter.WeaponPutDown(activeWeapon)
        holstered = True
    elif not holstered:
        #Find weapon sight and detach.
        # sight = (x for x in activeWeapon.behaviors if x.Class.Name == "WeaponBehavior_Sight") #array, find Sight. detach
        for x in activeWeapon.behaviors:
            if x.Class.Name == "WeaponBehavior_Sight":
                x.WeaponDetached()
        get_pc().OakCharacter.WeaponPutDown(activeWeapon)
        # get_pc().OakCharacter.ClientSetActiveWeaponEquipSlot(9)



    return None
