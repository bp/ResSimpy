from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod
from ResSimpy.RelPermMethods import RelPermMethods


@dataclass(kw_only=True)
class NexusRelPermMethods(RelPermMethods):
    """Class for collection of Nexus relative permeability and capillary pressure property methods
    Attributes:
        relperm_methods (dict[int, NexusRelPermMethod]): Collection of Nexus relperm property methods, as a dictionary
        relperm_files (dict[int, NexusFile]): Dictionary collection of relperm property files, as defined in Nexus fcs
    """

    __relperm_methods: MutableMapping[int, NexusRelPermMethod]
    __relperm_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, relperm_methods: Optional[MutableMapping[int, NexusRelPermMethod]] = None,
                 relperm_files: Optional[dict[int, NexusFile]] = None) -> None:
        if relperm_methods:
            self.__relperm_methods = relperm_methods
        else:
            self.__relperm_methods: MutableMapping[int, NexusRelPermMethod] = {}
        if relperm_files:
            self.__relperm_files = relperm_files
        else:
            self.__relperm_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing relative permeability and capillary pressure methods"""
        if not self.__properties_loaded:
            self.load_relperm_methods()
        printable_str = ''
        for table_num in self.__relperm_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'RELPM method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__relperm_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def relperm_methods(self) -> MutableMapping[int, NexusRelPermMethod]:
        if not self.__properties_loaded:
            self.load_relperm_methods()
        return self.__relperm_methods

    @property
    def relperm_files(self) -> dict[int, NexusFile]:
        return self.__relperm_files

    def load_relperm_methods(self):
        # Read in relperm properties from Nexus relperm method files
        if self.__relperm_files is not None and len(self.__relperm_files) > 0:  # Check if relperm files exist
            for table_num in self.__relperm_files.keys():  # For each relperm property method
                relperm_file = self.__relperm_files[table_num].location
                if relperm_file is None:
                    raise ValueError(f'Unable to find relperm file: {relperm_file}')
                if os.path.isfile(relperm_file):
                    # Create NexusRelPermMethod object
                    self.__relperm_methods[table_num] = NexusRelPermMethod(file_path=relperm_file,
                                                                           method_number=table_num)
                    # Populate object with relperm properties in file
                    self.__relperm_methods[table_num].read_properties()
        self.__properties_loaded = True
