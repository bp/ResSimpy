from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Optional, Type, TYPE_CHECKING

from ResSimpy.Grid import Grid, VariableEntry
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.structured_grid_operations import StructuredGridOperations
import ResSimpy.Nexus.nexus_file_operations as nfo

import pandas as pd
from resqpy.olio.read_nexus_fault import load_nexus_fault_mult_table_from_list

if TYPE_CHECKING:
    from ResSimpy.Nexus.NexusSimulator import NexusSimulator


@dataclass
class PropertyToLoad:
    token: str
    modifiers: list[str]
    property: VariableEntry


@dataclass(kw_only=True)
class StructuredGridFile(Grid):

    __faults_df: Optional[pd.DataFrame] = None
    __grid_faults_loaded: bool = False
    __grid_file_contents: Optional[list[str]] = None

    def __init__(self, data: Optional[dict] = None, grid_file_contents: Optional[list[str]] = None):
        super().__init__()

        self.__faults_df: Optional[pd.DataFrame] = None
        self.__grid_faults_loaded: bool = False
        self.__grid_file_contents = grid_file_contents

        # Use the dict provided to populate the properties
        if data is not None:
            for name, value in data.items():
                setattr(self, name, self.__wrap(value))

    def __wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self.__wrap(v) for v in value])
        else:
            return StructuredGridFile(value) if isinstance(value, dict) else value

    @classmethod
    def load_structured_grid_file(cls: Type[StructuredGridFile], structure_grid_file: NexusFile) -> StructuredGridFile:
        """Loads in a structured grid file including all grid properties and modifiers.
        Currently loading in grids with FUNCTIONS included are not supported.
        Args:
            structure_grid_file (NexusFile): the NexusFile representation of a structured grid file for converting \
                into a structured grid file class
        Raises:
            AttributeError: if no value is found for the structured grid file path
            ValueError: if when loading the grid no values can be found for the NX NY NZ line.
        """
        if structure_grid_file.location is None:
            raise ValueError(f"No file path given or found for structured grid file path. \
                Instead got {structure_grid_file.location}")
        file_as_list = structure_grid_file.get_flat_list_str_file()
        # Clean up file_as_list
        file_as_list = [s.strip() for s in file_as_list]
        file_as_list = list(filter(None, file_as_list))

        if file_as_list is None:
            raise ValueError("No file path given or found for structured grid file path. \
                Please update structured grid file path")
        loaded_structured_grid_file = cls(grid_file_contents=file_as_list)

        def move_next_value(next_line: str) -> tuple[str, str]:
            """finds the next value and then strips out the value from the line.

            Args:
                next_line (str): the line to search through for the value

            Raises:
                ValueError: if no value is found within the line provided

            Returns:
                tuple[str, str]: the next value found in the line, the line with the value stripped out.
            """
            value = nfo.get_next_value(0, [next_line], next_line)
            if value is None:
                raise ValueError(f"No value found within the provided line: {next_line}")
            next_line = next_line.replace(value, "", 1)
            return value, next_line

        for line in file_as_list:
            # Load in the basic properties
            properties_to_load = [
                PropertyToLoad('NETGRS', ['VALUE', 'CON'], loaded_structured_grid_file.netgrs),
                PropertyToLoad('POROSITY', ['VALUE', 'CON'], loaded_structured_grid_file.porosity),
                PropertyToLoad('SW', ['VALUE', 'CON'], loaded_structured_grid_file.sw),
                PropertyToLoad('KX', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kx),
                PropertyToLoad('PERMX', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kx),
                PropertyToLoad('PERMI', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kx),
                PropertyToLoad('KI', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kx),
                PropertyToLoad('KY', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.ky),
                PropertyToLoad('PERMY', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.ky),
                PropertyToLoad('PERMJ', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.ky),
                PropertyToLoad('KJ', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.ky),
                PropertyToLoad('KZ', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kz),
                PropertyToLoad('PERMZ', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kz),
                PropertyToLoad('PERMK', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kz),
                PropertyToLoad('KK', ['VALUE', 'MULT', 'CON'], loaded_structured_grid_file.kz),
            ]

            for token_property in properties_to_load:
                for modifier in token_property.modifiers:
                    StructuredGridOperations.load_token_value_if_present(token_property.token, modifier,
                                                                         token_property.property, line,
                                                                         file_as_list, ['INCLUDE'])

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

                loaded_structured_grid_file.range_x = int(first_value)
                loaded_structured_grid_file.range_y = int(second_value)
                loaded_structured_grid_file.range_z = int(third_value)

        return loaded_structured_grid_file

    @staticmethod
    def update_structured_grid_file(grid_dict: dict[str, VariableEntry | int], model: NexusSimulator) -> None:
        """Save values passed from the front end to the structured grid file and update the class

        Args:
            grid_dict (dict[str, Union[VariableEntry, int]]): dictionary containing grid properties to be replaced
            model (NexusSimulator): an instance of a NexusSimulator object
        Raises:
            ValueError: If no structured grid file is in the instance of the Simulator class
        """
        # Convert the dictionary back to a class, and update the properties on our class
        structured_grid = model.get_structured_grid()
        if structured_grid is None or model.fcs_file.structured_grid_file is None:
            raise ValueError("Model does not contain a structured grid")
        original_structured_grid_file = copy.deepcopy(structured_grid)

        # replace the structured grid with a new object with an updated dictionary
        structured_grid = StructuredGridFile(grid_dict)
        model.set_structured_grid(structured_grid)

        # change it in the text file for nexus:
        grid_file_path = model.fcs_file.structured_grid_file.location
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

    def load_faults(self):
        """Function to read faults in Nexus grid file defined using MULT and FNAME keywords

        Args:
            file_content_as_list (list[str]): list of strings that comprise input from Nexus structured grid file

        """
        if self.__grid_file_contents is None:
            raise ValueError('Grid file contents have not been loaded')
        file_content_as_list = self.__grid_file_contents
        df = load_nexus_fault_mult_table_from_list(file_content_as_list)

        if not df.empty:
            # Ensure resulting dataframe has uppercase column names
            df.columns = [col.upper() for col in df.columns]

            # Check if any multfl's have been used in grid file and update fault trans multipliers accordingly
            f_names = df['NAME'].unique()
            f_mults = [1.]*len(f_names)
            mult_dict = dict(zip(f_names, f_mults))
            for line in file_content_as_list:
                if nfo.check_token('MULTFL', line):
                    if nfo.get_token_value('MULTFL', line, file_content_as_list) is None:
                        raise ValueError(f'{line} does not have a fault name following MULTFL.')
                    fname = str(nfo.get_token_value('MULTFL', line, file_content_as_list))
                    if fname in df['NAME'].unique():
                        if nfo.get_token_value(fname, line, file_content_as_list) is None:
                            raise ValueError(f'MULTFL {fname} does not have a numerical tmult value.')
                        tmult = float(str(nfo.get_token_value(fname, line, file_content_as_list)))
                        mult_dict[fname] *= tmult
            mult_df = pd.DataFrame.from_dict(mult_dict, orient='index').reset_index()
            mult_df.columns = ['NAME', 'TMULT']
            new_df = df.merge(mult_df, how='left', on='NAME', validate='many_to_one')
            new_df['MULT'] = new_df['MULT']*new_df['TMULT']
            self.__faults_df = new_df.drop(['TMULT'], axis=1)
        self.__grid_faults_loaded = True

    def get_faults_df(self) -> Optional[pd.DataFrame]:
        """Returns the fault definition and transmissility multiplier information as a dataframe"""

        if not self.__grid_faults_loaded:
            self.load_faults()
        return self.__faults_df
