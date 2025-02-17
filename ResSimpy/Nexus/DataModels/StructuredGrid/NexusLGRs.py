"""Class for handling the set of Local Grid Refinements (LGR) in the NexusGrid."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ResSimpy.GenericContainerClasses.LGRs import LGRs
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusLGR import NexusLGR
from ResSimpy.FileOperations import file_operations as fo

if TYPE_CHECKING:
    from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid


@dataclass(kw_only=True)
class NexusLGRs(LGRs):
    """Class for handling the set of Local Grid Refinements (LGR) in the NexusGrid."""

    _lgr_list: list[NexusLGR] = field(default_factory=list)
    _grid_file_as_list: list[str] = field(default_factory=list)
    __has_been_loaded: bool = False
    __parent_grid: NexusGrid

    def __init__(self, parent_grid: NexusGrid, grid_file_as_list: None | list[str],
                 lgr_list: None | list[NexusLGR] = None, assume_loaded: bool = False) -> None:
        """Initializes the NexusLGRs class.

        Args:
            parent_grid (NexusGrid): The NexusGrid object that the LGRs belong to.
            grid_file_as_list (None | list[str]): List of strings representing the file to load the LGRs from.
            lgr_list (None | list[NexusLGR]): List of LGRs to initialize the class with. Defaults to None for loading
            purposes.
            assume_loaded (bool): Whether the LGRs have already been loaded. Defaults to False.
        """
        super().__init__(lgr_list=lgr_list)
        self._grid_file_as_list = grid_file_as_list if grid_file_as_list is not None else []
        self.__has_been_loaded = assume_loaded
        self.__parent_grid = parent_grid

    def load_lgrs(self) -> None:
        """Loads LGRs from a list of strings."""
        if self.__has_been_loaded:
            return
        # Implementation to load LGRs from the provided list
        start_cartref_index = -1
        end_cartref_index = -1
        lgr_name = ''
        for line_num, line in enumerate(self._grid_file_as_list):
            if fo.check_token('CARTREF', line):
                lgr_name = fo.get_expected_token_value('CARTREF',
                                                       token_line=line,
                                                       file_list=self._grid_file_as_list,
                                                       )
                start_cartref_index = line_num

            if fo.check_token('ENDREF', line):
                end_cartref_index = line_num

            if 0 < start_cartref_index < end_cartref_index:
                new_lgr = self.__read_lgr_table(
                    file_subsection=self._grid_file_as_list[start_cartref_index + 1:end_cartref_index],
                    lgr_name=lgr_name)
                self._lgr_list.append(new_lgr)
                start_cartref_index = -1
                end_cartref_index = -1

        self.__has_been_loaded = True

    def __read_lgr_table(self, file_subsection: list[str], lgr_name: str) -> NexusLGR:
        """Reads in a single LGR table. Returns a NexusLGR object from the read."""
        range_of_lgr = []

        filter_list = file_subsection.copy()
        for x in range(6):
            range_values = fo.get_expected_next_value(0, filter_list, filter_list[0], replace_with='')
            range_of_lgr.append(range_values)
        i1, i2, j1, j2, k1, k2 = (int(x) for x in range_of_lgr)

        refinement_lines: list[list[str]] = []
        for line in filter_list:
            if len(refinement_lines) == 3:
                # we expect 3 lines worth of refinement one for each
                break
            next_value = fo.get_next_value(0, [line])
            if fo.get_next_value(0, [line]) is None:
                continue
            line_values = []
            filtered_line = [line]
            while next_value is not None:
                next_value = fo.get_next_value(0, filtered_line, replace_with='')
                if next_value is not None:
                    line_values.append(next_value)

            refinement_lines.append(line_values)

        nx_ny_nz = []
        for ref_line in refinement_lines:
            processed_line = self.__expand_refinement_lines(ref_line)
            nx_ny_nz.append(processed_line)
        nx, ny, nz = nx_ny_nz

        return NexusLGR(parent_grid='ROOT', name=lgr_name, i1=i1, i2=i2, j1=j1, j2=j2, k1=k1, k2=k2,
                        nx=nx, ny=ny, nz=nz)

    @staticmethod
    def __expand_refinement_lines(refinement_line: list[str]) -> list[int]:
        """Expands the refinement lines into a list of integers."""
        store_final_values: list[int] = []
        for value in refinement_line:
            if '*' in value:
                number_values, val = value.split('*', 1)
                value_expanded = int(number_values) * [int(val)]
                store_final_values.extend(value_expanded)
            else:
                store_final_values.append(int(value))
        return store_final_values

    @property
    def lgr_list(self) -> list[NexusLGR]:
        """Collection of the LGRs in the NexusGrid."""
        if not self.__has_been_loaded:
            self.load_lgrs()
            self.__parent_grid.load_grid_properties_if_not_loaded()
        return self._lgr_list

    def get_all(self) -> list[NexusLGR]:
        """Returns the collection of LGRs in the NexusGrid."""
        return self.lgr_list

    def get(self, name: str) -> NexusLGR:
        """Returns the LGR with the specified name.

        Args:
            name (str): the name of the LGR to get from the grid.
        """
        lgr = next((x for x in self.lgr_list if x.name == name), None)
        if lgr is None:
            raise ValueError(f'No LGR with name {name} found in the NexusGrid.')
        return lgr
