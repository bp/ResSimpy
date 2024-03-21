from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from ResSimpy.GridArrayFunction import GridArrayFunction


@dataclass
class VariableEntry:
    modifier: Optional[str] = None
    value: Optional[str] = None


@dataclass(kw_only=True)
class Grid(ABC):
    # Grid dimensions
    _range_x: Optional[int]
    _range_y: Optional[int]
    _range_z: Optional[int]

    _netgrs: VariableEntry
    _porosity: VariableEntry
    _sw: VariableEntry
    _kx: VariableEntry
    _ky: VariableEntry
    _kz: VariableEntry

    def __init__(self) -> None:
        """Initialises the Grid class."""
        self._netgrs = VariableEntry()
        self._porosity = VariableEntry()
        self._sw = VariableEntry()
        self._kx = VariableEntry()
        self._ky = VariableEntry()
        self._kz = VariableEntry()
        # Grid dimensions
        self._range_x: Optional[int] = None
        self._range_y: Optional[int] = None
        self._range_z: Optional[int] = None

    @property
    def range_x(self):
        self.load_grid_properties_if_not_loaded()
        return self._range_x

    @property
    def range_y(self):
        self.load_grid_properties_if_not_loaded()
        return self._range_y

    @property
    def range_z(self):
        self.load_grid_properties_if_not_loaded()
        return self._range_z

    @property
    def netgrs(self):
        self.load_grid_properties_if_not_loaded()
        return self._netgrs

    @property
    def porosity(self):
        self.load_grid_properties_if_not_loaded()
        return self._porosity

    @property
    def sw(self):
        self.load_grid_properties_if_not_loaded()
        return self._sw

    @property
    def kx(self):
        self.load_grid_properties_if_not_loaded()
        return self._kx

    @property
    def ky(self):
        self.load_grid_properties_if_not_loaded()
        return self._ky

    @property
    def kz(self):
        self.load_grid_properties_if_not_loaded()
        return self._kz

    @abstractmethod
    def load_structured_grid_file(self, structure_grid_file, lazy_loading) -> Grid:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def load_grid_properties_if_not_loaded(self) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def to_dict(self) -> dict[str, Optional[int] | VariableEntry]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def update_properties_from_dict(self, data: dict[str, int | VariableEntry]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def array_functions(self) -> Optional[Sequence[GridArrayFunction]]:
        """Returns a list of the array functions defined in the structured grid file."""
        raise NotImplementedError("Implement this in the derived class")
