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

    def to_string_line(self, header: bool = False) -> str:
        """Convert the NexusFtrans to a string representation for writing to a Nexus file.

        Returns:
            str: The string representation of the NexusFtrans.
        """
        return_string = ''
        if header:
            return_string += "FTRANS\n"
        if self.grid:
            return_string += f"GRID {self.grid}\n"
        if self.fault_name:
            return_string += f"FAULT {self.fault_name}\n"
        return_string += f"{self.i1} {self.j1} {self.k1} {self.i2} {self.j2} {self.k2} {self.value}\n"
        return return_string
