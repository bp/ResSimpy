from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import pandas as pd
from typing import Optional, Sequence, TYPE_CHECKING
from ResSimpy.GridArrayFunction import GridArrayFunction

if TYPE_CHECKING:
    from ResSimpy.File import File


@dataclass
class GridArrayDefinition:
    """Initialises the NexusGrid class.

    Args:
        modifier (Optional[str]): the modifier for the grid array property (e.g. CON, MULT, etc.)
        value (Optional[str]): the actual values for the grid array property in question. Can be an include file.
        mods (Optional[dict[str, pd.DataFrame]): if the grid array has an associated mod card we capture it.
        keyword_in_include_file (bool): an indicator to tell you if the grid array keyword was found in an inc file
        absolute_path (Optional[str]): the absolute path to the path if value is an include file.
    """
    modifier: Optional[str] = None
    value: Optional[str] = None
    mods: Optional[dict[str, pd.DataFrame]] = None
    keyword_in_include_file: bool = False
    absolute_path: Optional[str] = None


@dataclass(kw_only=True)
class Grid(ABC):
    # Grid dimensions
    _range_x: Optional[int]
    _range_y: Optional[int]
    _range_z: Optional[int]

    _netgrs: GridArrayDefinition
    _porosity: GridArrayDefinition
    _sw: GridArrayDefinition
    _sg: GridArrayDefinition
    _pressure: GridArrayDefinition
    _temperature: GridArrayDefinition
    _kx: GridArrayDefinition
    _ky: GridArrayDefinition
    _kz: GridArrayDefinition
    _grid_properties_loaded: bool = False

    def __init__(self, assume_loaded: bool = False) -> None:
        """Initialises the Grid class."""
        self._netgrs = GridArrayDefinition()
        self._porosity = GridArrayDefinition()
        self._sw = GridArrayDefinition()
        self._sg = GridArrayDefinition()
        self._pressure = GridArrayDefinition()
        self._temperature = GridArrayDefinition()
        self._kx = GridArrayDefinition()
        self._ky = GridArrayDefinition()
        self._kz = GridArrayDefinition()

        # Grid dimensions
        self._range_x: Optional[int] = None
        self._range_y: Optional[int] = None
        self._range_z: Optional[int] = None
        self._grid_properties_loaded = assume_loaded

    @property
    def range_x(self) -> int | None:
        self.load_grid_properties_if_not_loaded()
        return self._range_x

    @property
    def range_y(self) -> int | None:
        self.load_grid_properties_if_not_loaded()
        return self._range_y

    @property
    def range_z(self) -> int | None:
        self.load_grid_properties_if_not_loaded()
        return self._range_z

    @property
    def netgrs(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._netgrs

    @property
    def porosity(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._porosity

    @property
    def sw(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._sw

    @property
    def sg(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._sg

    @property
    def pressure(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._pressure

    @property
    def temperature(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._temperature

    @property
    def kx(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._kx

    @property
    def ky(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._ky

    @property
    def kz(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self._kz

    @abstractmethod
    def load_structured_grid_file(self, structure_grid_file: File, lazy_loading: bool) -> Grid:
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
