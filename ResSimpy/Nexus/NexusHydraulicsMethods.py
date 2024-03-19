from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Hydraulics import Hydraulics


@dataclass(kw_only=True)
class NexusHydraulicsMethods(Hydraulics):
    """Class for collection of Nexus hydraulics methods.

    Attributes:
        inputs (dict[int, NexusHydraulicsMethod]): Collection of Nexus hydraulics methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of hydraulics files, in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusHydraulicsMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusHydraulicsMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        """Initialises the NexusHydraulicsMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusHydraulicsMethod]]): Collection of Nexus hydraulics methods.
            files (Optional[dict[int, NexusFile]]): Collection of hydraulics files, as defined in Nexus fcs file.
                Keyed by the method number.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusHydraulicsMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing hydraulics methods."""
        if not self.__properties_loaded:
            self.load_hydraulics_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'HYD method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusHydraulicsMethod]:
        if not self.__properties_loaded:
            self.load_hydraulics_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        return self.__files

    def load_hydraulics_methods(self):
        # Read in hydraulics properties from Nexus hydraulics method files
        if self.__files is not None and len(self.__files) > 0:  # Check if hydraulics files exist
            for table_num in self.__files.keys():  # For each hydraulics property method
                hydraulics_file = self.__files[table_num]
                if hydraulics_file.location is None:
                    raise ValueError(f'Unable to find hydraulics file: {hydraulics_file}')
                if os.path.isfile(hydraulics_file.location):
                    # Create NexusHydraulicsMethod object
                    self.__inputs[table_num] = NexusHydraulicsMethod(file=hydraulics_file, input_number=table_num,
                                                                     model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with hydraulics props
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system
