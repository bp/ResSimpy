"""Base class for handling any dynamic property simulator inputs, for use in inputs such as PVT, relperm, etc."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd
from typing import Optional, Union
from ResSimpy.FileOperations.File import File
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass
class DynamicProperty(ABC):
    """The abstract base class for dynamic property simulator inputs, for use in inputs such as PVT, relperm, etc.

    Attributes:
        input_number (int): Method, table or input number, in order as entered in the simulation input deck.
    """

    properties: dict
    input_number: int = field(compare=False)
    file: File = field(compare=False)

    def __init__(self, input_number: int, file: File) -> None:
        """Initialises the DynamicProperty class.

        Args:
            input_number (int): Method, table or input number, in order as entered in the simulation input deck.
            file (File): The File that the dynamic property is read from.
        """
        self.input_number: int = input_number
        self.file: File = file

    @property
    @abstractmethod
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the constraint."""
        raise NotImplementedError('Implement in the derived class.')

    def __repr__(self) -> str:
        """Repr for dynamic property data."""
        printable_str = f'\nFILE_PATH: {self.file.location}\n\n'
        printable_str += self.to_string()
        return printable_str

    def __str__(self) -> str:
        """Pretty printing dynamic property in human-readable format, e.g. output of print function."""
        printable_str = f'\nFILE_PATH: {self.file.location}\n\n'
        printable_str += self.to_string()
        return printable_str

    def to_string(self) -> str:
        """Write dynamic property data to string."""
        raise NotImplementedError('Implement in the derived class.')

    def write_to_file(self, new_file_path: Optional[str] = None, overwrite_file: bool = False) -> None:
        """Write dynamic property data to file."""
        printable_str = self.to_string()
        new_file_contents = printable_str.splitlines(keepends=True)
        if overwrite_file is True and new_file_path is not None:
            raise ValueError('Please specify only one of either overwrite_existing or new_file_location.')

        if new_file_path is not None:
            new_file = File(file_content_as_list=new_file_contents, location=new_file_path, create_as_modified=True)
            new_file.write_to_file(new_file_path=new_file_path, overwrite_file=True)
            return
        elif overwrite_file is False:
            raise ValueError('Please specify either overwrite_file as True or provide new_file_location.')

        # Overwriting existing file contents
        if overwrite_file is True:
            self.file.file_content_as_list = new_file_contents
            self.file.write_to_file(overwrite_file=overwrite_file)

    @property
    def ranges(self) -> dict[str, tuple[float, float]]:
        """Returns a dictionary of the ranges of the dynamic properties."""
        ranges: dict[str, tuple[float, float]] = {}
        for prop, prop_value in self.properties.items():
            existing_range: tuple[float, float] = ranges.get(prop, (np.nan, np.nan))
            if isinstance(prop_value, pd.DataFrame):
                for col in prop_value.columns:
                    existing_range = ranges.get(col, (np.nan, np.nan))
                    ranges[col] = (np.nanmin((*existing_range, prop_value[col].min())),
                                   np.nanmax((*existing_range, prop_value[col].max())))
            elif isinstance(prop_value, np.ndarray):
                ranges[prop] = (np.nanmin((*existing_range, min(prop_value))),
                                np.nanmax((*existing_range, max(prop_value))))
            elif isinstance(prop_value, str):
                # try to convert the string to a list of floats
                split_prop_value = prop_value.split()
                try:
                    split_prop_value_as_float = [float(val) for val in split_prop_value]
                except ValueError:
                    # if it can't be converted to a list of floats, then continue to the next property
                    continue
                if len(split_prop_value_as_float) == 0:
                    # skip if the list is empty
                    continue
                ranges[prop] = (np.nanmin((*existing_range, min(split_prop_value_as_float))),
                                np.nanmax((*existing_range, max(split_prop_value_as_float))))
            elif isinstance(prop_value, float):
                ranges[prop] = (prop_value, prop_value)
            else:
                continue
        return ranges

    @staticmethod
    def convert_to_hashable(value: Union[str, float, pd.DataFrame, list[str], dict[str, float],
                                         tuple[str, dict[str, float]], dict[str, pd.DataFrame], np.ndarray,
                                         dict[str, Union[float, pd.DataFrame]]]) -> Union[str, float, tuple, frozenset]:
        """Converts a value of a mix of datatypes and nested dictionaries to a hashable value."""
        if isinstance(value, pd.DataFrame):
            pd_hash = pd.util.hash_pandas_object(value)
            return tuple(pd_hash.values)
        elif isinstance(value, np.ndarray):
            return np.array2string(value)
        elif isinstance(value, list):
            return tuple(value)
        elif isinstance(value, dict):
            return frozenset((k, DynamicProperty.convert_to_hashable(v)) for k, v in value.items())
        elif isinstance(value, Enum):
            return value.value
        else:
            return value

    def __hash__(self) -> int:
        """Returns the hash of the object. Excludes the file and input number attributes."""
        property_hash = self.convert_to_hashable(self.properties)
        return hash(property_hash)
