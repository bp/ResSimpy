from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from ResSimpy.FileOperations.File import File
from ResSimpy.FileOperations import file_operations as fo
from ResSimpy.Utils.grid_filtering_functions import grid_filter_file_as_list, filter_grid_array_definition


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
    array: Optional[np.ndarray] = None

    def load_grid_array_definition_to_file_as_list(self) -> list[str]:
        """Loads the grid array definition to a file as a list of strings."""
        path = self.absolute_path
        if path is None and self.value is not None:
            sanitised_value = "".join(fo.strip_file_of_comments(self.value.splitlines()))
            # If the value is a path, load that file in. Otherwise, assume it is a grid array value.
            if sanitised_value.upper().isupper():  # Fastest way to check if there are any letters in a string
                path = self.value
            else:
                return sanitised_value.splitlines()
        elif path is None:
            raise FileNotFoundError('No file path found in the grid array definition')
        return fo.load_file_as_list(path)

    def get_array_from_file(self, x_range: None | int = None, y_range: None | int = None,
                            z_range: None | int = None) -> np.ndarray:
        """Returns a 1D numpy array from the grid array definition."""
        if self.array is not None:
            return self.array
        file_as_list = self.load_grid_array_definition_to_file_as_list()
        self.array = self.grid_file_as_list_to_numpy_array(file_as_list, x_range, y_range, z_range)
        return self.array

    def filtered_grid_array_def_as_file(self) -> File:
        """Filters the grid array definition."""
        return filter_grid_array_definition(self)

    @staticmethod
    def grid_file_as_list_to_numpy_array(file_as_list: list[str], x_range: None | int, y_range: None | int,
                                         z_range: None | int) -> np.ndarray:
        """Converts a list of strings to a numpy array."""
        # ensure the list of strings is filtered of comments and non-float values
        new_file_as_list = grid_filter_file_as_list(file_as_list)

        array_size = -1
        if x_range is not None and y_range is not None and z_range is not None:
            array_size = x_range * y_range * z_range

        grid_array = np.fromstring(' '.join(new_file_as_list), sep=' ', count=array_size)

        return grid_array

    def _get_array_or_value(self) -> np.ndarray | float:
        """Returns the array or value based on the modifier."""
        if self.modifier == 'VALUE':
            return self.get_array_from_file()
        elif self.modifier == 'CON':
            if self.value is None:
                raise ValueError('No value found for grid array definition.')
            return float(self.value)
        else:
            raise NotImplementedError('Only VALUE and CON are modifiers supported for grid array definitions.')

    def min(self) -> float:
        """Returns the minimum value of the grid array property."""
        array_or_value = self._get_array_or_value()
        if isinstance(array_or_value, float):
            return array_or_value
        else:
            return array_or_value.min()

    def max(self) -> float:
        """Returns the maximum value of the grid array property."""
        array_or_value = self._get_array_or_value()
        if isinstance(array_or_value, float):
            return array_or_value
        else:
            return array_or_value.max()

    def get_array(self) -> np.ndarray:
        """Returns the array from the grid array definition."""
        return self.get_array_from_file()
