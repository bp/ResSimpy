"""Class for collection of Nexus relative permeability and capillary pressure property inputs."""
from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import Optional, MutableMapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod
from ResSimpy.DataModelBaseClasses.RelPerm import RelPerm
from ResSimpy.Utils.dynamic_method_manipulations import add_dynamic_method


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
    __model_unit_system: UnitSystem
    _model_files: Optional[FcsNexusFile] = field(default=None, repr=False, compare=False)

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusRelPermMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None, assume_loaded: bool = False,
                 model_files: Optional[FcsNexusFile] = None) -> None:
        """Initialises the NexusRelPermMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusRelPermMethod]]): Collection of Nexus relperm property inputs.
            files (Optional[dict[int, NexusFile]]): Collection of relperm property files, as defined in Nexus fcs file.
                Keyed by the method number.
            assume_loaded (bool): If True, assumes that the properties are already loaded.
            model_files (Optional[FcsNexusFile]): The FcsNexusFile that contains the whole set of model files.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusRelPermMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        self.__properties_loaded = assume_loaded
        self._model_files = model_files
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
        """Returns collection of Nexus relperm property inputs as dictionary.

        Returns:
            NexusRelPermMethod(MutableMapping): Keyed by method number with values being the NexusRelPermMethod.
        """
        if not self.__properties_loaded:
            self.load_relperm_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of Nexus Files."""
        return self.__files

    def load_relperm_methods(self) -> None:
        """Loads a collection of relperm Nexus files."""
        # Read in relperm properties from Nexus relperm method files
        if self.__files is not None and len(self.__files) > 0:  # Check if relperm files exist
            for table_num in self.__files.keys():  # For each relperm property method
                relperm_file = self.__files[table_num]
                if relperm_file.location is None:
                    raise ValueError(f'Unable to find relperm file: {relperm_file}')
                if os.path.isfile(relperm_file.location):
                    # Create NexusRelPermMethod object
                    self.__inputs[table_num] = NexusRelPermMethod(file=relperm_file, input_number=table_num,
                                                                  model_unit_system=self.__model_unit_system)
                    # Populate object with relperm properties in file
                    self.__inputs[table_num].read_properties()
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system

    @property
    def summary(self) -> str:
        """Returns a string summary of 'NexusRelPermMethods' inputs in a dictionary."""
        relperm_summary = ''
        for key, value in self.inputs.items():
            relperm_summary += f'        {key}: {value.file.location}\n'

        return relperm_summary

    @property
    def keyword(self) -> str:
        """Returns the keyword for the relperm methods."""
        return 'RELPM'

    def add_method(self, method: DynamicProperty, new_file_name: str, create_new_file: bool = False) -> None:
        """Adds a new relpm method to the collection.

        Args:
            method (DynamicProperty): The relpm method to add.
            new_file_name (str): The name of the file to save the method to.
            create_new_file (bool): Whether to create a new file for the method.
        """
        add_dynamic_method(dynamic_method_collection=self, method=method, new_file_name=new_file_name,
                           create_new_file=create_new_file)

    def _method_type(self) -> type[NexusRelPermMethod]:
        """Returns the expected type of the dynamic property."""
        return NexusRelPermMethod
