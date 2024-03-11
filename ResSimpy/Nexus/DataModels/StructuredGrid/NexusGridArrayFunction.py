from dataclasses import dataclass
from ResSimpy.Enums.GridFunctionTypes import GridFunctionTypeEnum
from typing import Optional


@dataclass
class NexusGridArrayFunction:
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
