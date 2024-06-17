"""Grid base class."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import pandas as pd
import numpy as np

from typing import Optional, Sequence
from ResSimpy.GridArrayFunction import GridArrayFunction
from ResSimpy.FileOperations import file_operations as fo
from ResSimpy.Utils.general_utilities import check_if_string_is_float
from ResSimpy.File import File


@dataclass
class GridArrayDefinition:
    """A class to define a grid array property.

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

    def load_grid_array_definition_to_file_as_list(self) -> list[str]:
        """Loads the grid array definition to a file as a list of strings."""
        path = self.absolute_path
        if path is None and self.value is not None:
            path = self.value
        elif path is None:
            raise FileNotFoundError('No file path found in the grid array definition')
        return fo.load_file_as_list(path)

    def get_array(self) -> np.ndarray:
        """Returns a 1D numpy array from the grid array definition."""
        file_as_list = self.load_grid_array_definition_to_file_as_list()
        return Grid.grid_file_as_list_to_numpy_array(file_as_list, None, None, None)


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

    @staticmethod
    def filter_grid_array_definition(grid_array_definition: GridArrayDefinition) -> File:
        """Checks array files for only float values and returns a new file with only float values."""
        file_path = grid_array_definition.absolute_path
        if file_path is None and grid_array_definition.value is not None:
            file_path = grid_array_definition.value
        elif file_path is None:
            raise FileNotFoundError('No file path found in the grid array definition')
        file_as_list = fo.load_file_as_list(file_path)

        new_file_as_list = Grid.grid_filter_file_as_list(file_as_list)

        # create a new file with the filtered list
        new_file_path = (os.path.splitext(file_path)[0] + '_filtered' +
                         os.path.splitext(file_path)[1])
        new_grid_file = File(location=new_file_path,
                             file_content_as_list=new_file_as_list,
                             create_as_modified=True,
                             )

        return new_grid_file

    @staticmethod
    def grid_filter_file_as_list(file_as_list: list[str], comment_characters: list[str] | None = None) -> list[str]:
        """Checks array files for only float values and returns a new file with only float values.

        This works for grid arrays only. It does not work well with extremely large files.

        Args:
            file_as_list (list[str]): The file as a list of strings.
            comment_characters (Optional[list[str]]): The comment characters to filter out. Defaults to None.
        """
        if comment_characters is None:
            comment_characters = ['--', '!', 'C']
        if fo.value_in_file('INCLUDE', file_as_list):
            raise NotImplementedError('Nested includes for grid files currently not implemented')
        file_as_list = fo.strip_file_of_comments(file_as_list, comment_characters=comment_characters)
        # remove non float values
        file_as_list = [' '.join([x for x in line.split()
                                  if check_if_string_is_float(x)])+'\n' for line in file_as_list]
        return file_as_list

    @staticmethod
    def grid_file_as_list_to_numpy_array(file_as_list: list[str], x_range: None | int, y_range: None | int,
                                         z_range: None | int) -> np.ndarray:
        """Converts a list of strings to a numpy array."""
        # ensure the list of strings is filtered of comments and non-float values
        new_file_as_list = Grid.grid_filter_file_as_list(file_as_list)

        array_size = -1
        if x_range is not None and y_range is not None and z_range is not None:
            array_size = x_range * y_range * z_range

        grid_array = np.fromstring(' '.join(new_file_as_list), sep=' ', count=array_size)

        return grid_array

    def grid_array_definition_to_numpy_array(self, grid_array_definition: GridArrayDefinition) -> np.ndarray:
        """Converts a grid array to a numpy array."""
        file_as_list = grid_array_definition.load_grid_array_definition_to_file_as_list()
        return self.grid_file_as_list_to_numpy_array(file_as_list, self.range_x, self.range_y, self.range_z)
