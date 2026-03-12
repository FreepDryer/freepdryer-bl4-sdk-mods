from typing import Any 
from mods_base import hook, build_mod,get_pc, SliderOption, BoolOption
from unrealsdk.hooks import Type
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct 



vehicle_jump_height : SliderOption = SliderOption("Vehicle Jump Height", 330.0, 0.0,1000, 0.1, False, description="How high should the vehicle jump? (default is 165.0)") 
vehicle_gravity_scalar : SliderOption = SliderOption("Vehicle Gravity Scale", 1.75, 1.0, 20.0, 0.1, False, description="Gravity multiplier for vehicles (default is 8.0)")
vehicle_jump_impulse_distance : SliderOption = SliderOption("Vehicle Jump Impulse Distance", 100.0, 1.0, 1000.0, 0.1, False, description="Vehicle Jump Impulse Distance (default 500.0)")
vehicle_jump_impulse_magnitude : SliderOption = SliderOption("Vehicle Jump Impulse Magnitude", 500.0, 1.0, 1000.0, 0.1, False, description="Vehicle Jump Impulse Magnitude (default is 100.0)")

@hook("/Script/OakGame.OakUIDataCollector_EquippedGadget:OnPossessPawnChanged", Type.POST)
def Vehicle_On_Construct(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if not get_pc().Pawn or get_pc().Pawn.Class.Name == "OakCharacter":
        return
    
    get_pc().Pawn.OakVehicleMovement.HoverSetup.PowerslideJumpGravityScalar.constant = vehicle_gravity_scalar.value
    get_pc().Pawn.OakVehicleMovement.HoverSetup.PowerslideJumpHeight.constant = vehicle_jump_height.value
    get_pc().Pawn.OakVehicleMovement.HoverSetup.PowerslideJumpExpressionImpulseDistance = vehicle_jump_impulse_distance.value
    get_pc().Pawn.OakVehicleMovement.HoverSetup.PowerslideJumpExpressionImpulseMagnitude = vehicle_jump_impulse_magnitude.value




build_mod()