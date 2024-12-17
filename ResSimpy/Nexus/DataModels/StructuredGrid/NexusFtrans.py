from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.Ftrans import Ftrans
from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass
class NexusFtrans(Ftrans):
    """Used to represent an abstract base of Ftrans for transmissibility modification by cell.

    Attributes:
        i1 (int): i coordinate of the first cell
        i2 (int): i coordinate of the second cell
        j1 (int): j coordinate of the first cell
        j2 (int): j coordinate of the second cell
        k1 (int): k coordinate of the first cell
        k2 (int): k coordinate of the second cell
        value (float): The value to be assigned to the range.
        grid (Optional[str]): The grid that the Over function relates to.
        fault_name (Optional[str]): The named fault that the Over function relates to.
    """
    i1: int
    i2: int
    j1: int
    j2: int
    k1: int
    k2: int
    value: float
    unit_system: UnitSystem
    grid: Optional[str] = None
    fault_name: Optional[str] = None
