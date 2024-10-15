"""Class for collection of Nexus PVT property methods."""

from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusPVTMethod import NexusPVTMethod
from ResSimpy.DataModelBaseClasses.PVT import PVT


@dataclass(kw_only=True)
class NexusPVTMethods(PVT):
    """Class for collection of Nexus PVT property methods.

    Attributes:
        inputs (dict[int, NexusPVTMethod]): Collection of Nexus PVT property methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of PVT property files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusPVTMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem, inputs: Optional[MutableMapping[int, NexusPVTMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        """Initialises the NexusPVTMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusPVTMethod]]): Collection of Nexus PVT property methods.
            files (Optional[dict[int, NexusFile]]): Collection of PVT property files, as defined in Nexus fcs file.
                Keyed by the method number.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusPVTMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing pvt methods."""
        if not self.__properties_loaded:
            self.load_pvt_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'PVT method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusPVTMethod]:
        """Returns mapping of Nexus PVT property methods.
        If properties are not loaded, it will load them first.
        """
        if not self.__properties_loaded:
            self.load_pvt_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of Nexus files."""
        return self.__files

    def load_pvt_methods(self) -> None:
        """Loads a collection of pvt properties from Nexus pvt method files."""
        # Read in pvt properties from Nexus pvt method files
        if self.__files is not None and len(self.__files) > 0:  # Check if pvt files exist
            for table_num in self.__files.keys():  # For each pvt property method
                pvt_file = self.__files[table_num]
                if pvt_file.location is None:
                    raise ValueError(f'Unable to find pvt file: {pvt_file}')
                if os.path.isfile(pvt_file.location):
                    # Create NexusPVTMethod object
                    self.__inputs[table_num] = NexusPVTMethod(file=pvt_file, input_number=table_num,
                                                              model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with pvt properties in file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system

    @property
    def summary(self) -> str:
        """Returns a string summary of 'NexusPVTMethods' inputs in a dictionary."""
        pvt_summary = ''
        for key, value in self.inputs.items():
            pvt_summary += f'        {key}: {value.file.location}\n'
        return pvt_summary
