"""Grid base class."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import Optional, Sequence

import numpy as np

from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition
from ResSimpy.DataModelBaseClasses.GridArrayFunction import GridArrayFunction
from ResSimpy.DataModelBaseClasses.Over import Over
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.FileOperations.File import File
from ResSimpy.GenericContainerClasses.LGRs import LGRs


@dataclass(kw_only=True)
class Grid(ABC):
    """A base class to represent a collection of grids in a reservoir simulation model."""
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
    _iregion: dict[str, GridArrayDefinition]
    _grid_properties_loaded: bool = False
    _lgrs: LGRs
    _overs: Sequence[Over]

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
        self._iregion = {}

        # Grid dimensions
        self._range_x: Optional[int] = None
        self._range_y: Optional[int] = None
        self._range_z: Optional[int] = None
        self._grid_properties_loaded = assume_loaded

        # LGRs
        self._lgrs: LGRs = LGRs()

    @property
    def range_x(self) -> int | None:
        """Returns an instance of grid dimensions.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._range_x

    @property
    def range_y(self) -> int | None:
        """Returns an instance of grid dimensions.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._range_y

    @property
    def range_z(self) -> int | None:
        """Returns range_z.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._range_z

    @property
    def netgrs(self) -> GridArrayDefinition:
        """Returns grid array definition for netgrs.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._netgrs

    @property
    def porosity(self) -> GridArrayDefinition:
        """Returns grid porosity.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._porosity

    @property
    def sw(self) -> GridArrayDefinition:
        """Returns water saturation grid.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._sw

    @property
    def sg(self) -> GridArrayDefinition:
        """Returns gas saturation grid.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._sg

    @property
    def pressure(self) -> GridArrayDefinition:
        """Returns grid pressure.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._pressure

    @property
    def temperature(self) -> GridArrayDefinition:
        """Returns grid temperature.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._temperature

    @property
    def kx(self) -> GridArrayDefinition:
        """Returns grid kx.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._kx

    @property
    def ky(self) -> GridArrayDefinition:
        """Returns grid ky.
        Loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._ky

    @property
    def kz(self) -> GridArrayDefinition:
        """Returns grid kz.
        loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._kz

    @property
    def iregion(self) -> dict[str, GridArrayDefinition]:
        """Returns integer regions as dictionary keyed by the name of the array.
        loads grid properties if not loaded.
        """
        self.load_grid_properties_if_not_loaded()
        return self._iregion

    @property
    def lgrs(self) -> LGRs:
        """Returns the LGR module object associated with the grid."""
        return self._lgrs

    @abstractmethod
    def load_structured_grid_file(self, structure_grid_file: File,
                                  model_unit_system: UnitSystem, lazy_loading: bool) -> Grid:
        """Loads in a structured grid file with all grid properties, and the array functions defined with 'FUNCTION'.

        Args:
            structure_grid_file(File, lazy_loading: bool):The NexusFile representation of a structured grid file for
            converting into a structured grid file class.
            lazy_loading(bool): If set to True, parts of the grid will only be loaded in
             when requested via properties on the object.
            model_unit_system(UnitSystem): The default unit system used in the model.
        """
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def load_grid_properties_if_not_loaded(self) -> None:
        """Loads grid properties if not loaded."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def to_dict(self) -> dict[str, Optional[int] | GridArrayDefinition]:
        """Converts object to a dictionary."""
        raise NotImplementedError("Implement this in the derived class")

    @abstractmethod
    def update_properties_from_dict(self, data: dict[str, int | GridArrayDefinition]) -> None:
        """Allows you to update properties on the class using the provided dict of values.

        Args:
            data(dict[str, int | GridArrayDefinition]): Dictionary of values to update on the class.
        """
        raise NotImplementedError("Implement this in the derived class")

    @property
    def array_functions(self) -> Optional[Sequence[GridArrayFunction]]:
        """Returns a list of the array functions defined in the structured grid file."""
        raise NotImplementedError("Implement this in the derived class")

    def grid_array_definition_to_numpy_array(self, grid_array_definition: GridArrayDefinition) -> np.ndarray:
        """Converts a grid array to a numpy array."""
        return grid_array_definition.get_array_from_file(self.range_x, self.range_y, self.range_z)

    @property
    def overs(self) -> Sequence[Over]:
        """Returns the overs associated with the grid."""
        return self._overs
