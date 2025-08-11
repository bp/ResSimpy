"""Class for collection of Nexus water property methods."""
from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import Optional, MutableMapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod
from ResSimpy.DataModelBaseClasses.Water import Water
from ResSimpy.Utils.dynamic_method_manipulations import add_dynamic_method


@dataclass(kw_only=True)
class NexusWaterMethods(Water):
    """Class for collection of Nexus water property methods.

    Attributes:
        inputs (dict[int, NexusWaterMethod]): Collection of Nexus water property methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of water property files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusWaterMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem
    _model_files: Optional[FcsNexusFile] = field(default=None, repr=False, compare=False)

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusWaterMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None, assume_loaded: bool = False,
                 model_files: Optional[FcsNexusFile] = None) -> None:
        """Initialises the NexusWaterMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusWaterMethod]]): Collection of Nexus water property methods.
            files (Optional[dict[int, NexusFile]]): Collection of water property files, as defined in Nexus fcs file.
                Keyed by the method number.
            assume_loaded (bool): If True, assumes that the water methods have already been loaded.
            model_files (Optional[FcsNexusFile]): The FCS file containing the whole set of Nexus files.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusWaterMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        self.__properties_loaded = assume_loaded
        self._model_files = model_files
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing water methods."""
        if not self.__properties_loaded:
            self.load_water_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'WATER method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusWaterMethod]:
        """Returns mapping of water property methods as a dictionary where keys are the method number of type int."""
        if not self.__properties_loaded:
            self.load_water_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of 'NexusFile' objects where keys are of type int."""
        return self.__files

    def load_water_methods(self) -> None:
        """Loads water properties from files and initialises NexusWaterMethod object."""
        # Read in water properties from Nexus water method files
        if self.__files is not None and len(self.__files) > 0:  # Check if water files exist
            for table_num in self.__files.keys():  # For each water property method
                water_file = self.__files[table_num]
                if water_file.location is None:
                    raise ValueError(f'Unable to find water file: {water_file}')
                if os.path.isfile(water_file.location):
                    # Create NexusWaterMethod object
                    self.__inputs[table_num] = NexusWaterMethod(file=water_file, input_number=table_num,
                                                                model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with water properties in file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system

    @property
    def keyword(self) -> str:
        """Return the keyword for the water methods."""
        return 'WATER'

    def add_method(self, method: DynamicProperty, new_file_name: str, create_new_file: bool = False) -> None:
        """Adds a new Water method to the collection.

        Args:
            method (DynamicProperty): The water method to add.
            new_file_name (str): The name of the file to save the method to.
            create_new_file (bool): Whether to create a new file for the method.
        """
        add_dynamic_method(dynamic_method_collection=self, method=method, new_file_name=new_file_name,
                           create_new_file=create_new_file)

    def _method_type(self) -> type[NexusWaterMethod]:
        """Returns the expected type of the dynamic property."""
        return NexusWaterMethod
