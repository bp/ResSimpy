from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusGasliftMethod import NexusGasliftMethod
from ResSimpy.DataModelBaseClasses.Gaslift import Gaslift


@dataclass(kw_only=True)
class NexusGasliftMethods(Gaslift):
    """Class for collection of Nexus gaslift methods.

    Attributes:
        inputs (dict[int, NexusGasliftMethod]): Collection of Nexus gaslift methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of gaslift files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusGasliftMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusGasliftMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        """Initialises the NexusGasliftMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusGasliftMethod]]): Collection of Nexus gaslift methods.
            files (Optional[dict[int, NexusFile]]): Collection of gaslift files, as defined in Nexus fcs file.
            Keyed by the method number.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusGasliftMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing gaslift methods."""
        if not self.__properties_loaded:
            self.load_gaslift_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'GASLIFT method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusGasliftMethod]:
        """Returns mapping of gaslift where keys are of type int.
        If gaslift properties are not loaded, it will load them.
        """
        if not self.__properties_loaded:
            self.load_gaslift_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of Nexus files where keys are of type int."""
        return self.__files

    def load_gaslift_methods(self) -> None:
        """Loads a collection of gaslift method properties from files.
        This method checks if gaslift files are available and reads their properties into the
        'NexusGasliftMethod' objects.
        """
        # Read in gaslift properties from Nexus gaslift method files
        if self.__files is not None and len(self.__files) > 0:  # Check if gaslift files exist
            for table_num in self.__files.keys():  # For each gaslift property method
                gaslift_file = self.__files[table_num]
                if gaslift_file.location is None:
                    raise ValueError(f'Unable to find gaslift file: {gaslift_file}')
                if os.path.isfile(gaslift_file.location):
                    # Create NexusGasliftMethod object
                    self.__inputs[table_num] = NexusGasliftMethod(file=gaslift_file, input_number=table_num,
                                                                  model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with gaslift props in file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system
