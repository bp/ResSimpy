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
    __model_files: Optional[FcsNexusFile] = field(default=None, repr=False, compare=False)

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
        self.__model_files = model_files
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
        if new_file_name is None or new_file_name.strip() == '':
            raise ValueError('New file name must be provided and cannot be empty when adding a new method.')
        if not isinstance(method, NexusHydraulicsMethod):
            raise TypeError(f'Expected NexusHydraulicsMethod, got {type(method)}')
        if method.input_number in self.__inputs:
            raise ValueError(f'Method with input number {method.input_number} already exists in the collection.')

        if self.__model_unit_system != method.unit_system:
            raise ValueError(f'Model unit system {self.__model_unit_system} does not match method unit system '
                             f'{method.unit_system}.')

        self.__properties_loaded = True  # We are adding a new method so no more loading can happen.

        new_nexus_file = NexusFile(location=new_file_name,
                                   origin=None,  # Should get connected to the parent fcs file later
                                   include_objects=None,
                                   file_content_as_list=method.to_string().splitlines(keepends=True)
                                   )
        new_nexus_file._file_modified_set(True)  # Mark the file as modified
        method.file = new_nexus_file

        if create_new_file:
            method.write_to_file(new_file_path=new_file_name, overwrite_file=False)

        self.__inputs[method.input_number] = method
        self.__files[method.input_number] = method.file
        if self.__model_files is not None:
            self.__model_files._add_file(new_nexus_file, keyword='HYD', method_number=method.input_number)
