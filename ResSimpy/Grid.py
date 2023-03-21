from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional


@dataclass
class VariableEntry:
    modifier: Optional[str] = None
    value: Optional[str] = None


@dataclass(kw_only=True)
class Grid(ABC):
    # Grid dimensions
    range_x: Optional[int]
    range_y: Optional[int]
    range_z: Optional[int]

    netgrs: VariableEntry = VariableEntry()
    porosity: VariableEntry = VariableEntry()
    sw: VariableEntry = VariableEntry()
    kx: VariableEntry = VariableEntry()
    ky: VariableEntry = VariableEntry()
    kz: VariableEntry = VariableEntry()

    def __init__(self):
        self.netgrs = VariableEntry()
        self.porosity = VariableEntry()
        self.sw = VariableEntry()
        self.kx = VariableEntry()
        self.ky = VariableEntry()
        self.kz = VariableEntry()
        # Grid dimensions
        self.range_x: Optional[int] = None
        self.range_y: Optional[int] = None
        self.range_z: Optional[int] = None

    def load_structured_grid_file(self, structure_grid_file) -> Grid:
        raise NotImplementedError("Implement this in the derived class")
