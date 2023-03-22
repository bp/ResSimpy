from dataclasses import dataclass
import ResSimpy.Nexus.array_function_operations as afo
import pandas as pd


@dataclass
class NexusArrayFunctions:
    """
           Class to call the array functions created with FUNCTION keyword in Nexus Structured Grid file

           """

# Not sure if we really need a class to call these functions, but here you go...
    @staticmethod
    def load_functions_list(file_content_as_list: list[str]) -> list[str]:
        return afo.collect_all_function_blocks(file_content_as_list)

    @staticmethod
    def load_functions_df(file_content_as_list: list[str]) -> pd.DataFrame:
        return afo.summarize_model_functions(file_content_as_list)
