"""Nexus grid file class for loading in a structured grid file and extracting the grid properties."""
from __future__ import annotations

import copy

import pandas as pd
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING, Any, Final
import warnings

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.FileOperations.File import File
from ResSimpy.DataModelBaseClasses.Grid import Grid
from ResSimpy.DataModelBaseClasses.GridArrayDefinition import GridArrayDefinition
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusFtrans import NexusFtrans
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusLGRs import NexusLGRs
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusMultir import NexusMultir
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusOver import NexusOver
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusTOver import NexusTOver
from ResSimpy.Nexus.NexusKeywords.nexus_keywords import VALID_NEXUS_KEYWORDS
from ResSimpy.Nexus.NexusKeywords.structured_grid_keywords import GRID_ARRAY_FORMAT_KEYWORDS
from ResSimpy.Nexus.structured_grid_operations import StructuredGridOperations
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.Nexus.array_function_operations as afo
from ResSimpy.FileOperations import file_operations as fo
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
    _iregion: dict[str, GridArrayDefinition]
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
    __kxeff: GridArrayDefinition
    __kyeff: GridArrayDefinition
    __kzeff: GridArrayDefinition
    __grid_multir_loaded: bool = False
    __multir: Optional[list[NexusMultir]] = None
    __lgrs: NexusLGRs
    __overs: list[NexusOver] = field(default_factory=list)
    __tovers: list[NexusTOver] = field(default_factory=list)
    __ftrans: list[NexusFtrans] = field(default_factory=list)
    __model_unit_system: UnitSystem

    def __init__(self, model_unit_system: UnitSystem, grid_nexus_file: Optional[NexusFile] = None,
                 assume_loaded: bool = False,
                 ) -> None:
        """Initialises the NexusGrid class.

        Args:
            model_unit_system (UnitSystem): the default unit system to use for the model.
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
        self._iregion: dict[str, GridArrayDefinition] = {}
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
        self.__kxeff: GridArrayDefinition = GridArrayDefinition()
        self.__kyeff: GridArrayDefinition = GridArrayDefinition()
        self.__kzeff: GridArrayDefinition = GridArrayDefinition()

        self.__lgrs: NexusLGRs = NexusLGRs(grid_file_as_list=self.__grid_file_contents, parent_grid=self)
        self.__overs: list[NexusOver] = []
        self.__tovers: list[NexusTOver] = []
        self.__ftrans: list[NexusFtrans] = []
        self.__model_unit_system: UnitSystem = model_unit_system

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
        """Returns a dictionary representation of grid array.
        Checks if grid properties are not loaded and loads them.
        """
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

    @staticmethod
    def keyword_mapping() -> dict[str, tuple[str, type]]:
        """Returns the keyword mapping for the NexusGrid class."""
        keyword_map = {
            'NETGRS': ('netgrs', GridArrayDefinition),
            'POROSITY': ('porosity', GridArrayDefinition),
            'POR': ('porosity', GridArrayDefinition),
            'SW': ('sw', GridArrayDefinition),
            'SG': ('sg', GridArrayDefinition),
            'PRESSURE': ('pressure', GridArrayDefinition),
            'P': ('pressure', GridArrayDefinition),
            'TEMPERATURE': ('temperature', GridArrayDefinition),
            'TEMP': ('temperature', GridArrayDefinition),
            'KX': ('kx', GridArrayDefinition),
            'KI': ('kx', GridArrayDefinition),
            'PERMX': ('kx', GridArrayDefinition),
            'PERMI': ('kx', GridArrayDefinition),
            'KY': ('ky', GridArrayDefinition),
            'KXEFF': ('kxeff', GridArrayDefinition),
            'KYEFF': ('kyeff', GridArrayDefinition),
            'KZEFF': ('kzeff', GridArrayDefinition),
            'KJ': ('ky', GridArrayDefinition),
            'PERMY': ('ky', GridArrayDefinition),
            'PERMJ': ('ky', GridArrayDefinition),
            'KZ': ('kz', GridArrayDefinition),
            'KK': ('kz', GridArrayDefinition),
            'PERMZ': ('kz', GridArrayDefinition),
            'PERMK': ('kz', GridArrayDefinition),
            'IREGION': ('iregion', dict),
            'PVMULT': ('pvmult', GridArrayDefinition),
            'CORP': ('corp', GridArrayDefinition),
            'IEQUIL': ('iequil', GridArrayDefinition),
            'IPVT': ('ipvt', GridArrayDefinition),
            'IWATER': ('iwater', GridArrayDefinition),
            'IRELPM': ('irelpm', GridArrayDefinition),
            'IROCK': ('irock', GridArrayDefinition),
            'ITRAN': ('itran', GridArrayDefinition),
            'LIVECELL': ('livecell', GridArrayDefinition),
            'WORKA1': ('worka1', GridArrayDefinition),
            'WORKA2': ('worka2', GridArrayDefinition),
            'WORKA3': ('worka3', GridArrayDefinition),
            'WORKA4': ('worka4', GridArrayDefinition),
            'WORKA5': ('worka5', GridArrayDefinition),
            'WORKA6': ('worka6', GridArrayDefinition),
            'WORKA7': ('worka7', GridArrayDefinition),
            'WORKA8': ('worka8', GridArrayDefinition),
            'WORKA9': ('worka9', GridArrayDefinition),
            'DX': ('dx', GridArrayDefinition),
            'DY': ('dy', GridArrayDefinition),
            'DZ': ('dz', GridArrayDefinition),
            'DEPTH': ('depth', GridArrayDefinition),
            'MDEPTH': ('mdepth', GridArrayDefinition),
            'DZNET': ('dznet', GridArrayDefinition),
            'COMPR': ('compr', GridArrayDefinition),
            'ICOARS': ('icoars', GridArrayDefinition),
            'IALPHAF': ('ialphaf', GridArrayDefinition),
            'IPOLYMER': ('ipolymer', GridArrayDefinition),
            'IADSORPTION': ('iadsorption', GridArrayDefinition),
            'ITRACER': ('itracer', GridArrayDefinition),
            'IGRID': ('igrid', GridArrayDefinition),
            'ISECTOR': ('isector', GridArrayDefinition),
            'SWL': ('swl', GridArrayDefinition),
            'SWR': ('swr', GridArrayDefinition),
            'SWU': ('swu', GridArrayDefinition),
            'SGL': ('sgl', GridArrayDefinition),
            'SGR': ('sgr', GridArrayDefinition),
            'SGU': ('sgu', GridArrayDefinition),
            'SWRO': ('swro', GridArrayDefinition),
            'SWRO_LS': ('swro_ls', GridArrayDefinition),
            'SGRO': ('sgro', GridArrayDefinition),
            'SGRW': ('sgrw', GridArrayDefinition),
            'KRW_SWRO': ('krw_swro', GridArrayDefinition),
            'KRWS_LS': ('krws_ls', GridArrayDefinition),
            'KRW_SWU': ('krw_swu', GridArrayDefinition),
            'KRG_SGRO': ('krg_sgro', GridArrayDefinition),
            'KRG_SGU': ('krg_sgu', GridArrayDefinition),
            'KRG_SGRW': ('krg_sgrw', GridArrayDefinition),
            'KRO_SWL': ('kro_swl', GridArrayDefinition),
            'KRO_SWR': ('kro_swr', GridArrayDefinition),
            'KRO_SGL': ('kro_sgl', GridArrayDefinition),
            'KRO_SGR': ('kro_sgr', GridArrayDefinition),
            'KRW_SGL': ('krw_sgl', GridArrayDefinition),
            'KRW_SGR': ('krw_sgr', GridArrayDefinition),
            'SGTR': ('sgtr', GridArrayDefinition),
            'SOTR': ('sotr', GridArrayDefinition),
            'SWLPC': ('swlpc', GridArrayDefinition),
            'SGLPC': ('sglpc', GridArrayDefinition),
            'PCW_SWL': ('pcw_swl', GridArrayDefinition),
            'PCG_SGU': ('pcg_sgu', GridArrayDefinition),
            'CHLORIDE': ('chloride', GridArrayDefinition),
            'CALCIUM': ('calcium', GridArrayDefinition),
            'SALINITY': ('salinity', GridArrayDefinition),
            'API': ('api', GridArrayDefinition),
            'TMX': ('tmx', GridArrayDefinition),
            'TMY': ('tmy', GridArrayDefinition),
            'TMZ': ('tmz', GridArrayDefinition),
            'MULTBV': ('multbv', GridArrayDefinition),
            'PV': ('pv', GridArrayDefinition),

        }
        return keyword_map

    def load_grid_properties_if_not_loaded(self) -> None:
        """Checks if grid properties are not loaded and loads them."""

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

        self.lgrs.load_lgrs()

        if self.__grid_nexus_file is None or self.__grid_file_contents is None or self.__grid_file_nested is None:
            raise ValueError("Grid file not found, cannot load grid properties")

        # Strip file of comments
        file_as_list_with_original_line_numbers = []
        for i, line in enumerate(self.__grid_file_contents):
            cleaned_line = nfo.strip_file_of_comments([line], comment_characters=['!', 'C'])
            if len(cleaned_line) == 0 or cleaned_line[0].strip() == '':
                pass
            else:
                file_as_list_with_original_line_numbers.append((i, cleaned_line[0]))

        file_as_list = [line for _, line in file_as_list_with_original_line_numbers]

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
            PropertyToLoad('KXEFF', GRID_ARRAY_FORMAT_KEYWORDS, self.__kxeff),
            PropertyToLoad('KYEFF', GRID_ARRAY_FORMAT_KEYWORDS, self.__kyeff),
            PropertyToLoad('KZEFF', GRID_ARRAY_FORMAT_KEYWORDS, self.__kzeff),
            PropertyToLoad('KJ', GRID_ARRAY_FORMAT_KEYWORDS, self._ky),
            PropertyToLoad('PERMY', GRID_ARRAY_FORMAT_KEYWORDS, self._ky),
            PropertyToLoad('PERMJ', GRID_ARRAY_FORMAT_KEYWORDS, self._ky),
            PropertyToLoad('KZ', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('KK', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('PERMZ', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('PERMK', GRID_ARRAY_FORMAT_KEYWORDS, self._kz),
            PropertyToLoad('IREGION', GRID_ARRAY_FORMAT_KEYWORDS, self._iregion),
            PropertyToLoad('PVMULT', GRID_ARRAY_FORMAT_KEYWORDS, self.__pvmult),
            PropertyToLoad('CORP', ['VALUE'], self.__corp),
            PropertyToLoad('IEQUIL', GRID_ARRAY_FORMAT_KEYWORDS, self.__iequil),
            PropertyToLoad('IPVT', GRID_ARRAY_FORMAT_KEYWORDS, self.__ipvt),
            PropertyToLoad('IWATER', GRID_ARRAY_FORMAT_KEYWORDS, self.__iwater),
            PropertyToLoad('IRELPM', GRID_ARRAY_FORMAT_KEYWORDS, self.__irelpm),
            PropertyToLoad('IROCK', GRID_ARRAY_FORMAT_KEYWORDS, self.__irock),
            PropertyToLoad('ITRAN', GRID_ARRAY_FORMAT_KEYWORDS, self.__itran),
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
        array_name = 'ROOT'
        property_dict: dict = {}
        unit_system = self.__model_unit_system

        for idx, (original_line_location, line) in enumerate(file_as_list_with_original_line_numbers):

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

            nfo.check_property_in_line(line, property_dict, file_as_list)
            unit_system = property_dict.get('UNIT_SYSTEM', self.__model_unit_system)

            if nfo.check_token('ARRAYS', line):
                temp_array_name = fo.get_token_value('ARRAYS', line, [line])
                if temp_array_name is None:
                    array_name = 'ROOT'
                else:
                    array_name = temp_array_name

            if line_start_token is not None and line_start_token.upper() in possible_properties:
                token_property = properties_to_load[possible_properties.index(line_start_token)]
                for modifier in token_property.modifiers:
                    # execute the load
                    if array_name == 'ROOT':
                        StructuredGridOperations.load_token_value_if_present(
                            token_property.token, modifier, token_property.property, line, file_as_list, idx,
                            grid_nexus_file=self.__grid_nexus_file, ignore_values=['INCLUDE', 'NOLIST'],
                            original_line_location=original_line_location)
                    else:
                        # get the LGR object to add the grid array to:
                        lgr = self.lgrs.get(array_name)
                        attribute_name = self.keyword_mapping()[token_property.token][0]
                        grid_array_def_to_modify = getattr(lgr, attribute_name)
                        StructuredGridOperations.load_token_value_if_present(
                            token_property.token, modifier, grid_array_def_to_modify, line, file_as_list, idx,
                            grid_nexus_file=self.__grid_nexus_file, ignore_values=['INCLUDE', 'NOLIST'],
                            original_line_location=original_line_location)

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

        # load the overs:
        if fo.value_in_file('OVER', file_as_list):
            self.__overs = NexusGrid.load_nexus_overs(file_as_list)
        if fo.value_in_file('FTRANS', file_as_list):
            self.__ftrans = NexusGrid.load_nexus_ftrans(file_as_list, unit_system)
        if fo.value_in_file('TOVER', file_as_list):
            self.__tovers = NexusGrid.load_nexus_tovers(file_as_list)

        self._grid_properties_loaded = True

    @classmethod
    def load_structured_grid_file(cls: type[NexusGrid], structured_grid_file: File,
                                  model_unit_system: UnitSystem, lazy_loading: bool = True,
                                  ) -> NexusGrid:
        """Loads in a structured grid file with all grid properties, and the array functions defined with 'FUNCTION'.

        Other grid modifiers are currently not supported.

        Args:
            structured_grid_file (NexusFile): the NexusFile representation of a structured grid file for converting \
                into a structured grid file class
            model_unit_system (UnitSystem): the default unit system to use for the model
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

        loaded_structured_grid_file = cls(grid_nexus_file=structured_grid_file, model_unit_system=model_unit_system)

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
        """Loads collection of array function defined in the nexus grid file."""
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

    def load_multir(self) -> None:
        """Function to read MULTIR in Nexus grid file."""
        file_content_as_list = self.__grid_file_contents
        if file_content_as_list is None:
            raise ValueError('Grid file contents have not been loaded')
        multir_list = self.load_nexus_multir_table_from_list(file_content_as_list)
        self.__multir = multir_list
        self.__grid_multir_loaded = True

    @staticmethod
    def load_nexus_multir_table_from_list(file_content_as_list: list[str]) -> list[NexusMultir]:
        """Function to read MULTIR from a file represented as a list."""
        start_idx = -1
        end_idx = -1

        valid_end_tokens = VALID_NEXUS_KEYWORDS
        skip_tokens = ['X', 'Y', 'Z', 'XYZ', 'ALL', 'STD', 'NONSTD']
        valid_end_tokens = [x for x in valid_end_tokens if x not in skip_tokens]
        multir_lists: list[NexusMultir] = []

        for idx, line in enumerate(file_content_as_list):
            if nfo.nexus_token_found(line, valid_end_tokens):
                end_idx = idx
            if idx == len(file_content_as_list) - 1:
                end_idx = idx + 1

            if 0 < start_idx < end_idx - 1:
                for multir_line in file_content_as_list[start_idx:end_idx]:
                    new_multir = NexusGrid.__extract_multir_tableline(multir_line)
                    if new_multir is not None:
                        multir_lists.append(new_multir)
                start_idx = -1
                end_idx = -1

            if nfo.check_token('MULTIR', line):
                start_idx = idx + 1
                continue
        # if no MULTIR table is found, return an empty list
        return multir_lists

    @staticmethod
    def __extract_multir_tableline(line: str) -> None | NexusMultir:
        """Takes a single line in a file and extracts a Multir object from it."""
        stored_values = nfo.split_line(line)
        if not stored_values:
            return None
        region_1_str, region_2_str, tmult_str = stored_values[0:3]
        region_1 = int(region_1_str)
        region_2 = int(region_2_str)
        tmult = float(tmult_str)

        direction = ''
        for ele in stored_values:
            if 'X' in ele:
                direction += 'X'
            if 'Y' in ele:
                direction += 'Y'
            if 'Z' in ele:
                direction += 'Z'

        if direction == '':
            # default to all directions
            direction = 'XYZ'

        standard_connections = True
        non_standard_connections = True
        if 'STD' in stored_values and 'NONSTD' not in stored_values:
            standard_connections = True
            non_standard_connections = False
        if 'NONSTD' in stored_values and 'STD' not in stored_values:
            standard_connections = False
            non_standard_connections = True
        if 'ALL' in stored_values or ('STD' not in stored_values and 'NONSTD' not in stored_values):
            standard_connections = True
            non_standard_connections = True
        return NexusMultir(region_1=region_1, region_2=region_2, tmult=tmult, directions=direction,
                           std_connections=standard_connections, non_std_connections=non_standard_connections)

    def get_multir(self) -> list[NexusMultir]:
        """Returns the MULTIR information as a list of multir objects."""
        self.load_grid_properties_if_not_loaded()
        if not self.__grid_multir_loaded:
            self.load_multir()
        return self.__multir if self.__multir is not None else []

    @staticmethod
    def __keyword_in_include_file_warning(var_entry_obj: GridArrayDefinition) -> None:

        if var_entry_obj.keyword_in_include_file is True:
            warnings.warn('Grid array keyword in include file. This is not recommended simulation practice.')
        else:
            return None

    @property
    def array_functions(self) -> Optional[list[NexusGridArrayFunction]]:
        """Returns a list of the array functions defined in the structured grid file."""
        self.load_grid_properties_if_not_loaded()
        if self.__grid_array_functions is None:
            self.load_array_functions()
        return self.__grid_array_functions

    @property
    def corp(self) -> GridArrayDefinition:
        """Returns corp grid property.
        Ensures grid properties are loaded and returns value of 'corp'.
        """
        self.load_grid_properties_if_not_loaded()
        NexusGrid.__keyword_in_include_file_warning(self.__corp)

        return self.__corp

    @property
    def iequil(self) -> GridArrayDefinition:
        """Returns iequil grid property.
        Ensures grid properties are loaded and returns value of 'iequil'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__iequil

    @property
    def ipvt(self) -> GridArrayDefinition:
        """Returns ipvt grid property.
        Ensures grid properties are loaded and returns value of 'ipvt'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__ipvt

    @property
    def iwater(self) -> GridArrayDefinition:
        """Returns iwater grid property.
        Ensures grid properties are loaded and returns value of 'iwater'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__iwater

    @property
    def irelpm(self) -> GridArrayDefinition:
        """Returns irelpm grid property.
        Ensures grid properties are loaded and returns value of 'irelpm'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__irelpm

    @property
    def irock(self) -> GridArrayDefinition:
        """Returns irock grid property.
        Ensures grid properties are loaded and returns value of 'irock'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__irock

    @property
    def itran(self) -> GridArrayDefinition:
        """Returns itran grid property.
        Ensures grid properties are loaded and returns value of 'itran'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__itran

    @property
    def iregion(self) -> dict[str, GridArrayDefinition]:
        """Returns iregion grid property.
        Ensures grid properties are loaded and returns value of 'iregion'.
        """
        self.load_grid_properties_if_not_loaded()
        return self._iregion

    @property
    def livecell(self) -> GridArrayDefinition:
        """Returns livecell grid property.
        Ensures grid properties are loaded and returns value of 'livecell'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__livecell

    @property
    def pvmult(self) -> GridArrayDefinition:
        """Returns pvmult grid property.
        Ensures grid properties are loaded and returns value of 'pv_mult'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__pvmult

    @property
    def worka1(self) -> GridArrayDefinition:
        """Returns worka1 grid property.
        Ensures grid properties are loaded and returns value of 'worka1'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka1

    @property
    def worka2(self) -> GridArrayDefinition:
        """Returns worka2 grid property.
        Ensures grid properties are loaded and returns value of 'worka2'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka2

    @property
    def worka3(self) -> GridArrayDefinition:
        """Returns worka3 grid property.
        Ensures grid properties are loaded and returns value of 'worka3'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka3

    @property
    def worka4(self) -> GridArrayDefinition:
        """Returns worka4 grid property.
        Ensures grid properties are loaded and returns value of 'worka4'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka4

    @property
    def worka5(self) -> GridArrayDefinition:
        """Returns worka5 grid property.
        Ensures grid properties are loaded and returns value of 'worka5'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka5

    @property
    def worka6(self) -> GridArrayDefinition:
        """Returns worka6 grid property.
        Ensures grid properties are loaded and returns value of 'worka6'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka6

    @property
    def worka7(self) -> GridArrayDefinition:
        """Returns worka7 grid property.
        Ensures grid properties are loaded and returns value of 'worka7'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka7

    @property
    def worka8(self) -> GridArrayDefinition:
        """Returns worka8 grid property.
        Ensures grid properties are loaded and returns value of 'worka8'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka8

    @property
    def worka9(self) -> GridArrayDefinition:
        """Returns worka9 grid property.
        Ensures grid properties are loaded and returns value of 'worka9'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__worka9

    @property
    def dx(self) -> GridArrayDefinition:
        """Returns dx grid property.
        Ensures grid properties are loaded and returns value of 'dx'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__dx

    @property
    def dy(self) -> GridArrayDefinition:
        """Returns dy grid property.
        Ensures grid properties are loaded and returns value of 'dy'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__dy

    @property
    def dz(self) -> GridArrayDefinition:
        """Returns dz grid property.
        Ensures grid properties are loaded and returns value of 'dz'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__dz

    @property
    def depth(self) -> GridArrayDefinition:
        """Returns depth grid property.
        Ensures grid properties are loaded and returns value of 'depth'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__depth

    @property
    def mdepth(self) -> GridArrayDefinition:
        """Returns mdepth grid property.
        Ensures grid properties are loaded and returns value of 'mdepth'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__mdepth

    @property
    def dznet(self) -> GridArrayDefinition:
        """Returns dznet grid property.
        Ensures grid properties are loaded and returns value of 'dznet'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__dznet

    @property
    def compr(self) -> GridArrayDefinition:
        """Returns compr grid property.
        Ensures grid properties are loaded and returns value of 'compr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__compr

    @property
    def icoars(self) -> GridArrayDefinition:
        """Returns icoars grid property.
        Ensures grid properties are loaded and returns value of 'icoars'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__icoars

    @property
    def ialphaf(self) -> GridArrayDefinition:
        """Returns ialphaf grid property.
        Ensures grid properties are loaded and returns value of 'ialphaf'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__ialphaf

    @property
    def ipolymer(self) -> GridArrayDefinition:
        """Returns ipolymer grid property.
        Ensures grid properties are loaded and returns value of 'ipolymer'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__ipolymer

    @property
    def iadsorption(self) -> GridArrayDefinition:
        """Returns iadsorption grid property.
        Ensures grid properties are loaded and returns value of 'iadsorption'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__iadsorption

    @property
    def itracer(self) -> GridArrayDefinition:
        """Returns itracer grid property.
        Ensures grid properties are loaded and returns value of 'itracer'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__itracer

    @property
    def igrid(self) -> GridArrayDefinition:
        """Returns igrid grid property.
        Ensures grid properties are loaded and returns value of 'igrid'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__igrid

    @property
    def isector(self) -> GridArrayDefinition:
        """Returns isector grid property.
        Ensures grid properties are loaded and returns value of 'isector'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__isector

    @property
    def swl(self) -> GridArrayDefinition:
        """Returns swl grid property.
        Ensures grid properties are loaded and returns value of 'swl'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__swl

    @property
    def swr(self) -> GridArrayDefinition:
        """Returns swr grid property.
        Ensures grid properties are loaded and returns value of 'swr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__swr

    @property
    def swu(self) -> GridArrayDefinition:
        """Returns swu grid property.
        Ensures grid properties are loaded and returns value of 'swu'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__swu

    @property
    def sgl(self) -> GridArrayDefinition:
        """Returns sgl grid property.
        Ensures grid properties are loaded and returns value of 'sgl'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sgl

    @property
    def sgr(self) -> GridArrayDefinition:
        """Returns sgr grid property.
        Ensures grid properties are loaded and returns value of 'sgr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sgr

    @property
    def sgu(self) -> GridArrayDefinition:
        """Returns sgu grid property.
        Ensures grid properties are loaded and returns value of 'sgu'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sgu

    @property
    def swro(self) -> GridArrayDefinition:
        """Returns swro grid property.
        Ensures grid properties are loaded and returns value of 'swro'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__swro

    @property
    def swro_ls(self) -> GridArrayDefinition:
        """Returns swro_ls grid property.
        Ensures grid properties are loaded and returns value of 'swro_ls'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__swro_ls

    @property
    def sgro(self) -> GridArrayDefinition:
        """Returns sgro grid property.
        Ensures grid properties are loaded and returns value of 'sgro'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sgro

    @property
    def sgrw(self) -> GridArrayDefinition:
        """Returns sgrw grid property.
        Ensures grid properties are loaded and returns value of 'sgrw'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sgrw

    @property
    def krw_swro(self) -> GridArrayDefinition:
        """Returns krw_swro grid property.
        Ensures grid properties are loaded and returns value of 'krw_swro'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krw_swro

    @property
    def krws_ls(self) -> GridArrayDefinition:
        """Returns krws_ls grid property.
        Ensures grid properties are loaded and returns value of 'krws_ls'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krws_ls

    @property
    def krw_swu(self) -> GridArrayDefinition:
        """Returns krw_swu grid property.
        Ensures grid properties are loaded and returns value of 'krw_swu'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krw_swu

    @property
    def krg_sgro(self) -> GridArrayDefinition:
        """Returns kro_sgro grid property.
        Ensures grid properties are loaded and returns value of 'krg_sgro'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krg_sgro

    @property
    def krg_sgu(self) -> GridArrayDefinition:
        """Returns krg_sgu grid property.
        Ensures grid properties are loaded and returns value of 'krg_sgu'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krg_sgu

    @property
    def krg_sgrw(self) -> GridArrayDefinition:
        """Returns kro_sgrw grid property.
        Ensures grid properties are loaded and returns value of 'krg_sgrw'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krg_sgrw

    @property
    def kro_swl(self) -> GridArrayDefinition:
        """Returns kro_swl grid property.
        Ensures grid properties are loaded and returns value of 'kro_swl'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__kro_swl

    @property
    def kro_swr(self) -> GridArrayDefinition:
        """Returns kro_swr grid property.
        Ensures grid properties are loaded and returns value of 'kro_swr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__kro_swr

    @property
    def kro_sgl(self) -> GridArrayDefinition:
        """Returns kro_sgl grid property.
        Ensures grid properties are loaded and returns value of 'kro_sgl'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__kro_sgl

    @property
    def kro_sgr(self) -> GridArrayDefinition:
        """Returns kro_sgr grid property.
        Ensures grid properties are loaded and returns value of 'kro_sgr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__kro_sgr

    @property
    def krw_sgl(self) -> GridArrayDefinition:
        """Returns krw_sgl grid property.
        Ensures grid properties are loaded and returns value of 'krw_sgl'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krw_sgl

    @property
    def krw_sgr(self) -> GridArrayDefinition:
        """Returns krw_sgr grid property.
        Ensures grid properties are loaded and returns value of 'krw_sgr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__krw_sgr

    @property
    def sgtr(self) -> GridArrayDefinition:
        """"Returns sgtr grid property.
        Ensures gir properties are loaded and returns value of 'sgtr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sgtr

    @property
    def sotr(self) -> GridArrayDefinition:
        """"Returns sotr grid property.
        Ensures grid properties are loaded and returns value of 'sotr'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sotr

    @property
    def swlpc(self) -> GridArrayDefinition:
        """Returns swlpc grid property.
        Ensures grid properties are loaded and returns value of 'swlpc'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__swlpc

    @property
    def sglpc(self) -> GridArrayDefinition:
        """Returns sglpc property.
        Ensures grid properties are loaded and returns value of 'sglpc'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__sglpc

    @property
    def pcw_swl(self) -> GridArrayDefinition:
        """Returns pcw_swl property.
        Ensures grid properties are loaded and returns value of 'pcw_swl'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__pcw_swl

    @property
    def pcg_sgu(self) -> GridArrayDefinition:
        """Returns pcg_sgu grid proprety.
        Ensures grid properties are loaded and returns value of 'pcg_sgu'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__pcg_sgu

    @property
    def chloride(self) -> GridArrayDefinition:
        """Returns chloride grid property.
        Ensures grid properties are loaded and returns value of 'chloride'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__chloride

    @property
    def calcium(self) -> GridArrayDefinition:
        """Returns calcium grid property.
        Ensures grid properties are loaded and returns value of 'calcium'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__calcium

    @property
    def salinity(self) -> GridArrayDefinition:
        """Returns grid salinity.
        Ensures grid properties are loaded and returns the value 'salinity'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__salinity

    @property
    def api(self) -> GridArrayDefinition:
        """Returns grid api.
        Ensures grid properties are loaded and returns value of 'api'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__api

    @property
    def tmx(self) -> GridArrayDefinition:
        """Returns gird tmx.
        Ensures grid properties are loaded and returns value of 'tmx'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__tmx

    @property
    def tmy(self) -> GridArrayDefinition:
        """Returns grid tmy.
        Ensures grid properties are loaded and returns value of 'tmy'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__tmy

    @property
    def tmz(self) -> GridArrayDefinition:
        """Returns grid tmz.
        Ensures gird properties are loaded and returns value if 'tmz'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__tmz

    @property
    def multbv(self) -> GridArrayDefinition:
        """Returns grid multvb.
        Ensures grid properties are loaded and returns value of 'multvb'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__multbv

    @property
    def pv(self) -> GridArrayDefinition:
        """Returns grid pv.
        Ensures grid properties are loaded and returns value of 'pv'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__pv

    @property
    def kxeff(self) -> GridArrayDefinition:
        """Returns the kxeff grid property.
        Ensures grid properties are loaded and returns value of 'kxeff'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__kxeff

    @property
    def kyeff(self) -> GridArrayDefinition:
        """Returns the kyeff grid property.
        Ensures grid properties are loaded and returns value of 'kyeff'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__kyeff

    @property
    def kzeff(self) -> GridArrayDefinition:
        """Returns the kzeff grid property.
        Ensures grid properties are loaded and returns value of 'kzeff'.
        """
        self.load_grid_properties_if_not_loaded()
        return self.__kzeff

    @property
    def multir(self) -> list[NexusMultir]:
        """Returns the MULTIR table as a list of multir objects."""
        return self.get_multir()

    @property
    def lgrs(self) -> NexusLGRs:
        """Returns the LGR object which contains a list of the LGRs in the nexus grid."""
        return self.__lgrs

    @staticmethod
    def load_nexus_overs(file_content_as_list: list[str]) -> list[NexusOver]:
        """Function to read in OVER tables from a file.

        Args:
            file_content_as_list (list[str]): list of strings representing the file contents.

        Returns:
            list[NexusOver]: list of NexusOver objects representing the OVER table.
        """
        ignore_list = ['OVER', 'TX', 'TY', 'TZ', 'PV', 'PVF', 'TXF', 'TYF', 'TZF', 'GRID', 'FNAME', 'GE', 'LE', 'ROOT']
        valid_end_tokens = [x for x in VALID_NEXUS_KEYWORDS if x not in ignore_list]
        overs_list: list[NexusOver] = []
        reading_over = False
        grid = 'ROOT'
        fname = None
        arrays: list[str] = []
        potential_operators: Final = ['+', '-', '*', '/', '=']
        threshold_value = None
        for line in file_content_as_list:
            if nfo.nexus_token_found(line, valid_end_tokens):
                reading_over = False
                grid = 'ROOT'
                fname = None
                arrays = []
                continue
            if reading_over:
                split_line = nfo.split_line(line)
                if nfo.check_token('GRID', line):
                    grid = nfo.get_expected_token_value('GRID', line, file_content_as_list)
                if nfo.check_token('FNAME', line):
                    fname = nfo.get_expected_token_value('FNAME', line, file_content_as_list)
                if len(split_line) > 6:
                    i1, i2, j1, j2, k1, k2 = (int(x) for x in split_line[0:6])
                    # cut out the ranges
                    split_line = split_line[6:]
                    for array in arrays:
                        operator_value = split_line[0]
                        operator_matches = [x for x in potential_operators if x == operator_value[0]]
                        if not operator_matches and ('GE' in split_line or 'LE' in split_line):
                            # if the operator is not found then it is GE or LE
                            value = float(split_line[0])
                            operator = split_line[1]
                            threshold_value = float(split_line[2])
                            split_line_position = 3
                        elif operator_matches:
                            operator = operator_matches[0]
                            # remove the operator and the remaining string is the value
                            trimmed_value = split_line[0].replace(operator, '')
                            if trimmed_value == '':
                                # then the value is in the next element of split_line
                                value = float(split_line[1])
                                split_line_position = 2
                            else:
                                value = float(split_line[0][1:])
                                split_line_position = 1
                        else:
                            # no operator match and not GE or LE then it is implicitly '*'
                            value = float(split_line[0])
                            operator = '*'
                            split_line_position = 1
                        overs_list.append(NexusOver(array=array, grid=grid, fault_name=fname,
                                                    i1=i1, i2=i2, j1=j1, j2=j2, k1=k1, k2=k2, operator=operator,
                                                    value=value, threshold=threshold_value))
                        split_line = split_line[split_line_position:]
                        threshold_value = None

            if nfo.check_token('OVER', line):
                reading_over = True
                over_split_line = nfo.split_line(line)
                arrays = over_split_line[over_split_line.index('OVER') + 1:]

        return overs_list

    @property
    def overs(self) -> list[NexusOver]:
        """Returns the OVER table as a list of NexusOver objects."""
        if not self._grid_properties_loaded:
            self.load_grid_properties_if_not_loaded()
        return self.__overs

    @property
    def tovers(self) -> list[NexusTOver]:
        """Returns the TOVER table as a list of NexusTOver objects."""
        if not self._grid_properties_loaded:
            self.load_grid_properties_if_not_loaded()
        return self.__tovers

    @staticmethod
    def load_nexus_tovers(file_content_as_list: list[str]) -> list[NexusTOver]:
        """Loads the Nexus TOVER tables to a list of objects.

        Args:
        file_content_as_list (list[str]): list of strings representing the file contents.

        Returns:
            list[NexusOver]: list of NexusTOver objects representing the TOVER table.
        """
        ignore_list = ['OVER', 'TX', 'TY', 'TZ', 'GRID', 'ROOT', 'TOVER',
                       'TX+', 'TX-', 'TZ+', 'TZ-', 'TY+', 'TY-',
                       'TXF+', 'TXF-', 'TYF+', 'TYF-', 'TZF+', 'TZF-', 'INCLUDE',
                       'ADD', 'SUB', 'DIV', 'EQ', 'MULT']
        valid_end_tokens = [x for x in VALID_NEXUS_KEYWORDS if x not in ignore_list]
        tovers_list: list[NexusTOver] = []
        reading_tover = False
        grid = 'ROOT'
        array = ''
        potential_operators: Final = ['ADD', 'SUB', 'DIV', 'MULT', 'EQ']
        i1, i2, j1, j2, k1, k2 = 0, 0, 0, 0, 0, 0
        operator = ''
        for i, line in enumerate(file_content_as_list):
            if nfo.check_token('TOVER', line.upper()):
                array = nfo.get_expected_token_value(token='TOVER', token_line=line,
                                                     file_list=file_content_as_list[i:])
                reading_tover = True

            if not reading_tover:
                continue
            if nfo.nexus_token_found(line, valid_end_tokens):
                # reset reading after another token found
                reading_tover = False
                grid = 'ROOT'
                array = ''
                operator = ''
                i1, i2, j1, j2, k1, k2 = 0, 0, 0, 0, 0, 0
                continue

            if any(nfo.check_token(x, line.upper()) for x in potential_operators):
                split_line = nfo.split_line(line)
                i1, i2, j1, j2, k1, k2 = (int(x) for x in split_line[0:6])
                operator = split_line[-1]
                continue
            if nfo.check_token('INCLUDE', line.upper()):
                include_file = nfo.get_expected_token_value(token='INCLUDE', token_line=line,
                                                            file_list=file_content_as_list[i:])
                new_tover = NexusTOver(i1=i1, i2=i2, j1=j1, j2=j2, k1=k1, k2=k2,
                                       include_file=include_file, array=array, grid=grid, operator=operator,
                                       value=0)
                tovers_list.append(new_tover)
                i1, i2, j1, j2, k1, k2 = 0, 0, 0, 0, 0, 0
                operator = ''

            elif i1 and i2 and j1 and j2 and k1 and k2 and operator and nfo.get_next_value(0, [line]):
                # not an include file, so it must be a value or array of values
                number_of_values = (i2 - i1 + 1) * (j2 - j1 + 1) * (k2 - k1 + 1)
                array_values = fo.get_multiple_expected_sequential_values(file_content_as_list[i:],
                                                                          number_tokens=number_of_values,
                                                                          ignore_values=[])
                new_tover = NexusTOver(i1=i1, i2=i2, j1=j1, j2=j2, k1=k1, k2=k2,
                                       include_file=None, array=array, grid=grid, operator=operator,
                                       value=0, array_values=[float(x) for x in array_values])
                i1, i2, j1, j2, k1, k2 = 0, 0, 0, 0, 0, 0
                operator = ''
                tovers_list.append(new_tover)

        return tovers_list

    @staticmethod
    def load_nexus_ftrans(file_content_as_list: list[str], unit_system: UnitSystem) -> list[NexusFtrans]:
        """Function to read in FTRANS tables from a file.

        Args:
            file_content_as_list (list[str]): list of strings representing the file contents.
            unit_system (UnitSystem): the unit system used in the grid file.

        Returns:
            list[NexusFtrans]: list of NexusFtrans objects representing the FTRANS table.
        """
        ignore_list = ['FTRANS', 'GRID', 'FNAME', 'ROOT']
        valid_end_tokens = [x for x in VALID_NEXUS_KEYWORDS if x not in ignore_list]
        ftrans_list: list[NexusFtrans] = []
        reading = False
        grid = 'ROOT'
        fname = None
        for line in file_content_as_list:
            if nfo.nexus_token_found(line, valid_end_tokens):
                reading = False
                grid = 'ROOT'
                fname = None
                continue

            if reading:
                split_line = nfo.split_line(line)
                if nfo.check_token('GRID', line):
                    grid = nfo.get_expected_token_value('GRID', line, file_content_as_list)
                if nfo.check_token('FNAME', line):
                    fname = nfo.get_expected_token_value('FNAME', line, file_content_as_list)
                if len(split_line) == 7:
                    i1, j1, k1, i2, j2, k2 = (int(x) for x in split_line[0:6])
                    value = float(split_line[-1])
                    # cut out the ranges
                    ftrans_list.append(NexusFtrans(grid=grid, fault_name=fname,
                                                   i1=i1, i2=i2, j1=j1, j2=j2, k1=k1, k2=k2,
                                                   value=value, unit_system=unit_system))

            if nfo.check_token('FTRANS', line):
                # reset the default values if another FTRANS call is found
                grid = 'ROOT'
                fname = None
                reading = True

        return ftrans_list

    @property
    def ftrans(self) -> list[NexusFtrans]:
        """Returns the OVER table as a list of NexusOver objects."""
        if not self._grid_properties_loaded:
            self.load_grid_properties_if_not_loaded()
        return self.__ftrans
