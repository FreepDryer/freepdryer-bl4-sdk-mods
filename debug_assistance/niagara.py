# import ctypes
import enum

from dataclasses import dataclass

from unrealsdk.logging import info, warning, error
from unrealsdk.unreal import UObject, WeakPointer


@enum.global_enum
@enum.verify(enum.UNIQUE, enum.CONTINUOUS)
class LootBeamRarity(enum.IntEnum):
    UNKNOWN   = 0
    AMMO      = enum.auto()
    MONEY     = enum.auto()
    ERIDIUM   = enum.auto()
    HEALTH    = enum.auto()
    COMMON    = enum.auto()
    UNCOMMON  = enum.auto()
    RARE      = enum.auto()
    EPIC      = enum.auto()
    LEGENDARY = enum.auto()
    MISSION   = enum.auto()



NiagaraRarityColors = {
    bytes((0x52, 0xB8, 0xDE, 0x3E, 0x52, 0xB8, 0xDE, 0x3E, 0x52, 0xB8, 0xDE, 0x3E, 0x00, 0x00, 0x80, 0x3F)): AMMO,
    bytes((2)): ERIDIUM,
    bytes((3)): HEALTH,
    bytes((4)): MISSION,
    bytes((0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3F)): MONEY,
    # white gear
    bytes((6)): COMMON,
    # green gear
    bytes((7)): UNCOMMON,
    # blue gear, no firmware, nothing notable, VLA_SMG
    bytes((0x50, 0x8D, 0x97, 0x3C, 0xC3, 0xA0, 0xAC, 0x3E, 0xCF, 0x32, 0x17, 0x3F, 0x00, 0x00, 0x80, 0x3F)): RARE,
    # purple: weapon, no firmware
    bytes((0x6E, 0x69, 0xF5, 0x3E, 0x79, 0xE6, 0x65, 0x3D, 0x44, 0x8B, 0x28, 0x3F, 0x00, 0x00, 0x80, 0x3F)): EPIC,
    # orange: legendary shield with firmware.
    bytes((0x00, 0x00, 0x80, 0x3F, 0x8F, 0xA6, 0x6A, 0x3E, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x3F)): LEGENDARY,
}

def _as_hex(value: bytes):
    return f'bytes(({', '.join(map(lambda n: f"0x{n:02X}", list(value)))}))'

NiagaraTrue  = bytes((0xFF, 0xFF, 0xFF, 0xFF))
NiagaraFalse = bytes((0x00, 0x00, 0x00, 0x00))


UNKNOWN_PARAMS_SEEN = set([
    'User.Color2',
    'User.ScanlineTile',
    'User.Height',
    'User.Radius',
    'User.ShinyOneShot',
])

@dataclass(slots=True)
class LootBeam:
    rarity:       LootBeamRarity    = UNKNOWN
    anointment:   bool              = False
    firmware:     bool              = False
    shiny:        bool              = False
    legendary:    bool              = False

    # debugging stuff, basically.
    _raw_color:   bytes|None        = None
    item:         WeakPointer|None  = None


    @classmethod
    def from_InventoryPickup(cls, item: UObject) -> LootBeam:
        beam = cls(item=WeakPointer(item))
        if (component := item.AttractEffectComponent) is None:
            return beam

        # build from empty class to something with some info in it...
        data = bytes(component.OverrideParameters.ParameterData)
        for var in component.OverrideParameters.SortedParameterOffsets:
            match str(var.Name):
                case str('User.HasFirmware'):
                    raw = data[var.Offset:var.Offset+4]
                    value = (raw != NiagaraFalse)
                    # info(f'User.HasFirmware: data={_as_hex(raw)} {value=}')
                    beam.firmware = value

                case 'User.IsLegendary':
                    raw = data[var.Offset:var.Offset+4]
                    value = (raw != NiagaraFalse)
                    # info(f'User.IsLegendary: data={_as_hex(raw)} {value=}')
                    beam.legendary = value

                case str('User.HasAnointment'):
                    raw = data[var.Offset:var.Offset+4]
                    value = (raw != NiagaraFalse)
                    # info(f'User.HasAnointment: data={_as_hex(raw)}{value=}')
                    beam.anointment = value

                case str('User.IsShiny'):
                    raw = data[var.Offset:var.Offset+4]
                    value = (raw != NiagaraFalse)
                    # info(f'User.IsShiny: data={_as_hex(raw)} {value=}')
                    beam.shiny = value

                case str('User.Color'):
                    raw = data[var.Offset:var.Offset+16]
                    if (value := NiagaraRarityColors.get(raw, UNKNOWN)) == UNKNOWN:
                        beam._raw_color = _as_hex(raw)
                    beam.rarity = value

                case str(name):
                    if name not in UNKNOWN_PARAMS_SEEN:
                        warning(f'saw unknown niagara parameter {name=} {type(name)=} {component.OverrideParameters=}')
                        UNKNOWN_PARAMS_SEEN.add(name)

        # decoded what we can, job done.
        return beam
