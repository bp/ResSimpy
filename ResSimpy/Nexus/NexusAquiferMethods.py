from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.AquiferMethods import AquiferMethods


@dataclass(kw_only=True)
class NexusAquiferMethods(AquiferMethods):
    """Class for collection of Nexus aquifer methods
    Attributes:
        aquifer_methods (dict[int, NexusAquiferMethod]): Collection of Nexus aquifer methods, as a dictionary
        aquifer_files (dict[int, NexusFile]): Dictionary collection of aquifer files, as defined in Nexus fcs file.
    """

    __aquifer_methods: MutableMapping[int, NexusAquiferMethod]
    __aquifer_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, aquifer_methods: Optional[MutableMapping[int, NexusAquiferMethod]] = None,
                 aquifer_files: Optional[dict[int, NexusFile]] = None) -> None:
        if aquifer_methods:
            self.__aquifer_methods = aquifer_methods
        else:
            self.__aquifer_methods: MutableMapping[int, NexusAquiferMethod] = {}
        if aquifer_files:
            self.__aquifer_files = aquifer_files
        else:
            self.__aquifer_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing aquifer methods."""
        if not self.__properties_loaded:
            self.load_aquifer_methods()
        printable_str = ''
        for table_num in self.__aquifer_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'AQUIFER method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__aquifer_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def aquifer_methods(self) -> MutableMapping[int, NexusAquiferMethod]:
        if not self.__properties_loaded:
            self.load_aquifer_methods()
        return self.__aquifer_methods

    @property
    def aquifer_files(self) -> dict[int, NexusFile]:
        return self.__aquifer_files

    def load_aquifer_methods(self):
        # Read in aquifer properties from Nexus aquifer method files
        if self.__aquifer_files is not None and len(self.__aquifer_files) > 0:  # Check if aquifer files exist
            for table_num in self.__aquifer_files.keys():  # For each aquifer property method
                aquifer_file = self.__aquifer_files[table_num].location
                if aquifer_file is None:
                    raise ValueError(f'Unable to find aquifer file: {aquifer_file}')
                if os.path.isfile(aquifer_file):
                    # Create NexusAquiferMethod object
                    self.__aquifer_methods[table_num] = NexusAquiferMethod(file_path=aquifer_file,
                                                                           method_number=table_num)
                    self.__aquifer_methods[table_num].read_properties()  # Populate object with aquifer props in file
        self.__properties_loaded = True
