"""Class to represent grid array functions."""
from dataclasses import dataclass
from ResSimpy.Enums.GridFunctionTypes import GridFunctionTypeEnum
from typing import Optional


@dataclass(kw_only=True)
class GridArrayFunction:
    """Class to represent grid array functions.

    Attributes:
        region_type (str): Type of regions in which function input option is applied
        region_number (list[int]): Region numbers, to which function input options are to be applied
        input_array (list[str]): Name of input array(s)
        output_array (list[str]): Name of output array(s)
        function_type (GridFunctionTypeEnum): Analytical function type for function that acts on input arrays
        function_values (list[float]): Coefficients of polynomial or step function
        blocks (list[int]): Range of grid blocks, [i1, i2, j1, j2, k1, k2]
        grid_name (str): Name of grid to which function applies
        input_range (list[tuple[float, float]]): Min-max input range tuples of the input variables
        output_range (list[tuple[float, float]]): Min-max output range tuples of the output variables
        drange (list[float]): List of maximum distances from the input point
    """
    region_type: Optional[str] = None
    region_number: Optional[list[int]] = None
    input_array: Optional[list[str]] = None
    output_array: Optional[list[str]] = None
    function_type: Optional[GridFunctionTypeEnum] = None
    function_values: Optional[list[float]] = None
    blocks: Optional[list[int]] = None
    grid_name: Optional[str] = None
    input_range: Optional[list[tuple[float, float]]] = None
    output_range: Optional[list[tuple[float, float]]] = None
    drange: Optional[list[float]] = None
