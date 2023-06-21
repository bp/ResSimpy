from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusValveMethod import NexusValveMethod
from ResSimpy.Valve import Valve


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

    def __init__(self, inputs: Optional[MutableMapping[int, NexusValveMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusValveMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
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
        if not self.__properties_loaded:
            self.load_valve_methods()
        return self.__inputs

    @property
    def valve_files(self) -> dict[int, NexusFile]:
        return self.__files

    def load_valve_methods(self):
        # Read in valve properties from Nexus valve method files
        if self.__files is not None and len(self.__files) > 0:  # Check if valve files exist
            for table_num in self.__files.keys():  # For each valve property method
                valve_file = self.__files[table_num].location
                if valve_file is None:
                    raise ValueError(f'Unable to find valve file: {valve_file}')
                if os.path.isfile(valve_file):
                    # Create NexusValveMethod object
                    self.__inputs[table_num] = NexusValveMethod(file_path=valve_file, input_number=table_num)
                    self.__inputs[table_num].read_properties()  # Populate object with valve properties in file
        self.__properties_loaded = True
