from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusEquilMethod import NexusEquilMethod
from ResSimpy.EquilMethods import EquilMethods


@dataclass(kw_only=True)
class NexusEquilMethods(EquilMethods):
    """Class for collection of Nexus equilibration methods
    Attributes:
        equil_methods (dict[int, NexusEquilMethod]): Collection of Nexus equilibration methods, as a dictionary
        equil_files (dict[int, NexusFile]): Dictionary collection of equilibration files, as defined in Nexus fcs file
    """

    __equil_methods: MutableMapping[int, NexusEquilMethod]
    __equil_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, equil_methods: Optional[MutableMapping[int, NexusEquilMethod]] = None,
                 equil_files: Optional[dict[int, NexusFile]] = None):
        if equil_methods:
            self.__equil_methods = equil_methods
        else:
            self.__equil_methods: MutableMapping[int, NexusEquilMethod] = {}
        if equil_files:
            self.__equil_files = equil_files
        else:
            self.__equil_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing equil methods"""
        if not self.__properties_loaded:
            self.load_equil_methods()
        printable_str = ''
        for table_num in self.__equil_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'EQUIL method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__equil_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def equil_methods(self) -> MutableMapping[int, NexusEquilMethod]:
        if not self.__properties_loaded:
            self.load_equil_methods()
        return self.__equil_methods

    @property
    def equil_files(self) -> dict[int, NexusFile]:
        return self.__equil_files

    def load_equil_methods(self):
        # Read in equil properties from Nexus equil method files
        if self.__equil_files is not None and len(self.__equil_files) > 0:  # Check if equil files exist
            for table_num in self.__equil_files.keys():  # For each equil property method
                equil_file = self.__equil_files[table_num].location
                if equil_file is None:
                    raise ValueError(f'Unable to find equil file: {equil_file}')
                if os.path.isfile(equil_file):
                    # Create NexusEquilMethod object
                    self.__equil_methods[table_num] = NexusEquilMethod(file_path=equil_file, method_number=table_num)
                    self.__equil_methods[table_num].read_properties()  # Populate object with equil properties in file
        self.__properties_loaded = True
