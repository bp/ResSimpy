"""Nexus grid file class for loading in a structured grid file and extracting the grid properties."""
from __future__ import annotations

import copy
import pandas as pd
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from ResSimpy.Grid import Grid, VariableEntry
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction
from ResSimpy.Nexus.structured_grid_operations import StructuredGridOperations
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.Nexus.array_function_operations as afo

from resqpy.olio.read_nexus_fault import load_nexus_fault_mult_table_from_list

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass
class PropertyToLoad:
    token: str
    modifiers: list[str]
    property: VariableEntry


@dataclass(kw_only=True)
class NexusGrid(Grid):
    __array_functions_list: Optional[list[list[str]]] = None
    __array_functions_df: Optional[pd.DataFrame] = None
    __array_functions_loaded: bool = False
    __grid_file_contents: Optional[list[str]] = None
    __grid_file_nested: Optional[list[str]] = None
    __faults_df: Optional[pd.DataFrame] = None
    __grid_faults_loaded: bool = False
    __grid_properties_loaded: bool = False
    __grid_nexus_file: Optional[NexusFile] = None

    def __init__(self, grid_nexus_file: Optional[NexusFile] = None) -> None:
        """Initialises the NexusGrid class.

        Args:
            grid_nexus_file (Optional[NexusFile]): the NexusFile representation of a structured grid file for \
                reading and interpreting the grid properties from.
        """
        super().__init__()
        self.__array_functions_list: Optional[list[list[str]]] = None
        self.__array_functions_df: Optional[pd.DataFrame] = None
        self.__array_functions_loaded: bool = False
        self.__grid_file_contents: Optional[list[str]] = None if grid_nexus_file is None else \
            grid_nexus_file.get_flat_list_str_file_including_includes
        self.__grid_file_nested: Optional[list[str]] = None if grid_nexus_file is None else \
            grid_nexus_file.file_content_as_list
        self.__faults_df: Optional[pd.DataFrame] = None
        self.__grid_faults_loaded: bool = False
        self.__grid_properties_loaded: bool = False
        self.__grid_nexus_file: Optional[NexusFile] = grid_nexus_file
        self.__grid_array_functions: Optional[list[NexusGridArrayFunction]] = None

    def __wrap(self, value):
        if isinstance(value, tuple | list | set | frozenset):
            return type(value)([self.__wrap(v) for v in value])
        else:
            return value

    def update_properties_from_dict(self, data: dict[str, int | VariableEntry]) -> None:
        """Allows you to update properties on the class using the provided dict of values.

        Args:
        ----
                data dict[str, int | VariableEntry]: the dictionary of values to update on the class
        """
        # Use the dict provided to populate the properties in the class
        if data is not None:
            for name, value in data.items():
                private_name = '_' + name
                setattr(self, private_name, self.__wrap(value))

        # Prevent reload from disk
        self.__grid_properties_loaded = True

    def to_dict(self) -> dict[str, Optional[int] | VariableEntry]:
        self.load_grid_properties_if_not_loaded()

        original_dict = self.__dict__
        new_dict: dict[str, Optional[int] | VariableEntry] = {}
        for key in original_dict.keys():
            new_key = key
            if new_key[0] == '_':
                new_key = new_key.replace('_', '', 1)
            if new_key[0] == '_':
                new_key = new_key.replace('_', '', 1)
            new_dict[new_key] = original_dict[key]

        return new_dict

    def load_grid_properties_if_not_loaded(self) -> None:
        def move_next_value(next_line: str) -> tuple[str, str]:
            """Finds the next value and then strips out the value from the line.

            Args:
            ----
                next_line (str): the line to search through for the value

            Raises:
            ------
                ValueError: if no value is found within the line provided

            Returns:
            -------
                tuple[str, str]: the next value found in the line, the line with the value stripped out.
            """
            value = nfo.get_next_value(0, [next_line], next_line)
            if value is None:
                raise ValueError(f"No value found within the provided line: {next_line}")
            next_line = next_line.replace(value, "", 1)
            return value, next_line

        # If we've already loaded the grid properties, don't do so again.
        if self.__grid_properties_loaded:
            return

        if self.__grid_nexus_file is None or self.__grid_file_contents is None or self.__grid_file_nested is None:
            raise ValueError("Grid file not found, cannot load grid properties")

        file_as_list = self.__grid_file_contents
        for line in file_as_list:

            # Load in the basic properties
            properties_to_load = [
                PropertyToLoad('NETGRS', ['VALUE', 'CON'], self._netgrs),
                PropertyToLoad('POROSITY', ['VALUE', 'CON'], self._porosity),
                PropertyToLoad('SW', ['VALUE', 'CON'], self._sw),
                PropertyToLoad('KX', ['VALUE', 'MULT', 'CON'], self._kx),
                PropertyToLoad('PERMX', ['VALUE', 'MULT', 'CON'], self._kx),
                PropertyToLoad('PERMI', ['VALUE', 'MULT', 'CON'], self._kx),
                PropertyToLoad('KI', ['VALUE', 'MULT', 'CON'], self._kx),
                PropertyToLoad('KY', ['VALUE', 'MULT', 'CON'], self._ky),
                PropertyToLoad('PERMY', ['VALUE', 'MULT', 'CON'], self._ky),
                PropertyToLoad('PERMJ', ['VALUE', 'MULT', 'CON'], self._ky),
                PropertyToLoad('KJ', ['VALUE', 'MULT', 'CON'], self._ky),
                PropertyToLoad('KZ', ['VALUE', 'MULT', 'CON'], self._kz),
                PropertyToLoad('PERMZ', ['VALUE', 'MULT', 'CON'], self._kz),
                PropertyToLoad('PERMK', ['VALUE', 'MULT', 'CON'], self._kz),
                PropertyToLoad('KK', ['VALUE', 'MULT', 'CON'], self._kz),
            ]

            for token_property in properties_to_load:
                for modifier in token_property.modifiers:
                    StructuredGridOperations.load_token_value_if_present(
                        token_property.token, modifier, token_property.property, line, file_as_list, ['INCLUDE'])

            # Load in grid dimensions
            if nfo.check_token('NX', line):
                # Check that the format of the grid is NX followed by NY followed by NZ
                current_line = file_as_list[file_as_list.index(line)]
                remaining_line = current_line[current_line.index('NX') + 2:]
                if nfo.get_next_value(0, [remaining_line], remaining_line) != 'NY':
                    continue
                remaining_line = remaining_line[remaining_line.index('NY') + 2:]
                if nfo.get_next_value(0, [remaining_line], remaining_line) != 'NZ':
                    continue

                # Avoid loading in a comment
                if "!" in line and line.index("!") < line.index('NX'):
                    continue
                next_line = file_as_list[file_as_list.index(line) + 1]
                first_value, next_line = move_next_value(next_line)
                second_value, next_line = move_next_value(next_line)
                third_value, next_line = move_next_value(next_line)

                self._range_x = int(first_value)
                self._range_y = int(second_value)
                self._range_z = int(third_value)

        self.__grid_properties_loaded = True

    @classmethod
    def load_structured_grid_file(cls: type[NexusGrid], structured_grid_file: NexusFile,
                                  lazy_loading: bool = True) -> NexusGrid:
        """Loads in a structured grid file with all grid properties, and the array functions defined with 'FUNCTION'.
        Other grid modifiers are currently not supported.

        Args:
        ----
            structured_grid_file (NexusFile): the NexusFile representation of a structured grid file for converting \
                into a structured grid file class
        Raises:
            AttributeError: if no value is found for the structured grid file path
            ValueError: if when loading the grid no values can be found for the NX NY NZ line.
        """
        if structured_grid_file.location is None:
            raise ValueError(f"No file path given or found for structured grid file path. \
                Instead got {structured_grid_file.location}")

        loaded_structured_grid_file = cls(grid_nexus_file=structured_grid_file)

        if not lazy_loading:
            loaded_structured_grid_file.load_grid_properties_if_not_loaded()
            loaded_structured_grid_file.load_faults()
            loaded_structured_grid_file.load_array_functions()

        return loaded_structured_grid_file

    @staticmethod
    def update_structured_grid_file(grid_dict: dict[str, VariableEntry | int], model: NexusSimulator) -> None:
        """Save values passed from the front end to the structured grid file and update the class.

        Args:
        ----
            grid_dict (dict[str, Union[VariableEntry, int]]): dictionary containing grid properties to be replaced
            model (NexusSimulator): an instance of a NexusSimulator object
        Raises:
            ValueError: If no structured grid file is in the instance of the Simulator class
        """
        # Convert the dictionary back to a class, and update the properties on our class
        structured_grid = model.grid
        if structured_grid is None or model.model_files.structured_grid_file is None:
            raise ValueError("Model does not contain a structured grid")
        original_structured_grid_file = copy.deepcopy(structured_grid)

        # replace the structured grid with a new object with an updated dictionary
        structured_grid.update_properties_from_dict(grid_dict)

        # change it in the text file for nexus:
        grid_file_path = model.model_files.structured_grid_file.location
        if grid_file_path is None:
            raise ValueError("No path found for structured grid file path.")
        structured_grid_contents = nfo.load_file_as_list(grid_file_path)
        # Get the existing file as a list
        if structured_grid_contents is None:
            raise ValueError("No path found for structured grid file path. \
                Please provide a path to the structured grid")
        # Update each value in the file
        StructuredGridOperations.replace_value(structured_grid_contents, original_structured_grid_file.netgrs,
                                               structured_grid.netgrs, 'NETGRS')
        StructuredGridOperations.replace_value(structured_grid_contents, original_structured_grid_file.porosity,
                                               structured_grid.porosity, 'POROSITY')
        StructuredGridOperations.replace_value(structured_grid_contents, original_structured_grid_file.sw,
                                               structured_grid.sw, 'SW')
        StructuredGridOperations.replace_value(structured_grid_contents, original_structured_grid_file.kx,
                                               structured_grid.kx, 'KX')
        StructuredGridOperations.replace_value(structured_grid_contents, original_structured_grid_file.ky,
                                               structured_grid.ky, 'KY')
        StructuredGridOperations.replace_value(structured_grid_contents, original_structured_grid_file.kz,
                                               structured_grid.kz, 'KZ')

        # Save the new file contents
        new_file_str = "".join(structured_grid_contents)
        with open(grid_file_path, "w") as text_file:
            text_file.write(new_file_str)

    def load_array_functions(self) -> None:
        if self.__grid_file_contents is None:
            raise ValueError("Cannot load array functions as grid file cannot not found")
        self.__array_functions_list = afo.collect_all_function_blocks(self.__grid_file_contents)
        self.__grid_array_functions = afo.create_grid_array_function_objects(self.__array_functions_list)
        self.__array_functions_df = afo.summarize_model_functions(self.__array_functions_list)
        self.__array_functions_loaded = True

    def get_array_functions_list(self) -> Optional[list[list[str]]]:
        """Returns the grid array functions as a list of function lines."""
        if not self.__array_functions_loaded:
            self.load_array_functions()
        return self.__array_functions_list

    def get_array_functions_df(self) -> Optional[pd.DataFrame]:
        """Returns the grid array functions as a dataframe."""
        if not self.__array_functions_loaded:
            self.load_array_functions()
        return self.__array_functions_df

    def load_faults(self) -> None:
        """Function to read faults in Nexus grid file defined using MULT and FNAME keywords."""
        file_content_as_list = self.__grid_file_contents
        if file_content_as_list is None:
            raise ValueError('Grid file contents have not been loaded')
        df = load_nexus_fault_mult_table_from_list(file_content_as_list)

        if not df.empty:
            # Ensure resulting dataframe has uppercase column names
            df.columns = [col.upper() for col in df.columns]

            # Check if any multfls have been used in grid file and update fault trans multipliers accordingly
            f_names = df['NAME'].unique()
            f_mults = [1.] * len(f_names)
            mult_dict = dict(zip(f_names, f_mults))
            for line in file_content_as_list:
                if nfo.check_token('MULTFL', line):
                    fname = str(nfo.get_expected_token_value(
                        'MULTFL', line, file_content_as_list,
                        custom_message=f'{line} does not have a fault name following MULTFL'))
                    if fname in df['NAME'].unique():
                        tmult = float(str(nfo.get_expected_token_value(
                            fname, line, file_content_as_list,
                            custom_message=f'MULTFL {fname} does not have a numerical tmult value')))
                        mult_dict[fname] *= tmult
            mult_df = pd.DataFrame.from_dict(mult_dict, orient='index').reset_index()
            mult_df.columns = ['NAME', 'TMULT']
            new_df = df.merge(mult_df, how='left', on='NAME', validate='many_to_one')
            new_df['MULT'] = new_df['MULT'] * new_df['TMULT']
            self.__faults_df = new_df.drop(['TMULT'], axis=1)
        self.__grid_faults_loaded = True

    def get_faults_df(self) -> Optional[pd.DataFrame]:
        """Returns the fault definition and transmissility multiplier information as a dataframe."""

        if not self.__grid_faults_loaded:
            self.load_faults()
        return self.__faults_df

    @property
    def array_functions(self) -> Optional[list[NexusGridArrayFunction]]:
        """Returns a list of the array functions defined in the structured grid file."""
        if self.__grid_array_functions is None:
            self.load_array_functions()
        return self.__grid_array_functions
