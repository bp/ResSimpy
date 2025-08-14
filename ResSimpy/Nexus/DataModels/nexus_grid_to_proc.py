from dataclasses import dataclass

import pandas as pd


@dataclass
class GridToProc:
    """Class for storing the GRIDTOPROC table information from the Options file."""
    grid_to_proc_table: None | pd.DataFrame = None
    auto_distribute: None | str = None

    @property
    def table_header(self) -> str:
        """Start of the GRIDTOPROC definition table."""
        return 'GRIDTOPROC'

    @property
    def table_footer(self) -> str:
        """End of the GRIDTOPROC definition table."""
        return 'END' + self.table_header

    def get_number_of_processors(self) -> int:
        """Returns the number of processors to use for the simulation.

        Returns:
        -------
            int: number of processors to use for the simulation
        """
        if self.grid_to_proc_table is None:
            return 0
        if 'PROCESS' in self.grid_to_proc_table.columns:
            return self.grid_to_proc_table['PROCESS'].max()
        else:
            return 0

    def to_string(self) -> str:
        """Returns the GRIDTOPROC table as a string."""
        if self.grid_to_proc_table is None and self.auto_distribute is None:
            return ''
        output_str = self.table_header + '\n'
        if self.auto_distribute is not None:
            output_str += f"AUTO {self.auto_distribute}\n"
        elif self.grid_to_proc_table is not None and not self.grid_to_proc_table.empty:
            output_str += self.grid_to_proc_table.to_string(index=False, header=True, justify='left') + '\n'
        output_str += self.table_footer + '\n'

        return output_str
