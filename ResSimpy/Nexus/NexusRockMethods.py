from dataclasses import dataclass
import os
from typing import Optional
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusRockMethod import NexusRockMethod
from ResSimpy.RockMethods import RockMethods


@dataclass(kw_only=True)
class NexusRockMethods(RockMethods):
    """The abstract base class for rock property methods
    Attributes:
        rock_methods (dict[int, NexusRockMethod]): Collection of Nexus rock property methods, as a dictionary
        rock_files (dict[int, NexusFile]): Dictionary collection of rock property files, as defined in Nexus FCS file
    """

    __rock_methods: dict[int, NexusRockMethod]
    __rock_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, rock_methods: Optional[dict[int, NexusRockMethod]] = None,
                 rock_files: Optional[dict[int, NexusFile]] = None):
        if rock_methods:
            self.__rock_methods = rock_methods
        else:
            self.__rock_methods = {}
        if rock_files:
            self.__rock_files = rock_files
        else:
            self.__rock_files = {}
        super().__init__(rock_methods=self.__rock_methods)

    def __repr__(self) -> str:
        """Pretty printing rock methods"""
        if not self.__properties_loaded:
            self.load_rock_methods()
        printable_str = ''
        for table_num in self.__rock_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'ROCK method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__rock_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def rock_methods(self) -> dict[int, NexusRockMethod]:
        if not self.__properties_loaded:
            self.load_rock_methods()
        return self.__rock_methods

    @property
    def rock_files(self) -> dict[int, NexusFile]:
        return self.__rock_files

    def load_rock_methods(self):
        # Read in rock properties from Nexus rock method files
        if self.__rock_files is not None and len(self.__rock_files) > 0:  # Check if rock files exist
            for table_num in self.__rock_files.keys():  # For each rock property method
                rock_file = self.__rock_files[table_num].location
                if rock_file is None:
                    raise ValueError(f'Unable to find rock file: {rock_file}')
                if os.path.isfile(rock_file):
                    # Create NexusRockMethod object
                    self.__rock_methods[table_num] = NexusRockMethod(file_path=rock_file,
                                                                     method_number=table_num)
                    self.__rock_methods[table_num].read_properties()  # Populate object with rock properties in file
        self.__properties_loaded = True
