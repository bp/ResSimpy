from dataclasses import dataclass
import os
from typing import Optional, MutableMapping
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod
from ResSimpy.WaterMethods import WaterMethods


@dataclass(kw_only=True)
class NexusWaterMethods(WaterMethods):
    """Class for collection of Nexus water property methods
    Attributes:
        water_methods (dict[int, NexusWaterMethod]): Collection of Nexus water property methods, as a dictionary
        water_files (dict[int, NexusFile]): Dictionary collection of water property files, as defined in Nexus fcs file
    """

    __water_methods: MutableMapping[int, NexusWaterMethod]
    __water_files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading

    def __init__(self, water_methods: Optional[MutableMapping[int, NexusWaterMethod]] = None,
                 water_files: Optional[dict[int, NexusFile]] = None) -> None:
        if water_methods:
            self.__water_methods = water_methods
        else:
            self.__water_methods: MutableMapping[int, NexusWaterMethod] = {}
        if water_files:
            self.__water_files = water_files
        else:
            self.__water_files = {}
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing water methods"""
        if not self.__properties_loaded:
            self.load_water_methods()
        printable_str = ''
        for table_num in self.__water_methods.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'WATER method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__water_methods[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def water_methods(self) -> MutableMapping[int, NexusWaterMethod]:
        if not self.__properties_loaded:
            self.load_water_methods()
        return self.__water_methods

    @property
    def water_files(self) -> dict[int, NexusFile]:
        return self.__water_files

    def load_water_methods(self):
        # Read in water properties from Nexus water method files
        if self.__water_files is not None and len(self.__water_files) > 0:  # Check if water files exist
            for table_num in self.__water_files.keys():  # For each water property method
                water_file = self.__water_files[table_num].location
                if water_file is None:
                    raise ValueError(f'Unable to find water file: {water_file}')
                if os.path.isfile(water_file):
                    # Create NexusWaterMethod object
                    self.__water_methods[table_num] = NexusWaterMethod(file_path=water_file, method_number=table_num)
                    self.__water_methods[table_num].read_properties()  # Populate object with water properties in file
        self.__properties_loaded = True
