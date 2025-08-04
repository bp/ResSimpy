"""Class for collecting all the Nexus Aquifer methods."""
from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import Optional, MutableMapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.DataModelBaseClasses.Aquifer import Aquifer
from ResSimpy.Utils.dynamic_method_manipulations import add_dynamic_method


@dataclass(kw_only=True)
class NexusAquiferMethods(Aquifer):
    """Class for collection of Nexus aquifer methods.

    Attributes:
        inputs (dict[int, NexusAquiferMethod]): Collection of Nexus aquifer methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of aquifer files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusAquiferMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem
    _model_files: Optional[FcsNexusFile] = field(default=None, repr=False, compare=False)

    def __init__(self, model_unit_system: UnitSystem, inputs: Optional[MutableMapping[int, NexusAquiferMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None, assume_loaded: bool = False,
                 model_files: Optional[FcsNexusFile] = None) -> None:
        """Initialises the NexusAquiferMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusAquiferMethod]]): Collection of Nexus aquifer methods.
            files (Optional[dict[int, NexusFile]]): Collection of aquifer files, as defined in Nexus fcs file.
            Keyed by the method number.
            assume_loaded (bool): If True, assumes that the properties are already loaded.
            model_files (Optional[FcsNexusFile]): The Nexus fcs file that contains the whole set of model files.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusAquiferMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        self.__properties_loaded = assume_loaded
        self._model_files = model_files
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing aquifer methods."""
        if not self.__properties_loaded:
            self.load_aquifer_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'AQUIFER method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusAquiferMethod]:
        """Returns mapping of aquifer where keys are of type int.
        If properties are not loaded, it will load them.
        """
        if not self.__properties_loaded:
            self.load_aquifer_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of Nexus files where keys are of type int."""
        return self.__files

    def load_aquifer_methods(self) -> None:
        """Loads a collection of aquifer method files.
        This method checks if aquifer files are available and read their properties into
        the 'NexusAquifer' object.
        """
        # Read in aquifer properties from Nexus aquifer method files
        if self.__files is not None and len(self.__files) > 0:  # Check if aquifer files exist
            for table_num in self.__files.keys():  # For each aquifer property method
                aquifer_file = self.__files[table_num]
                if aquifer_file.location is None:
                    raise ValueError(f'Unable to find aquifer file: {aquifer_file.location}')
                if os.path.isfile(aquifer_file.location):
                    # Create NexusAquifer object
                    self.__inputs[table_num] = NexusAquiferMethod(file=aquifer_file, input_number=table_num,
                                                                  model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with aquifer properties from file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system

    @property
    def keyword(self) -> str:
        """Return the keyword for the aquifer methods."""
        return 'AQUIFER'

    def add_method(self, method: DynamicProperty, new_file_name: str, create_new_file: bool = False) -> None:
        """Adds a new aquifer method to the collection.

        Args:
            method (DynamicProperty): The aquifer method to add.
            new_file_name (str): The name of the file to save the method to.
            create_new_file (bool): Whether to create a new file for the method.
        """
        add_dynamic_method(dynamic_method_collection=self, method=method, new_file_name=new_file_name,
                           create_new_file=create_new_file)

    def _method_type(self) -> type[NexusAquiferMethod]:
        """Returns the expected type of the dynamic property."""
        return NexusAquiferMethod
