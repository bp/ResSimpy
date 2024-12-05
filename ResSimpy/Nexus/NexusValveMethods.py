"""Class for collection of Nexus valve property methods."""
from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusValveMethod import NexusValveMethod
from ResSimpy.DataModelBaseClasses.Valve import Valve


@dataclass(kw_only=True)
class NexusValveMethods(Valve):
    """Class for collection of Nexus valve property inputs.

    Attributes:
        inputs (dict[int, NexusValveMethod]): Collection of Nexus valve property methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of valve property files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusValveMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusValveMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        """Initialises the NexusValveMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusValveMethod]]): Collection of Nexus valve property methods.
            files (Optional[dict[int, NexusFile]]): Collection of valve property files, as defined in Nexus fcs file.
                Keyed by the method number.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusValveMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing valve methods."""
        if not self.__properties_loaded:
            self.load_valve_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'VALVE method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusValveMethod]:
        """Returns mapping of valve properties as a dictionary where keys are of type int."""
        if not self.__properties_loaded:
            self.load_valve_methods()
        return self.__inputs

    @property
    def valve_files(self) -> dict[int, NexusFile]:
        """Returns dictionary of valve files."""
        return self.__files

    def load_valve_methods(self) -> None:
        """Loads valve methods from files and initialises 'NexusValveMethod' object."""
        # Read in valve properties from Nexus valve method files
        if self.__files is not None and len(self.__files) > 0:  # Check if valve files exist
            for table_num in self.__files.keys():  # For each valve property method
                valve_file = self.__files[table_num]
                if valve_file.location is None:
                    raise ValueError(f'Unable to find valve file: {valve_file}')
                if os.path.isfile(valve_file.location):
                    # Create NexusValveMethod object
                    self.__inputs[table_num] = NexusValveMethod(file=valve_file, input_number=table_num,
                                                                model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with valve properties in file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system
