from dataclasses import dataclass
from typing import Optional


@dataclass
class NexusOver:
    """Used to represent a line from an OVER table in a Nexus file.

    Attributes:
        arrays (list[str]): The arrays to be modified by the over.
        i1 (int): The start of the i range.
        i2 (int): The end of the i range.
        j1 (int): The start of the j range.
        j2 (int): The end of the j range.
        k1 (int): The start of the k range.
        k2 (int): The end of the k range.
        operator (str): The operator to be assigned to the range.
        value (float): The value to be assigned to the range.
        threshold (float): The value for which GE or LE is used.
    """
    arrays: list[str]
    i1: int
    i2: int
    j1: int
    j2: int
    k1: int
    k2: int
    operator: str
    value: float
    threshold: Optional[float] = None
    grid: Optional[str] = None
    fault_name: Optional[str] = None

    def to_string(self) -> str:
        """Converts the over to a string for writing to a Nexus file."""
        return_str = 'OVER'
        for array in self.arrays:
            return_str += f" {self.arrays}"
        return_str += '\n'
        if self.grid:
            return_str += f"GRID {self.grid}\n"
        if self.fault_name:
            return_str += f"FNAME {self.fault_name}\n"
        return f"{self.i1}\t{self.i2}\t{self.j1}\t{self.j2}\t{self.k1}\t{self.k2}\t{self.operator}{self.value}\n"
