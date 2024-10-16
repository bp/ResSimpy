"""Class for collection of Nexus rock property methods."""
from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusRockMethod import NexusRockMethod
from ResSimpy.DataModelBaseClasses.Rock import Rock


@dataclass(kw_only=True)
class NexusRockMethods(Rock):
    """Class for collection of Nexus rock property methods.

    Attributes:
        inputs (dict[int, NexusRockMethod]): Collection of Nexus rock property methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of rock property files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusRockMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusRockMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        """Initialises the NexusRockMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusRockMethod]]): Collection of Nexus rock property methods.
            files (Optional[dict[int, NexusFile]]): Collection of rock property files, as defined in Nexus fcs file.
                Keyed by the method number.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusRockMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing rock methods."""
        if not self.__properties_loaded:
            self.load_rock_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'ROCK method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusRockMethod]:
        """Returns mapping of Nexus rock properties.
        If properties have not been loaded, it loads them first.
        """
        if not self.__properties_loaded:
            self.load_rock_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of NexusFile where keys are of type int."""
        return self.__files

    def load_rock_methods(self) -> None:
        """Loads rock property files from Nexus fcs file."""
        # Read in rock properties from Nexus rock method files
        if self.__files is not None and len(self.__files) > 0:  # Check if rock files exist
            for table_num in self.__files.keys():  # For each rock property method
                rock_file = self.__files[table_num]
                if rock_file.location is None:
                    raise ValueError(f'Unable to find rock file: {rock_file}')
                if os.path.isfile(rock_file.location):
                    # Create NexusRockMethod object
                    self.__inputs[table_num] = NexusRockMethod(file=rock_file, input_number=table_num,
                                                               model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with rock properties in file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system
