from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd
from typing import Optional, Sequence

from ResSimpy.GridArrayFunction import GridArrayFunction


@dataclass
class GridArrayDefinition:
    """Initialises the NexusGrid class.

    Args:
        modifier (Optional[str]): the modifier for the grid array property (e.g. CON, MULT, etc.)
        value (Optional[str]): the actual values for the grid array property in question. Can be an include file.
        mods (Optional[dict[str, pd.DataFrame]): if the grid array has an associated mod card we capture it.
        keyword_in_include_file (bool): an indicator to tell you if the grid array keyword was found in an inc file
    """
    modifier: Optional[str] = None
    value: Optional[str] = None
    # need a parameter for MOD cards
    mods: Optional[dict[str, pd.DataFrame]] = None
    # make a boolean to indicate if a keyword is found in an include file
    # assume initially that it is not
    keyword_in_include_file: bool = False


@dataclass(kw_only=True)
class Grid(ABC):
    # Grid dimensions
    _range_x: Optional[int]
    _range_y: Optional[int]
    _range_z: Optional[int]

    _netgrs: GridArrayDefinition
    _porosity: GridArrayDefinition
    _sw: GridArrayDefinition
    _kx: GridArrayDefinition
    _ky: GridArrayDefinition
    _kz: GridArrayDefinition

    def __init__(self) -> None:
        """Initialises the Grid class."""
        self._netgrs = GridArrayDefinition()
        self._porosity = GridArrayDefinition()
        self._sw = GridArrayDefinition()
        self._kx = GridArrayDefinition()
        self._ky = GridArrayDefinition()
        self._kz = GridArrayDefinition()

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
    def to_dict(self) -> dict[str, Optional[int] | GridArrayDefinition]:
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def update_properties_from_dict(self, data: dict[str, int | GridArrayDefinition]) -> None:
        raise NotImplementedError("Implement this in the derived class")

    @property
    def array_functions(self) -> Optional[Sequence[GridArrayFunction]]:
        """Returns a list of the array functions defined in the structured grid file."""
        raise NotImplementedError("Implement this in the derived class")
