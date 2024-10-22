"""Class for collection of Nexus water property methods."""
from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod
from ResSimpy.DataModelBaseClasses.Water import Water


@dataclass(kw_only=True)
class NexusWaterMethods(Water):
    """Class for collection of Nexus water property methods.

    Attributes:
        inputs (dict[int, NexusWaterMethod]): Collection of Nexus water property methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of water property files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusWaterMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusWaterMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        """Initialises the NexusWaterMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusWaterMethod]]): Collection of Nexus water property methods.
            files (Optional[dict[int, NexusFile]]): Collection of water property files, as defined in Nexus fcs file.
                Keyed by the method number.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusWaterMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing water methods."""
        if not self.__properties_loaded:
            self.load_water_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'WATER method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusWaterMethod]:
        """Returns mapping of water property methods as a dictionary where keys are the method number of type int."""
        if not self.__properties_loaded:
            self.load_water_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of 'NexusFile' objects where keys are of type int."""
        return self.__files

    def load_water_methods(self) -> None:
        """Loads water properties from files and initialises NexusWaterMethod object."""
        # Read in water properties from Nexus water method files
        if self.__files is not None and len(self.__files) > 0:  # Check if water files exist
            for table_num in self.__files.keys():  # For each water property method
                water_file = self.__files[table_num]
                if water_file.location is None:
                    raise ValueError(f'Unable to find water file: {water_file}')
                if os.path.isfile(water_file.location):
                    # Create NexusWaterMethod object
                    self.__inputs[table_num] = NexusWaterMethod(file=water_file, input_number=table_num,
                                                                model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with water properties in file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system
