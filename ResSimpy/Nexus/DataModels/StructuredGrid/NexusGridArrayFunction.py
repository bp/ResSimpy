"""Class to represent Nexus grid array functions."""
from dataclasses import dataclass
from typing import Optional
import pandas as pd

from ResSimpy.GridArrayFunction import GridArrayFunction


@dataclass
class NexusGridArrayFunction(GridArrayFunction):
    """Class to hold Nexus grid array function attributes.

    Attributes:
        function_table (pd.DataFrame): Dependency between input and output grid arrays, represented in tabular form
        function_table_m (int): Maximum number of function table entries which can be used in tabular interpolation
        function_table_p_list (list[float]): Shifts of the first, second, ..., and N-th input arrays
    """

    function_table: Optional[pd.DataFrame] = None
    function_table_m: Optional[int] = None
    function_table_p_list: Optional[list[float]] = None
