from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class Over(ABC):
    """Used to represent an abstract base of Overrides for transmissibility and pore volumes.

    Attributes:
        array (str): The array to be modified by the over.
        i1 (int): The start of the i range.
        i2 (int): The end of the i range.
        j1 (int): The start of the j range.
        j2 (int): The end of the j range.
        k1 (int): The start of the k range.
        k2 (int): The end of the k range.
        operator (str): The operator to be assigned to the range.
        value (float): The value to be assigned to the range.
        threshold (Optional[float]): The value for which GE or LE is used.
        grid (Optional[str]): The grid that the Over function relates to.
        fault_name (Optional[str]): The named fault that the Over function relates to.
    """
    array: str
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
    array_values: Optional[list[float]] = None
    include_file: Optional[str] = None
