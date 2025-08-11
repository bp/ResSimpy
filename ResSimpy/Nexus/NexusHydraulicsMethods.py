from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import Optional, MutableMapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.GenericContainerClasses.Hydraulics import Hydraulics
from ResSimpy.Utils.dynamic_method_manipulations import add_dynamic_method


@dataclass(kw_only=True)
class NexusHydraulicsMethods(Hydraulics):
    """Class for collection of Nexus hydraulics methods.

    Attributes:
        inputs (dict[int, NexusHydraulicsMethod]): Collection of Nexus hydraulics methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of hydraulics files, in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusHydraulicsMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem
    _model_files: Optional[FcsNexusFile] = field(default=None, repr=False, compare=False)

    def __init__(self, model_unit_system: UnitSystem,
                 inputs: Optional[MutableMapping[int, NexusHydraulicsMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None, assume_loaded: bool = False,
                 model_files: Optional[FcsNexusFile] = None) -> None:
        """Initialises the NexusHydraulicsMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusHydraulicsMethod]]): Collection of Nexus hydraulics methods.
            files (Optional[dict[int, NexusFile]]): Collection of hydraulics files, as defined in Nexus fcs file.
                Keyed by the method number.
            assume_loaded (bool): If True, assumes that the hydraulics methods are already loaded.
            model_files (Optional[FcsFile]): The FcsFile object that contains the model files.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusHydraulicsMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        self.__properties_loaded = assume_loaded
        self._model_files = model_files
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing hydraulics methods."""
        if not self.__properties_loaded:
            self.load_hydraulics_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'HYD method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusHydraulicsMethod]:
        """Returns mapping of hydraulics method where keys are of type int.
        If properties are not loaded, it will load them first.
        """
        if not self.__properties_loaded:
            self.load_hydraulics_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns a dictionary of Nexus files where keys are of type int."""
        return self.__files

    def load_hydraulics_methods(self) -> None:
        """Loads a collection of hydraulic method files defined by the Nexus fcs files."""
        # Read in hydraulics properties from Nexus hydraulics method files
        if self.__files is not None and len(self.__files) > 0:  # Check if hydraulics files exist
            for table_num in self.__files.keys():  # For each hydraulics property method
                hydraulics_file = self.__files[table_num]
                if hydraulics_file.location is None:
                    raise ValueError(f'Unable to find hydraulics file: {hydraulics_file}')
                if os.path.isfile(hydraulics_file.location):
                    # Create NexusHydraulicsMethod object
                    self.__inputs[table_num] = NexusHydraulicsMethod(file=hydraulics_file, input_number=table_num,
                                                                     model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with hydraulics props
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system

    @property
    def summary(self) -> str:
        """Returns a string summary of 'NexusHydraulicsMethods' inputs in a dictionary."""
        hydraulics_summary = ''
        for key, value in self.inputs.items():
            file_loc = value.file.location if value.file else 'No file associated'
            hydraulics_summary += f'        {key}: {file_loc}\n'

        return hydraulics_summary

    def add_method(self, method: DynamicProperty, new_file_name: str, create_new_file: bool = False) -> None:
        """Adds a new hydraulics method to the collection.

        Args:
            method (DynamicProperty): The hydraulics method to add.
            new_file_name (str): The name of the file to save the method to.
            create_new_file (bool): Whether to create a new file for the method.
        """
        add_dynamic_method(dynamic_method_collection=self, method=method, new_file_name=new_file_name,
                           create_new_file=create_new_file)

    @property
    def keyword(self) -> str:
        """Returns the keyword for the hydraulics methods."""
        return 'HYD'

    def _method_type(self) -> type[NexusHydraulicsMethod]:
        """Returns the expected type of the dynamic property."""
        return NexusHydraulicsMethod
