from .hpdp import HpDpSpell
from .damage import DamageSpell
from .hp import HpSpell
from .dp import DpSpell
from .draw import DrawSpell
from .execute import ExecuteSpell
from .swap import SwapSpell
from .restore import RestoreSpell
from .aura import AuraSpell
from .buff_add import AddBuffSpell
from .buff_remove import RemoveBuffSpell
from .switch_side import SwitchSideSpell
from .return_hand import ReturnHandSpell
from .shuffle import ShuffleSpell
from .summon import SummonSpell
from .transform import TransformSpell

def get_spell_class(spell_key):
    if spell_key == "hp":
        return HpSpell
    elif spell_key == "dp":
        return DpSpell
    elif spell_key == "hpdp":
        return HpDpSpell
    elif spell_key == "damage":
        return DamageSpell
    elif spell_key == "draw":
        return DrawSpell
    elif spell_key == "execute":
        return ExecuteSpell
    elif spell_key == "swaphpdp":
        return SwapSpell
    elif spell_key == "restore":
        return RestoreSpell
    elif spell_key == "aura":
        return AuraSpell
    elif spell_key == "addbuff":
        return AddBuffSpell
    elif spell_key == "removebuff":
        return RemoveBuffSpell
    elif spell_key == "control":
        return SwitchSideSpell
    elif spell_key == "returnhand":
        return ReturnHandSpell
    elif spell_key == "shuffle":
        return ShuffleSpell
    elif spell_key == "summon":
        return SummonSpell
    elif spell_key == "transform":
        return TransformSpell
    return None
