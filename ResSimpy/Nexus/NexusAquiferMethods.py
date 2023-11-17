"""Class for collecting all the Nexus Aquifer methods."""
from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.Aquifer import Aquifer


@dataclass(kw_only=True)
class NexusAquiferMethods(Aquifer):
    """Class for collection of Nexus aquifer methods.

    Attributes:
        inputs (dict[int, NexusAquiferMethod]): Collection of Nexus aquifer methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of aquifer files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusAquiferMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem, inputs: Optional[MutableMapping[int, NexusAquiferMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusAquiferMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing aquifer methods."""
        if not self.__properties_loaded:
            self.load_aquifer_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'AQUIFER method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusAquiferMethod]:
        if not self.__properties_loaded:
            self.load_aquifer_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        return self.__files

    def load_aquifer_methods(self):
        # Read in aquifer properties from Nexus aquifer method files
        if self.__files is not None and len(self.__files) > 0:  # Check if aquifer files exist
            for table_num in self.__files.keys():  # For each aquifer property method
                aquifer_file = self.__files[table_num]
                if aquifer_file.location is None:
                    raise ValueError(f'Unable to find aquifer file: {aquifer_file.location}')
                if os.path.isfile(aquifer_file.location):
                    # Create NexusAquifer object
                    self.__inputs[table_num] = NexusAquiferMethod(file=aquifer_file, input_number=table_num,
                                                                  model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with aquifer properties from file
        self.__properties_loaded = True
