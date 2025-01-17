from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class NexusTOver(ABC):
    """Used to represent an abstract base of Overrides for transmissibility arrays using values per cell.

    Attributes:
        array (str): The array to be modified by the over.
        i1 (int): The start of the i range.
        i2 (int): The end of the i range.
        j1 (int): The start of the j range.
        j2 (int): The end of the j range.
        k1 (int): The start of the k range.
        k2 (int): The end of the k range.
        operator (str): The operator to be assigned to the range.
        grid (Optional[str]): The grid that the Over function relates to.
        include_file (str): The include file that the TOver function reads values from.
    """
    array: str
    i1: int
    i2: int
    j1: int
    j2: int
    k1: int
    k2: int
    operator: str
    grid: Optional[str] = None
    include_file: str = None
