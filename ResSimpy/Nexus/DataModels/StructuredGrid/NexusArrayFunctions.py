from dataclasses import dataclass
import pandas as pd
import ResSimpy.Nexus.array_function_operations as afo


@dataclass
class NexusArrayFunctions:
    """
           Class to hold the array functions created with FUNCTION keyword in Nexus Structured Grid file

           Attributes:
               functions_summary_df: pd.DataFrame

           """

    @staticmethod
    def load_functions_summary(file_content_as_list: list[str]):
        return afo.summarize_model_functions(file_content_as_list)
