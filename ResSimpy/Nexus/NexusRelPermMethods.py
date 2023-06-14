from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod
from ResSimpy.RelPerm import RelPerm


@dataclass(kw_only=True)
class NexusRelPermMethods(RelPerm):
    """Class for collection of Nexus relative permeability and capillary pressure property inputs.

    Attributes:
        inputs (dict[int, NexusRelPermMethod]): Collection of Nexus relperm property inputs, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of relperm property files, as defined in Nexus fcs.
    """

    __inputs: MutableMapping[int, NexusRelPermMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, inputs: Optional[MutableMapping[int, NexusRelPermMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None) -> None:
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusRelPermMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing relative permeability and capillary pressure methods."""
        if not self.__properties_loaded:
            self.load_relperm_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'RELPM method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusRelPermMethod]:
        if not self.__properties_loaded:
            self.load_relperm_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        return self.__files

    def load_relperm_methods(self):
        # Read in relperm properties from Nexus relperm method files
        if self.__files is not None and len(self.__files) > 0:  # Check if relperm files exist
            for table_num in self.__files.keys():  # For each relperm property method
                relperm_file = self.__files[table_num].location
                if relperm_file is None:
                    raise ValueError(f'Unable to find relperm file: {relperm_file}')
                if os.path.isfile(relperm_file):
                    # Create NexusRelPermMethod object
                    self.__inputs[table_num] = NexusRelPermMethod(file_path=relperm_file, input_number=table_num)
                    # Populate object with relperm properties in file
                    self.__inputs[table_num].read_properties()
        self.__properties_loaded = True
