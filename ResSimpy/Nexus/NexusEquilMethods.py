"""Class for collection of Nexus equilibration methods."""
from __future__ import annotations
from dataclasses import dataclass, field
import os
from typing import Optional, MutableMapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusEquilMethod import NexusEquilMethod
from ResSimpy.DataModelBaseClasses.Equilibration import Equilibration
from ResSimpy.Utils.dynamic_method_manipulations import add_dynamic_method


@dataclass(kw_only=True)
class NexusEquilMethods(Equilibration):
    """Class for collection of Nexus equilibration methods.

    Attributes:
        inputs (dict[int, NexusEquilMethod]): Collection of Nexus equilibration methods, as a dictionary
        files (dict[int, NexusFile]): Dictionary collection of equilibration files, as defined in Nexus fcs file.
    """

    __inputs: MutableMapping[int, NexusEquilMethod]
    __files: dict[int, NexusFile]
    __properties_loaded: bool = False  # Used in lazy loading
    __model_unit_system: UnitSystem
    _model_files: Optional[FcsNexusFile] = field(default=None, repr=False, compare=False)

    def __init__(self, model_unit_system: UnitSystem, inputs: Optional[MutableMapping[int, NexusEquilMethod]] = None,
                 files: Optional[dict[int, NexusFile]] = None, assume_loaded: bool = False,
                 model_files: Optional[FcsNexusFile] = None) -> None:
        """Initialises the NexusEquilMethods class.

        Args:
            model_unit_system (UnitSystem): Unit system used in the model.
            inputs (Optional[MutableMapping[int, NexusEquilMethod]]): Collection of Nexus equilibration methods.
            files (Optional[dict[int, NexusFile]]): Collection of equilibration files, as defined in Nexus fcs file.
                Keyed by the method number.
            assume_loaded (bool): If True, assumes that the equilibration methods are already loaded.
            model_files (Optional[FcsNexusFile]): The FCS file that contains the model files.
        """
        if inputs:
            self.__inputs = inputs
        else:
            self.__inputs: MutableMapping[int, NexusEquilMethod] = {}
        if files:
            self.__files = files
        else:
            self.__files = {}
        self.__model_unit_system = model_unit_system
        self.__properties_loaded = assume_loaded
        self._model_files = model_files
        super().__init__()

    def __repr__(self) -> str:
        """Pretty printing equil methods."""
        if not self.__properties_loaded:
            self.load_equil_methods()
        printable_str = ''
        for table_num in self.__inputs.keys():
            printable_str += '\n--------------------------------\n'
            printable_str += f'EQUIL method {table_num}\n'
            printable_str += '--------------------------------\n'
            printable_str += self.__inputs[table_num].__repr__()
            printable_str += '\n'

        return printable_str

    @property
    def inputs(self) -> MutableMapping[int, NexusEquilMethod]:
        """Returns mapping of 'NexusEquilMethod' where keys are of type int.
        If properties are not loaded, it will load them.
        """
        if not self.__properties_loaded:
            self.load_equil_methods()
        return self.__inputs

    @property
    def files(self) -> dict[int, NexusFile]:
        """Returns dictionary of Nexus files where keys are of type int."""
        return self.__files

    def load_equil_methods(self) -> None:
        """Loads a collection of equilibration method files.
        This method checks if equil files are available and reads their properties into
        'NexusEquilmethod' objects.
        """
        # Read in equil properties from Nexus equil method files
        if self.__files is not None and len(self.__files) > 0:  # Check if equil files exist
            for table_num in self.__files.keys():  # For each equil property method
                equil_file = self.__files[table_num]
                if equil_file.location is None:
                    raise ValueError(f'Unable to find equil file: {equil_file}')
                if os.path.isfile(equil_file.location):
                    # Create NexusEquilMethod object
                    self.__inputs[table_num] = NexusEquilMethod(file=equil_file, input_number=table_num,
                                                                model_unit_system=self.__model_unit_system)
                    self.__inputs[table_num].read_properties()  # Populate object with equil properties in file
        self.__properties_loaded = True

    @property
    def model_unit_system(self) -> UnitSystem:
        """Return the model unit system."""
        return self.__model_unit_system

    @property
    def summary(self) -> str:
        """Returns a string summary of 'NexusEquilMethods' inputs in a dictionary."""
        equil_summary = ''
        for key, value in self.inputs.items():
            equil_summary += f'        {key}: {value.file.location}\n'

        return equil_summary

    @property
    def keyword(self) -> str:
        """Returns the keyword for the equilibration methods."""
        return 'EQUIL'

    def add_method(self, method: DynamicProperty, new_file_name: str, create_new_file: bool = False) -> None:
        """Adds a new equil method to the collection.

        Args:
            method (DynamicProperty): The equil method to add.
            new_file_name (str): The name of the file to save the method to.
            create_new_file (bool): Whether to create a new file for the method.
        """
        add_dynamic_method(dynamic_method_collection=self, method=method, new_file_name=new_file_name,
                           create_new_file=create_new_file)

    def _method_type(self) -> type[NexusEquilMethod]:
        """Returns the expected type of the dynamic property."""
        return NexusEquilMethod
