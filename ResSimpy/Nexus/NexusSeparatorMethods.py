"""Class for collection of Nexus separator property methods."""
from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusSeparatorMethod import NexusSeparatorMethod
from ResSimpy.Separator import Separator


@dataclass(kw_only=True)
class NexusSeparatorMethods(Separator):
    """Class for collection of Nexus separator property methods.

    Attributes:
        inputs (dict[int, NexusSeparatorMethod]): Dictionary collection of Nexus separator property methods
        files (dict[int, NexusFile]): Dictionary collection of separator property files, defined in Nexus fcs.
    """

    __inputs: MutableMapping[int, NexusSeparatorMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusSeparatorMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusSeparatorMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing separator methods."""
        if not self.__properties_loaded:
            self.load_separator_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'SEPARATOR method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += f'\nSEPARATOR_TYPE: {self.__inputs[table_num].separator_type}\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusSeparatorMethod]:
        if not self.__properties_loaded:
            self.load_separator_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        return self.__files

    def load_separator_methods(self):
        # Read in separator properties from Nexus separator method files
        if self.__files is not None and len(self.__files) > 0:  # Check if separator files exist
            for table_num in self.__files.keys():  # For each separator property method
                separator_file = self.__files[table_num]
                if separator_file.location is None:
                    raise ValueError(f'Unable to find separator file: {separator_file}')
                if os.path.isfile(separator_file.location):
                    # Create NexusSeparatorMethod object
                    self.__inputs[table_num] = NexusSeparatorMethod(file=separator_file, input_number=table_num,
                                                                    model_unit_system=self.__model_unit_system)
                    # Populate object with separator properties in input file
                    self.__inputs[table_num].read_properties()
        self.__properties_loaded = True
