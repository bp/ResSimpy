from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusGasliftMethod import NexusGasliftMethod
from ResSimpy.GasliftMethods import GasliftMethods


@dataclass(kw_only=True)
class NexusGasliftMethods(GasliftMethods):
    """Class for collection of Nexus gaslift methods
    Attributes:
        gaslift_methods (dict[int, NexusGasliftMethod]): Collection of Nexus gaslift methods, as a dictionary
        gaslift_files (dict[int, NexusFile]): Dictionary collection of gaslift files, as defined in Nexus fcs file.
    """

    __gaslift_methods: MutableMapping[int, NexusGasliftMethod]
    __gaslift_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, gaslift_methods: Optional[MutableMapping[int, NexusGasliftMethod]] = None,
                 gaslift_files: Optional[dict[int, NexusFile]] = None) -> None:
        if gaslift_methods:
            self.__gaslift_methods = gaslift_methods
        else:
            self.__gaslift_methods: MutableMapping[int, NexusGasliftMethod] = {}
        if gaslift_files:
            self.__gaslift_files = gaslift_files
        else:
            self.__gaslift_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing gaslift methods."""
        if not self.__properties_loaded:
            self.load_gaslift_methods()
        printable_str = ''
        for table_num in self.__gaslift_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'GASLIFT method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__gaslift_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def gaslift_methods(self) -> MutableMapping[int, NexusGasliftMethod]:
        if not self.__properties_loaded:
            self.load_gaslift_methods()
        return self.__gaslift_methods

    @property
    def gaslift_files(self) -> dict[int, NexusFile]:
        return self.__gaslift_files

    def load_gaslift_methods(self):
        # Read in gaslift properties from Nexus gaslift method files
        if self.__gaslift_files is not None and len(self.__gaslift_files) > 0:  # Check if gaslift files exist
            for table_num in self.__gaslift_files.keys():  # For each gaslift property method
                gaslift_file = self.__gaslift_files[table_num].location
                if gaslift_file is None:
                    raise ValueError(f'Unable to find gaslift file: {gaslift_file}')
                if os.path.isfile(gaslift_file):
                    # Create NexusGasliftMethod object
                    self.__gaslift_methods[table_num] = NexusGasliftMethod(file_path=gaslift_file,
                                                                           method_number=table_num)
                    self.__gaslift_methods[table_num].read_properties()  # Populate object with gaslift props in file
        self.__properties_loaded = True
