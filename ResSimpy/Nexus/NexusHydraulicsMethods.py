from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.HydraulicsMethods import HydraulicsMethods


@dataclass(kw_only=True)
class NexusHydraulicsMethods(HydraulicsMethods):
    """Class for collection of Nexus hydraulics methods
    Attributes:
        hydraulics_methods (dict[int, NexusHydraulicsMethod]): Collection of Nexus hydraulics methods, as a dictionary
        hydraulics_files (dict[int, NexusFile]): Dictionary collection of hydraulics files, in Nexus fcs file.
    """

    __hydraulics_methods: MutableMapping[int, NexusHydraulicsMethod]
    __hydraulics_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, hydraulics_methods: Optional[MutableMapping[int, NexusHydraulicsMethod]] = None,
                 hydraulics_files: Optional[dict[int, NexusFile]] = None) -> None:
        if hydraulics_methods:
            self.__hydraulics_methods = hydraulics_methods
        else:
            self.__hydraulics_methods: MutableMapping[int, NexusHydraulicsMethod] = {}
        if hydraulics_files:
            self.__hydraulics_files = hydraulics_files
        else:
            self.__hydraulics_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing hydraulics methods."""
        if not self.__properties_loaded:
            self.load_hydraulics_methods()
        printable_str = ''
        for table_num in self.__hydraulics_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'HYD method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__hydraulics_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def hydraulics_methods(self) -> MutableMapping[int, NexusHydraulicsMethod]:
        if not self.__properties_loaded:
            self.load_hydraulics_methods()
        return self.__hydraulics_methods

    @property
    def hydraulics_files(self) -> dict[int, NexusFile]:
        return self.__hydraulics_files

    def load_hydraulics_methods(self):
        # Read in hydraulics properties from Nexus hydraulics method files
        if self.__hydraulics_files is not None and len(self.__hydraulics_files) > 0:  # Check if hydraulics files exist
            for table_num in self.__hydraulics_files.keys():  # For each hydraulics property method
                hydraulics_file = self.__hydraulics_files[table_num].location
                if hydraulics_file is None:
                    raise ValueError(f'Unable to find hydraulics file: {hydraulics_file}')
                if os.path.isfile(hydraulics_file):
                    # Create NexusHydraulicsMethod object
                    self.__hydraulics_methods[table_num] = NexusHydraulicsMethod(file_path=hydraulics_file,
                                                                                 method_number=table_num)
                    self.__hydraulics_methods[table_num].read_properties()  # Populate object with hydraulics props
        self.__properties_loaded = True
