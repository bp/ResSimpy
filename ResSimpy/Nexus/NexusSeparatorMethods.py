from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusSeparatorMethod import NexusSeparatorMethod
from ResSimpy.SeparatorMethods import SeparatorMethods


@dataclass(kw_only=True)
class NexusSeparatorMethods(SeparatorMethods):
    """Class for collection of Nexus separator property methods
    Attributes:
        separator_methods (dict[int, NexusSeparatorMethod]): Dictionary collection of Nexus separator property methods
        separator_files (dict[int, NexusFile]): Dictionary collection of separator property files, defined in Nexus fcs.
    """

    __separator_methods: MutableMapping[int, NexusSeparatorMethod]
    __separator_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, separator_methods: Optional[MutableMapping[int, NexusSeparatorMethod]] = None,
                 separator_files: Optional[dict[int, NexusFile]] = None) -> None:
        if separator_methods:
            self.__separator_methods = separator_methods
        else:
            self.__separator_methods: MutableMapping[int, NexusSeparatorMethod] = {}
        if separator_files:
            self.__separator_files = separator_files
        else:
            self.__separator_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing separator methods."""
        if not self.__properties_loaded:
            self.load_separator_methods()
        printable_str = ''
        for table_num in self.__separator_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'SEPARATOR method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__separator_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def separator_methods(self) -> MutableMapping[int, NexusSeparatorMethod]:
        if not self.__properties_loaded:
            self.load_separator_methods()
        return self.__separator_methods

    @property
    def separator_files(self) -> dict[int, NexusFile]:
        return self.__separator_files

    def load_separator_methods(self):
        # Read in separator properties from Nexus separator method files
        if self.__separator_files is not None and len(self.__separator_files) > 0:  # Check if separator files exist
            for table_num in self.__separator_files.keys():  # For each separator property method
                separator_file = self.__separator_files[table_num].location
                if separator_file is None:
                    raise ValueError(f'Unable to find separator file: {separator_file}')
                if os.path.isfile(separator_file):
                    # Create NexusSeparatorMethod object
                    self.__separator_methods[table_num] = NexusSeparatorMethod(file_path=separator_file,
                                                                               method_number=table_num)
                    # Populate object with separator properties in input file
                    self.__separator_methods[table_num].read_properties()
        self.__properties_loaded = True
