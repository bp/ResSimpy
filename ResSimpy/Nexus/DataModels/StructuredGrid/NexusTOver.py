from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.Over import Over


@dataclass(kw_only=True)
class NexusTOver(Over):
    """Used to represent an Override for transmissibility arrays using values per cell.

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
    include_file: Optional[str]
    grid: Optional[str] = None
    array_values: Optional[list[float]] = None
