from typing import Any 
from mods_base import build_mod, keybind, unrealsdk

should_log_calls : bool = False

def notify(text: str) -> None:
    print(f"[Debug Assist] {text}")
    return None


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



build_mod()