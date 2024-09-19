"""Class for handling the set of Local Grid Refinements (LGR) in the NexusGrid."""
from dataclasses import dataclass, field

from ResSimpy.LGRs import LGRs
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusLGR import NexusLGR
from ResSimpy.FileOperations import file_operations as fo


@dataclass
class NexusLGRs(LGRs):
    """Class for handling the set of Local Grid Refinements (LGR) in the NexusGrid."""

    _lgrs: list[NexusLGR] = field(default_factory=list)
    _grid_file_as_list: list[str] = field(default_factory=list)
    __has_been_loaded: bool = False

    def __init__(self, grid_file_as_list: None | list[str], lgrs: None | list[NexusLGR] = None,
                 assume_loaded: bool = False) -> None:
        """Initializes the NexusLGRs class."""
        super().__init__(lgrs=lgrs)
        self._grid_file_as_list = grid_file_as_list if grid_file_as_list is not None else []
        self.__has_been_loaded = assume_loaded

    def load_lgrs(self) -> None:
        """Loads LGRs from a list of strings."""
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
                self._lgrs.append(new_lgr)
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

    def __expand_refinement_lines(self, refinement_line: list[str]) -> list[int]:
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
    def lgrs(self) -> list[NexusLGR]:
        """Collection of the LGRs in the NexusGrid."""
        if not self.__has_been_loaded:
            self.load_lgrs()
        return self._lgrs
