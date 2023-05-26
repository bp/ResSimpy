from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusValveMethod import NexusValveMethod
from ResSimpy.ValveMethods import ValveMethods


@dataclass(kw_only=True)
class NexusValveMethods(ValveMethods):
    """Class for collection of Nexus valve property methods
    Attributes:
        valve_methods (dict[int, NexusValveMethod]): Collection of Nexus valve property methods, as a dictionary
        valve_files (dict[int, NexusFile]): Dictionary collection of valve property files, as defined in Nexus fcs file.
    """

    __valve_methods: MutableMapping[int, NexusValveMethod]
    __valve_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, valve_methods: Optional[MutableMapping[int, NexusValveMethod]] = None,
                 valve_files: Optional[dict[int, NexusFile]] = None) -> None:
        if valve_methods:
            self.__valve_methods = valve_methods
        else:
            self.__valve_methods: MutableMapping[int, NexusValveMethod] = {}
        if valve_files:
            self.__valve_files = valve_files
        else:
            self.__valve_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing valve methods."""
        if not self.__properties_loaded:
            self.load_valve_methods()
        printable_str = ''
        for table_num in self.__valve_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'VALVE method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__valve_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def valve_methods(self) -> MutableMapping[int, NexusValveMethod]:
        if not self.__properties_loaded:
            self.load_valve_methods()
        return self.__valve_methods

    @property
    def valve_files(self) -> dict[int, NexusFile]:
        return self.__valve_files

    def load_valve_methods(self):
        # Read in valve properties from Nexus valve method files
        if self.__valve_files is not None and len(self.__valve_files) > 0:  # Check if valve files exist
            for table_num in self.__valve_files.keys():  # For each valve property method
                valve_file = self.__valve_files[table_num].location
                if valve_file is None:
                    raise ValueError(f'Unable to find valve file: {valve_file}')
                if os.path.isfile(valve_file):
                    # Create NexusValveMethod object
                    self.__valve_methods[table_num] = NexusValveMethod(file_path=valve_file, method_number=table_num)
                    self.__valve_methods[table_num].read_properties()  # Populate object with valve properties in file
        self.__properties_loaded = True
