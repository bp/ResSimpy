import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.StructuredGrid.NexusArrayFunctions import NexusArrayFunctions

# # TODO: Create test dataset using below info - used to create the functions above
# fcs_abs_path = 'C:/Users/dirii0/workspace/ResSimpy/ResSimpy/Nexus/resqml_to_nexus_deck/Oil_Template_Model/main_ID.fcs'
# model = NexusSimulator(origin=fcs_abs_path)
# my_str_grid_file_path = model.get_structured_grid_path()
# my_str_file_lines = nfo.load_file_as_list(my_str_grid_file_path,
#                                           strip_comments=True,
#                                           strip_str=True)


# test input for collect_all_function_blocks(my_str_file_lines):
# my_str_file_lines = ['', '', '', '', 'MAPBINARY', '', 'MAPVDB', '', 'MAPOUT ALL', '', '', '', '', '', 'NOLIST', '', '', '', 'ARRAYS ROOT', '', '', '', 'INCLUDE basic-grid.corp', '', '', '', 'LIST', '', '', '', '', '', '', '', '', '', 'KX CON', '', '350', '', '', 'KY MULT', '', '1.0  KX', '', '', 'KZ MULT', '', '0.1  KX', '', '', 'POROSITY CON', '', '0.2', '', '', 'NETGRS CON', '', '0.8', '', '', 'SWL CON', '', '0.26', '', '', 'SWR CON', '', '0.30', '', '', 'SWRO CON', '', '0.8', '', '', 'SWU CON', '', '1.0', '', '', 'IEQUIL CON', '', '1', '', '', '', '', '', 'WORKA3 CON', '', '0.3', '', '', '', 'FUNCTION', '', 'BLOCKS   1 30  1 30  1 1', '', 'ANALYT POLYN 1 0', '', 'blah', '', 'WORKA3 OUTPUT SW', '', '', '', 'FUNCTION IEQUIL', '', '1', '', 'RANGE OUTPUT 0.1 0.3', 'ANALYT POLYN 1 0', '', 'WORKA3 OUTPUT SWL', '', '', '', 'bugger line']
# my_func_list = collect_all_function_blocks(my_str_file_lines)


# test input for tabulate_all_model_function_parameters(function_list: list[list[str]])
# my_func_list = [['FUNCTION', 'ANALYT MULT', 'WORKA3 KX OUTPUT KX'], ['FUNCTION IREGION', '8', 'ANALYT POLYN a0 a1 a2', 'POROSITY OUTPUT POROSITY']]

