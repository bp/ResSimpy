"""Nexus grid file class for loading in a structured grid file and extracting the grid properties."""
from __future__ import annotations

import copy
import os

import pandas as pd
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, Any
import warnings

from ResSimpy.File import File
from ResSimpy.Grid import Grid, GridArrayDefinition
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_FORMAT_KEYWORDS
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
    property: GridArrayDefinition | dict[str, GridArrayDefinition]


@dataclass(kw_only=True)
class NexusGrid(Grid):
    __array_functions_list: Optional[list[list[str]]] = None
    __array_functions_df: Optional[pd.DataFrame] = None
    __array_functions_loaded: bool = False
    __grid_file_contents: Optional[list[str]] = None
    __grid_file_nested: Optional[list[str]] = None
    __faults_df: Optional[pd.DataFrame] = None
    __grid_faults_loaded: bool = False
    __grid_nexus_file: Optional[NexusFile] = None
    __corp: GridArrayDefinition
    __dx: GridArrayDefinition
    __dy: GridArrayDefinition
    __dz: GridArrayDefinition
    __depth: GridArrayDefinition
    __mdepth: GridArrayDefinition
    __dznet: GridArrayDefinition
    __compr: GridArrayDefinition
    __icoars: GridArrayDefinition
    __ialphaf: GridArrayDefinition
    __ipolymer: GridArrayDefinition
    __iadsorption: GridArrayDefinition
    __itracer: GridArrayDefinition
    __igrid: GridArrayDefinition
    __isector: GridArrayDefinition
    __swl: GridArrayDefinition
    __swr: GridArrayDefinition
    __swu: GridArrayDefinition
    __sgl: GridArrayDefinition
    __sgr: GridArrayDefinition
    __sgu: GridArrayDefinition
    __swro: GridArrayDefinition
    __swro_ls: GridArrayDefinition
    __sgro: GridArrayDefinition
    __sgrw: GridArrayDefinition
    __krw_swro: GridArrayDefinition
    __krws_ls: GridArrayDefinition
    __krw_swu: GridArrayDefinition
    __krg_sgro: GridArrayDefinition
    __krg_sgu: GridArrayDefinition
    __krg_sgrw: GridArrayDefinition
    __kro_swl: GridArrayDefinition
    __kro_swr: GridArrayDefinition
    __kro_sgl: GridArrayDefinition
    __kro_sgr: GridArrayDefinition
    __krw_sgl: GridArrayDefinition
    __krw_sgr: GridArrayDefinition
    __sgtr: GridArrayDefinition
    __sotr: GridArrayDefinition
    __swlpc: GridArrayDefinition
    __sglpc: GridArrayDefinition
    __pcw_swl: GridArrayDefinition
    __pcg_sgu: GridArrayDefinition
    __chloride: GridArrayDefinition
    __calcium: GridArrayDefinition
    __salinity: GridArrayDefinition
    __api: GridArrayDefinition
    __tmx: GridArrayDefinition
    __tmy: GridArrayDefinition
    __tmz: GridArrayDefinition
    __multbv: GridArrayDefinition
    __pv: GridArrayDefinition
    __iequil: GridArrayDefinition
    __ipvt: GridArrayDefinition
    __iwater: GridArrayDefinition
    __irelpm: GridArrayDefinition
    __irock: GridArrayDefinition
    __itran: GridArrayDefinition
    __iregion: dict[str, GridArrayDefinition]
    __pvmult: GridArrayDefinition
    __livecell: GridArrayDefinition
    __worka1: GridArrayDefinition
    __worka2: GridArrayDefinition
    __worka3: GridArrayDefinition
    __worka4: GridArrayDefinition
    __worka5: GridArrayDefinition
    __worka6: GridArrayDefinition
    __worka7: GridArrayDefinition
    __worka8: GridArrayDefinition
    __worka9: GridArrayDefinition

    def __init__(self, grid_nexus_file: Optional[NexusFile] = None, assume_loaded: bool = False) -> None:
        """Initialises the NexusGrid class.

        Args:
            grid_nexus_file (Optional[NexusFile]): the NexusFile representation of a structured grid file for \
                reading and interpreting the grid properties from.
            assume_loaded (bool): Create the object assuming the grid has already been loaded into memory.
        """
        super().__init__(assume_loaded=assume_loaded)
        self.__array_functions_list: Optional[list[list[str]]] = None
        self.__array_functions_df: Optional[pd.DataFrame] = None
        self.__array_functions_loaded: bool = False
        self.__grid_file_contents: Optional[list[str]] = None if grid_nexus_file is None else \
            grid_nexus_file.get_flat_list_str_file_including_includes
        self.__grid_file_nested: Optional[list[str]] = None if grid_nexus_file is None else \
            grid_nexus_file.file_content_as_list
        self.__faults_df: Optional[pd.DataFrame] = None
        self.__grid_nexus_file: Optional[NexusFile] = grid_nexus_file
        self.__grid_array_functions: Optional[list[NexusGridArrayFunction]] = None
        self.__corp: GridArrayDefinition = GridArrayDefinition()
        self.__iequil: GridArrayDefinition = GridArrayDefinition()
        self.__ipvt: GridArrayDefinition = GridArrayDefinition()
        self.__iwater: GridArrayDefinition = GridArrayDefinition()
        self.__irelpm: GridArrayDefinition = GridArrayDefinition()
        self.__irock: GridArrayDefinition = GridArrayDefinition()
        self.__itran: GridArrayDefinition = GridArrayDefinition()
        self.__iregion: dict[str, GridArrayDefinition] = {}
        self.__pvmult: GridArrayDefinition = GridArrayDefinition()
        self.__livecell: GridArrayDefinition = GridArrayDefinition()
        self.__worka1: GridArrayDefinition = GridArrayDefinition()
        self.__worka2: GridArrayDefinition = GridArrayDefinition()
        self.__worka3: GridArrayDefinition = GridArrayDefinition()
        self.__worka4: GridArrayDefinition = GridArrayDefinition()
        self.__worka5: GridArrayDefinition = GridArrayDefinition()
        self.__worka6: GridArrayDefinition = GridArrayDefinition()
        self.__worka7: GridArrayDefinition = GridArrayDefinition()
        self.__worka8: GridArrayDefinition = GridArrayDefinition()
        self.__worka9: GridArrayDefinition = GridArrayDefinition()
        self.__dx: GridArrayDefinition = GridArrayDefinition()
        self.__dy: GridArrayDefinition = GridArrayDefinition()
        self.__dz: GridArrayDefinition = GridArrayDefinition()
        self.__depth: GridArrayDefinition = GridArrayDefinition()
        self.__mdepth: GridArrayDefinition = GridArrayDefinition()
        self.__dznet: GridArrayDefinition = GridArrayDefinition()
        self.__compr: GridArrayDefinition = GridArrayDefinition()
        self.__icoars: GridArrayDefinition = GridArrayDefinition()
        self.__ialphaf: GridArrayDefinition = GridArrayDefinition()
        self.__ipolymer: GridArrayDefinition = GridArrayDefinition()
        self.__iadsorption: GridArrayDefinition = GridArrayDefinition()
        self.__itracer: GridArrayDefinition = GridArrayDefinition()
        self.__igrid: GridArrayDefinition = GridArrayDefinition()
        self.__isector: GridArrayDefinition = GridArrayDefinition()
        self.__swl: GridArrayDefinition = GridArrayDefinition()
        self.__swr: GridArrayDefinition = GridArrayDefinition()
        self.__swu: GridArrayDefinition = GridArrayDefinition()
        self.__sgl: GridArrayDefinition = GridArrayDefinition()
        self.__sgr: GridArrayDefinition = GridArrayDefinition()
        self.__sgu: GridArrayDefinition = GridArrayDefinition()
        self.__swro: GridArrayDefinition = GridArrayDefinition()
        self.__swro_ls: GridArrayDefinition = GridArrayDefinition()
        self.__sgro: GridArrayDefinition = GridArrayDefinition()
        self.__sgrw: GridArrayDefinition = GridArrayDefinition()
        self.__krw_swro: GridArrayDefinition = GridArrayDefinition()
        self.__krws_ls: GridArrayDefinition = GridArrayDefinition()
        self.__krw_swu: GridArrayDefinition = GridArrayDefinition()
        self.__krg_sgro: GridArrayDefinition = GridArrayDefinition()
        self.__krg_sgu: GridArrayDefinition = GridArrayDefinition()
        self.__krg_sgrw: GridArrayDefinition = GridArrayDefinition()
        self.__kro_swl: GridArrayDefinition = GridArrayDefinition()
        self.__kro_swr: GridArrayDefinition = GridArrayDefinition()
        self.__kro_sgl: GridArrayDefinition = GridArrayDefinition()
        self.__kro_sgr: GridArrayDefinition = GridArrayDefinition()
        self.__krw_sgl: GridArrayDefinition = GridArrayDefinition()
        self.__krw_sgr: GridArrayDefinition = GridArrayDefinition()
        self.__sgtr: GridArrayDefinition = GridArrayDefinition()
        self.__sotr: GridArrayDefinition = GridArrayDefinition()
        self.__swlpc: GridArrayDefinition = GridArrayDefinition()
        self.__sglpc: GridArrayDefinition = GridArrayDefinition()
        self.__pcw_swl: GridArrayDefinition = GridArrayDefinition()
        self.__pcg_sgu: GridArrayDefinition = GridArrayDefinition()
        self.__chloride: GridArrayDefinition = GridArrayDefinition()
        self.__calcium: GridArrayDefinition = GridArrayDefinition()
        self.__salinity: GridArrayDefinition = GridArrayDefinition()
        self.__api: GridArrayDefinition = GridArrayDefinition()
        self.__tmx: GridArrayDefinition = GridArrayDefinition()
        self.__tmy: GridArrayDefinition = GridArrayDefinition()
        self.__tmz: GridArrayDefinition = GridArrayDefinition()
        self.__multbv: GridArrayDefinition = GridArrayDefinition()
        self.__pv: GridArrayDefinition = GridArrayDefinition()

    def __wrap(self, value: Any) -> Any:
        if isinstance(value, tuple | list | set | frozenset):
            return type(value)([self.__wrap(v) for v in value])
        else:
            return value

    def update_properties_from_dict(self, data: dict[str, int | GridArrayDefinition]) -> None:
        """Allows you to update properties on the class using the provided dict of values.

        Args:
        ----
                data (dict[str, int | GridArrayDefinition]): the dictionary of values to update on the class
        """
        # Use the dict provided to populate the properties in the class
        if data is not None:
            for name, value in data.items():
                private_name = '_' + name
                setattr(self, private_name, self.__wrap(value))

        # Prevent reload from disk
        self._grid_properties_loaded = True

    def to_dict(self) -> dict[str, Optional[int] | GridArrayDefinition]:
        self.load_grid_properties_if_not_loaded()

        original_dict = self.__dict__
        new_dict: dict[str, Optional[int] | GridArrayDefinition] = {}
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
        if self._grid_properties_loaded:
            return

        if self.__grid_nexus_file is None or self.__grid_file_contents is None or self.__grid_file_nested is None:
            raise ValueError("Grid file not found, cannot load grid properties")

        # Strip file of comments
        file_as_list = nfo.strip_file_of_comments(self.__grid_file_contents, comment_characters=['!', 'C'])
        # Ignore blank lines
        file_as_list = [line for line in file_as_list if not line.strip() == '']

        properties_to_load = [
            PropertyToLoad('NETGRS', GRID_ARRAY_FORMAT_KEYWORDS, self._netgrs),
            PropertyToLoad('POROSITY', GRID_ARRAY_FORMAT_KEYWORDS, self._porosity),
            PropertyToLoad('POR', GRID_ARRAY_FORMAT_KEYWORDS, self._porosity),
            PropertyToLoad('SW', GRID_ARRAY_FORMAT_KEYWORDS, self._sw),
            PropertyToLoad('SG', GRID_ARRAY_FORMAT_KEYWORDS, self._sg),
            PropertyToLoad('PRESSURE', GRID_ARRAY_FORMAT_KEYWORDS, self._pressure),
            PropertyToLoad('P', GRID_ARRAY_FORMAT_KEYWORDS, self._pressure),
            PropertyToLoad('TEMPERATURE', GRID_ARRAY_FORMAT_KEYWORDS, self._temperature),
            PropertyToLoad('TEMP', GRID_ARRAY_FORMAT_KEYWORDS, self._temperature),
            PropertyToLoad('KX', GRID_ARRAY_FORMAT_KEYWORDS, self._kx),
            PropertyToLoad('KI', GRID_ARRAY_FORMAT_KEYWORDS, self._kx),
            PropertyToLoad('PERMX', GRID_ARRAY_FORMAT_KEYWORDS, self._kx),
            PropertyToLoad('PERMI', GRID_ARRAY_FORMAT_KEYWORDS, self._kx),
            PropertyToLoad('KY', GRID_ARRAY_FORMAT_KEYWORDS, self._ky),
            PropertyToLoad('KJ', GRID_ARRAY_FORMAT_KEYWORDS, self._ky),
            PropertyToLoad('PERMY', GRID_ARRAY_FORMAT_KEYWORDS, self._ky),
            PropertyToLoad('PERMJ', GRID_ARRAY_FORMAT_KEYWORDS, self._ky),
            PropertyToLoad('KZ', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('KK', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('PERMZ', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('PERMK', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('PVMULT', GRID_ARRAY_FORMAT_KEYWORDS, self.__pvmult),
            PropertyToLoad('CORP', ['VALUE'], self.__corp),
            PropertyToLoad('IEQUIL', GRID_ARRAY_FORMAT_KEYWORDS, self.__iequil),
            PropertyToLoad('IPVT', GRID_ARRAY_FORMAT_KEYWORDS, self.__ipvt),
            PropertyToLoad('IWATER', GRID_ARRAY_FORMAT_KEYWORDS, self.__iwater),
            PropertyToLoad('IRELPM', GRID_ARRAY_FORMAT_KEYWORDS, self.__irelpm),
            PropertyToLoad('IROCK', GRID_ARRAY_FORMAT_KEYWORDS, self.__irock),
            PropertyToLoad('ITRAN', GRID_ARRAY_FORMAT_KEYWORDS, self.__itran),
            PropertyToLoad('IREGION', GRID_ARRAY_FORMAT_KEYWORDS, self.__iregion),
            PropertyToLoad('LIVECELL', GRID_ARRAY_FORMAT_KEYWORDS, self.__livecell),
            PropertyToLoad('WORKA1', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka1),
            PropertyToLoad('WORKA2', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka2),
            PropertyToLoad('WORKA3', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka3),
            PropertyToLoad('WORKA4', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka4),
            PropertyToLoad('WORKA5', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka5),
            PropertyToLoad('WORKA6', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka6),
            PropertyToLoad('WORKA7', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka7),
            PropertyToLoad('WORKA8', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka8),
            PropertyToLoad('WORKA9', GRID_ARRAY_FORMAT_KEYWORDS, self.__worka9),
            PropertyToLoad('DX', GRID_ARRAY_FORMAT_KEYWORDS, self.__dx),
            PropertyToLoad('DY', GRID_ARRAY_FORMAT_KEYWORDS, self.__dy),
            PropertyToLoad('DZ', GRID_ARRAY_FORMAT_KEYWORDS, self.__dz),
            PropertyToLoad('DEPTH', GRID_ARRAY_FORMAT_KEYWORDS, self.__depth),
            PropertyToLoad('MDEPTH', GRID_ARRAY_FORMAT_KEYWORDS, self.__mdepth),
            PropertyToLoad('DZNET', GRID_ARRAY_FORMAT_KEYWORDS, self.__dznet),
            PropertyToLoad('COMPR', GRID_ARRAY_FORMAT_KEYWORDS, self.__compr),
            PropertyToLoad('CR', GRID_ARRAY_FORMAT_KEYWORDS, self.__compr),
            PropertyToLoad('ICOARS', GRID_ARRAY_FORMAT_KEYWORDS, self.__icoars),
            PropertyToLoad('IALPHAF', GRID_ARRAY_FORMAT_KEYWORDS, self.__ialphaf),
            PropertyToLoad('IPOLYMER', GRID_ARRAY_FORMAT_KEYWORDS, self.__ipolymer),
            PropertyToLoad('IADSORPTION', GRID_ARRAY_FORMAT_KEYWORDS, self.__iadsorption),
            PropertyToLoad('ITRACER', GRID_ARRAY_FORMAT_KEYWORDS, self.__itracer),
            PropertyToLoad('IGRID', GRID_ARRAY_FORMAT_KEYWORDS, self.__igrid),
            PropertyToLoad('ISECTOR', GRID_ARRAY_FORMAT_KEYWORDS, self.__isector),
            PropertyToLoad('SWL', GRID_ARRAY_FORMAT_KEYWORDS, self.__swl),
            PropertyToLoad('SWR', GRID_ARRAY_FORMAT_KEYWORDS, self.__swr),
            PropertyToLoad('SWU', GRID_ARRAY_FORMAT_KEYWORDS, self.__swu),
            PropertyToLoad('SGL', GRID_ARRAY_FORMAT_KEYWORDS, self.__sgl),
            PropertyToLoad('SGR', GRID_ARRAY_FORMAT_KEYWORDS, self.__sgr),
            PropertyToLoad('SGU', GRID_ARRAY_FORMAT_KEYWORDS, self.__sgu),
            PropertyToLoad('SWRO', GRID_ARRAY_FORMAT_KEYWORDS, self.__swro),
            PropertyToLoad('SWRO_LS', GRID_ARRAY_FORMAT_KEYWORDS, self.__swro_ls),
            PropertyToLoad('SGRO', GRID_ARRAY_FORMAT_KEYWORDS, self.__sgro),
            PropertyToLoad('SGRW', GRID_ARRAY_FORMAT_KEYWORDS, self.__sgrw),
            PropertyToLoad('KRW_SWRO', GRID_ARRAY_FORMAT_KEYWORDS, self.__krw_swro),
            PropertyToLoad('KRWRO', GRID_ARRAY_FORMAT_KEYWORDS, self.__krw_swro),
            PropertyToLoad('KRWS_LS', GRID_ARRAY_FORMAT_KEYWORDS, self.__krws_ls),
            PropertyToLoad('KRW_SWU', GRID_ARRAY_FORMAT_KEYWORDS, self.__krw_swu),
            PropertyToLoad('KRG_SGRO', GRID_ARRAY_FORMAT_KEYWORDS, self.__krg_sgro),
            PropertyToLoad('KRGRO', GRID_ARRAY_FORMAT_KEYWORDS, self.__krg_sgro),
            PropertyToLoad('KRG_SGU', GRID_ARRAY_FORMAT_KEYWORDS, self.__krg_sgu),
            PropertyToLoad('KRG_SGRW', GRID_ARRAY_FORMAT_KEYWORDS, self.__krg_sgrw),
            PropertyToLoad('KRGRW', GRID_ARRAY_FORMAT_KEYWORDS, self.__krg_sgrw),
            PropertyToLoad('KRO_SWL', GRID_ARRAY_FORMAT_KEYWORDS, self.__kro_swl),
            PropertyToLoad('KROLW', GRID_ARRAY_FORMAT_KEYWORDS, self.__kro_swl),
            PropertyToLoad('KRO_SWR', GRID_ARRAY_FORMAT_KEYWORDS, self.__kro_swr),
            PropertyToLoad('KRO_SGL', GRID_ARRAY_FORMAT_KEYWORDS, self.__kro_sgl),
            PropertyToLoad('KRO_SGR', GRID_ARRAY_FORMAT_KEYWORDS, self.__kro_sgr),
            PropertyToLoad('KRW_SGL', GRID_ARRAY_FORMAT_KEYWORDS, self.__krw_sgl),
            PropertyToLoad('KRW_SGR', GRID_ARRAY_FORMAT_KEYWORDS, self.__krw_sgr),
            PropertyToLoad('SGTR', GRID_ARRAY_FORMAT_KEYWORDS, self.__sgtr),
            PropertyToLoad('SOTR', GRID_ARRAY_FORMAT_KEYWORDS, self.__sotr),
            PropertyToLoad('SWLPC', GRID_ARRAY_FORMAT_KEYWORDS, self.__swlpc),
            PropertyToLoad('SGLPC', GRID_ARRAY_FORMAT_KEYWORDS, self.__sglpc),
            PropertyToLoad('PCW_SWL', GRID_ARRAY_FORMAT_KEYWORDS, self.__pcw_swl),
            PropertyToLoad('PCG_SGU', GRID_ARRAY_FORMAT_KEYWORDS, self.__pcg_sgu),
            PropertyToLoad('CHLORIDE', GRID_ARRAY_FORMAT_KEYWORDS, self.__chloride),
            PropertyToLoad('CALCIUM', GRID_ARRAY_FORMAT_KEYWORDS, self.__calcium),
            PropertyToLoad('SALINITY', GRID_ARRAY_FORMAT_KEYWORDS, self.__salinity),
            PropertyToLoad('SAL', GRID_ARRAY_FORMAT_KEYWORDS, self.__salinity),
            PropertyToLoad('API', GRID_ARRAY_FORMAT_KEYWORDS, self.__api),
            PropertyToLoad('TMX', GRID_ARRAY_FORMAT_KEYWORDS, self.__tmx),
            PropertyToLoad('TMY', GRID_ARRAY_FORMAT_KEYWORDS, self.__tmy),
            PropertyToLoad('TMZ', GRID_ARRAY_FORMAT_KEYWORDS, self.__tmz),
            PropertyToLoad('MULTBV', GRID_ARRAY_FORMAT_KEYWORDS, self.__multbv),
            PropertyToLoad('PV', GRID_ARRAY_FORMAT_KEYWORDS, self.__pv)
        ]

        possible_properties = [prop.token for prop in properties_to_load]

        ignore_line = False

        for idx, line in enumerate(file_as_list):

            # Load in the basic properties
            line_start_token = nfo.get_next_value(0, [line])

            if line_start_token is None:
                continue

            # Confirm we aren't looking at an area that has been commented out. If we are, continue to the next line.
            if line_start_token.upper() == 'NOSKIP':
                ignore_line = False

            if line_start_token.upper() == 'SKIP':
                ignore_line = True

            if ignore_line:
                continue

            if line_start_token is not None and line_start_token.upper() in possible_properties:
                token_property = properties_to_load[possible_properties.index(line_start_token)]
                for modifier in token_property.modifiers:
                    # execute the load
                    StructuredGridOperations.load_token_value_if_present(
                        token_property.token, modifier, token_property.property, line, file_as_list, idx,
                        ['INCLUDE', 'NOLIST'])

                    # check for grid array definitions with paths and add absolute paths
                    grid_array_def = None
                    if isinstance(token_property.property, dict):
                        for ireg_name, grid_array_def in token_property.property.items():
                            if grid_array_def.modifier == 'VALUE' and grid_array_def.value is not None:
                                self.__add_absolute_path_to_grid_array_definition(grid_array_def, idx)
                    else:
                        grid_array_def = token_property.property
                        if grid_array_def.modifier == 'VALUE' and grid_array_def.value is not None:
                            self.__add_absolute_path_to_grid_array_definition(grid_array_def, idx)

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

        self._grid_properties_loaded = True

    @classmethod
    def load_structured_grid_file(cls: type[NexusGrid], structured_grid_file: File,
                                  lazy_loading: bool = True) -> NexusGrid:
        """Loads in a structured grid file with all grid properties, and the array functions defined with 'FUNCTION'.

        Other grid modifiers are currently not supported.

        Args:
            structured_grid_file (NexusFile): the NexusFile representation of a structured grid file for converting \
                into a structured grid file class
            lazy_loading (bool): If set to True, parts of the grid will only be loaded in when requested via \
                properties on the object.

        Raises:
            AttributeError: if no value is found for the structured grid file path
            ValueError: if when loading the grid no values can be found for the NX NY NZ line.

        """
        if structured_grid_file.location is None:
            raise ValueError(f"No file path given or found for structured grid file path. \
                Instead got {structured_grid_file.location}")

        if not isinstance(structured_grid_file, NexusFile):
            raise ValueError(f"Cannot load file of type {type(structured_grid_file)}.")

        loaded_structured_grid_file = cls(grid_nexus_file=structured_grid_file)

        if not lazy_loading:
            loaded_structured_grid_file.load_grid_properties_if_not_loaded()
            loaded_structured_grid_file.load_faults()
            loaded_structured_grid_file.load_array_functions()

        return loaded_structured_grid_file

    @staticmethod
    def update_structured_grid_file(grid_dict: dict[str, GridArrayDefinition | int], model: NexusSimulator) -> None:
        """Save values passed from the front end to the structured grid file and update the class.

        Args:
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
        # for function arrays we need the expanded file contents without includes
        if self.__grid_nexus_file is None or self.__grid_nexus_file.get_flat_list_str_file is None:
            raise ValueError("Cannot load array functions as grid file cannot not found")
        file_contents = self.__grid_nexus_file.get_flat_list_str_file
        self.__array_functions_list = afo.collect_all_function_blocks(file_contents)
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
        self.load_grid_properties_if_not_loaded()
        if not self.__grid_faults_loaded:
            self.load_faults()
        return self.__faults_df

    @staticmethod
    def __keyword_in_include_file_warning(var_entry_obj: GridArrayDefinition) -> None:

        if var_entry_obj.keyword_in_include_file is True:
            warnings.warn('Grid array keyword in include file. This is not recommended simulation practice.')
        else:
            return None

    def __add_absolute_path_to_grid_array_definition(self, grid_array_definition: GridArrayDefinition,
                                                     line_index_of_include_file: int) -> None:
        # cover the trivial case where the path is already absolute
        if grid_array_definition.value is None:
            return
        if os.path.isabs(grid_array_definition.value):
            grid_array_definition.absolute_path = grid_array_definition.value
            return
        if self.__grid_nexus_file is None:
            return
        file_containing_include_line, _ = self.__grid_nexus_file.find_which_include_file(line_index_of_include_file)
        # find the include path from within this include file
        if file_containing_include_line.include_objects is None:
            return
        matching_includes = [x for x in file_containing_include_line.include_objects if
                             grid_array_definition.value in x.location]
        if len(matching_includes) == 0:
            return
        include_file = matching_includes[0]

        absolute_file_path = include_file.location
        grid_array_definition.absolute_path = absolute_file_path

    @property
    def array_functions(self) -> Optional[list[NexusGridArrayFunction]]:
        """Returns a list of the array functions defined in the structured grid file."""
        self.load_grid_properties_if_not_loaded()
        if self.__grid_array_functions is None:
            self.load_array_functions()
        return self.__grid_array_functions

    @property
    def corp(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        NexusGrid.__keyword_in_include_file_warning(self.__corp)

        return self.__corp

    @property
    def iequil(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__iequil

    @property
    def ipvt(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__ipvt

    @property
    def iwater(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__iwater

    @property
    def irelpm(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__irelpm

    @property
    def irock(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__irock

    @property
    def itran(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__itran

    @property
    def iregion(self) -> dict[str, GridArrayDefinition]:
        self.load_grid_properties_if_not_loaded()
        return self.__iregion

    @property
    def livecell(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__livecell

    @property
    def pvmult(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__pvmult

    @property
    def worka1(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka1

    @property
    def worka2(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka2

    @property
    def worka3(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka3

    @property
    def worka4(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka4

    @property
    def worka5(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka5

    @property
    def worka6(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka6

    @property
    def worka7(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka7

    @property
    def worka8(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka8

    @property
    def worka9(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__worka9

    @property
    def dx(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__dx

    @property
    def dy(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__dy

    @property
    def dz(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__dz

    @property
    def depth(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__depth

    @property
    def mdepth(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__mdepth

    @property
    def dznet(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__dznet

    @property
    def compr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__compr

    @property
    def icoars(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__icoars

    @property
    def ialphaf(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__ialphaf

    @property
    def ipolymer(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__ipolymer

    @property
    def iadsorption(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__iadsorption

    @property
    def itracer(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__itracer

    @property
    def igrid(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__igrid

    @property
    def isector(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__isector

    @property
    def swl(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__swl

    @property
    def swr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__swr

    @property
    def swu(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__swu

    @property
    def sgl(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sgl

    @property
    def sgr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sgr

    @property
    def sgu(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sgu

    @property
    def swro(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__swro

    @property
    def swro_ls(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__swro_ls

    @property
    def sgro(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sgro

    @property
    def sgrw(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sgrw

    @property
    def krw_swro(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krw_swro

    @property
    def krws_ls(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krws_ls

    @property
    def krw_swu(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krw_swu

    @property
    def krg_sgro(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krg_sgro

    @property
    def krg_sgu(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krg_sgu

    @property
    def krg_sgrw(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krg_sgrw

    @property
    def kro_swl(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__kro_swl

    @property
    def kro_swr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__kro_swr

    @property
    def kro_sgl(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__kro_sgl

    @property
    def kro_sgr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__kro_sgr

    @property
    def krw_sgl(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krw_sgl

    @property
    def krw_sgr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__krw_sgr

    @property
    def sgtr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sgtr

    @property
    def sotr(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sotr

    @property
    def swlpc(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__swlpc

    @property
    def sglpc(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__sglpc

    @property
    def pcw_swl(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__pcw_swl

    @property
    def pcg_sgu(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__pcg_sgu

    @property
    def chloride(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__chloride

    @property
    def calcium(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__calcium

    @property
    def salinity(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__salinity

    @property
    def api(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__api

    @property
    def tmx(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__tmx

    @property
    def tmy(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__tmy

    @property
    def tmz(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__tmz

    @property
    def multbv(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__multbv

    @property
    def pv(self) -> GridArrayDefinition:
        self.load_grid_properties_if_not_loaded()
        return self.__pv
