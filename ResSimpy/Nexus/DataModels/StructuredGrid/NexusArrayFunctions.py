from dataclasses import dataclass
import pandas as pd

from ResSimpy.Nexus.NexusSimulator import NexusSimulator
import ResSimpy.Nexus.array_function_operations as afo


@dataclass
class NexusArrayFunctions:
    """
           Class to hold the array functions created with FUNCTION keyword in Nexus Structured Grid file

           Attributes:
               functions_summary_df: pd.DataFrame

           """

    functions_summary_df: pd.DataFrame
    str_grid_file_path: str
    grid_file_as_list: list[str]
    model: NexusSimulator

    def load_functions_summary(self):
        self.grid_file_as_list = self.model.fcs_file.structured_grid_file.file_content_as_list
        self.functions_summary_df = afo.create_function_parameters_df(self.grid_file_as_list)
