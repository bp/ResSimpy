from dataclasses import dataclass
import pandas as pd
from ResSimpy.Grid import Grid, VariableEntry
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.structured_grid_operations import StructuredGridOperations
import ResSimpy.Nexus.array_function_operations as afo

@dataclass
class NexusArrayFunctions():
    """
    Class to hold the array functions created with FUNCTION keyword in Nexus Structured Grid file
    """
    functions_summary_df : pd.DataFrame

    def load_functions_summary(self, grid_file_as_list: list[str]):
        self.functions_summary_df = afo.create_function_parameters_df(grid_file_as_list)





