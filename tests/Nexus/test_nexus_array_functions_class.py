import pandas as pd

from ResSimpy.Enums.GridFunctionTypes import GridFunctionTypeEnum
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction
from ResSimpy.Nexus.array_function_operations import object_from_array_function_block
from tests.multifile_mocker import mock_multiple_files
from pandas.testing import assert_frame_equal


def test_structured_grid_file_loads_array_functions(mocker):
    # Arrange
    structured_grid_file_contents = """

ARRAYS ROOT

INCLUDE basic-grid.corp

LIST
KX CON
350

KY MULT
1.0  KX

WORKA3 CON
0.3

BLOCKS   1 30  1 30  1 1

ANALYT POLYN 1 0
some line
WORKA3 OUTPUT SW

1

RANGE OUTPUT 0.1 0.3
ANALYT POLYN 1 0

WORKA3 OUTPUT SWL

some line
Function IREGION ! test comment
8 9 10
! test comment
ANALYT     log
WORKA3    OUTPUT  KX
FUNCTION
ANALYT log10
WORKA3 OUTPUT KX
FUNCTION  IREGION
8 9 10

ANALYT polyn 1.4 1.3 1.2 1.1 1.0
POROSITY output POROSITY
FUNCTION
BLOCKs 1 30 1   30 1 5
ANALYT Abs
WORKA3 OUTPUT KX
FUNCTION
ANALYT EXP
KX OUTPUT KX
FUNCTION
ANALYT EXp10
 KX OUTPUT KX
 
FUNCTION

ANALYT sqrt

WORKA3 OUTPUT KX

FUNCTION
ANALYT GE 1000 500
KX OUTPUT KX
FUNCTION
ANALYT LE 500 1000
 KY OUTPUT KX
FUNCTION
ANALYT    add 
WORKA3 ky OUTPUT KX
FUNCTION
ANALYT subt
    KX KY OUTPUT Kz
FUNCTION
ANALYT DIV
 KX KY OUTPUT Kz
 
FUNCTION IREGION\n 8 9 10
 GRID ROOT
BLOCKS 1 20 1  40 1 10
RANGE  INPUT 1 2  a 2000
RANGE output 2000 3000
ANALYT    mult 
WORKA3 ky OUTPUT KX
FUNCTION
ANALYT min
KX KY OUTPUT KY
FUNCTION
ANALYT  max
 KX KY OUTPUT KX KY
some line


  
!WORKA7 CON
!1.0
!
!FUNCTION
!  ANALYT POLYN 2.0 
!  RANGE INPUT 4 5 6
!  WORKA6 OUTPUT WORKA7
!
!FUNCTION
!  ANALYT MULT
!  KXEFF FRAC WORKA7 OUTPUT KXEFF FRAC 

FUNCTION
ANALYT POLYN 2.0
RANGE INPUT 4 5 6
WORKA6 OUTPUT WORKA7
    """
    expected_functions = [['Function IREGION', '8 9 10', 'ANALYT     log', 'WORKA3    OUTPUT  KX'],
                          ['FUNCTION', 'ANALYT log10', 'WORKA3 OUTPUT KX'],
                          ['FUNCTION  IREGION', '8 9 10', 'ANALYT polyn 1.4 1.3 1.2 1.1 1.0',
                           'POROSITY output POROSITY'],
                          ['FUNCTION', 'BLOCKs 1 30 1   30 1 5', 'ANALYT Abs', 'WORKA3 OUTPUT KX'],
                          ['FUNCTION', 'ANALYT EXP', 'KX OUTPUT KX'],
                          ['FUNCTION', 'ANALYT EXp10', 'KX OUTPUT KX'],
                          ['FUNCTION', 'ANALYT sqrt', 'WORKA3 OUTPUT KX'],
                          ['FUNCTION', 'ANALYT GE 1000 500', 'KX OUTPUT KX'],
                          ['FUNCTION', 'ANALYT LE 500 1000', 'KY OUTPUT KX'],
                          ['FUNCTION', 'ANALYT    add', 'WORKA3 ky OUTPUT KX'],
                          ['FUNCTION', 'ANALYT subt', 'KX KY OUTPUT Kz'],
                          ['FUNCTION', 'ANALYT DIV', 'KX KY OUTPUT Kz'],
                          ['FUNCTION IREGION', '8 9 10', 'GRID ROOT', 'BLOCKS 1 20 1  40 1 10',
                           'RANGE  INPUT 1 2  a 2000', 'RANGE output 2000 3000', 'ANALYT    mult',
                           'WORKA3 ky OUTPUT KX'], ['FUNCTION', 'ANALYT min', 'KX KY OUTPUT KY'],
                          ['FUNCTION', 'ANALYT  max', 'KX KY OUTPUT KX KY'],
                          ['FUNCTION', 'ANALYT POLYN 2.0', 'RANGE INPUT 4 5 6', 'WORKA6 OUTPUT WORKA7']]

    data_dict = {'FUNCTION #': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], \
            'notation': ['KX = ln|WORKA3|', 'KX = log10|WORKA3|', 'POROSITY = 1.4*(POROSITY^4) +1.3*(POROSITY^3) +1.2*(POROSITY^2) +1.1*POROSITY +1.0',
            'KX = | WORKA3 |', 'KX = e^KX', 'KX = 10^KX', 'KX = SQRT|WORKA3|', 'KX = (KX if KX >= 1000.0; 500.0 otherwise)',
            'KX = (KY if KY <= 500.0; 1000.0 otherwise)', 'KX = WORKA3 + KY', 'KZ = KX - KY', 'KZ = (KX / KY if KY != 0; KX otherwise)',
            'KX = WORKA3 * KY', 'KY = min(KX, KY)', 'KX = max(KX, KY)', 'WORKA7 = 2.0'],
            'blocks [i1,i2,j1,j2,k1,k2]': ['', '', '', [1, 30, 1, 30, 1, 5], '', '', '', '', '', '', '', '', [1, 20, 1, 40, 1, 10], '', '', ''], \
            'region_type': ['IREGION', '', 'IREGION', '', '', '', '', '', '', '', '', '', 'IREGION', '', '', ''],
            'region_numbers':  [[8, 9, 10], '', [8, 9, 10], '', '', '', '', '', '', '', '', '', [8, 9, 10], '', '', ''],
            'func_type': ['LOG', 'LOG10', 'POLYN', 'ABS', 'EXP', 'EXP10', 'SQRT', 'GE', 'LE', 'ADD', 'SUBT', 'DIV', 'MULT', 'MIN', 'MAX', 'POLYN'],
            'func_coeff': ['', '', [1.4, 1.3, 1.2, 1.1, 1.0], '', '', '', '', [1000, 500], [500, 1000], '', '', '', '', '', '', [2.0]],
            'grid': ['', '', '', '', '', '', '', '', '', '', '', '', 'ROOT', '', '', ''],
            'range_input': ['', '', '', '', '', '', '', '', '', '', '', '', ['1', '2', 'A', '2000'], '', '', [4, 5, 6]],
            'range_output': ['', '', '', '', '', '', '', '', '', '', '', '', [2000, 3000], '', '', ''],
            'drange': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '',''],
            'input_arrays': [['WORKA3'], ['WORKA3'], ['POROSITY'], ['WORKA3'], ['KX'], ['KX'], ['WORKA3'], ['KX'], ['KY'],
                             ['WORKA3', 'KY'], ['KX', 'KY'], ['KX', 'KY'], ['WORKA3', 'KY'], ['KX', 'KY'], ['KX', 'KY'],
                             ['WORKA6']],
            'output_arrays': [['KX'], ['KX'], ['POROSITY'], ['KX'], ['KX'], ['KX'], ['KX'], ['KX'], ['KX'], ['KX'],
                              ['KZ'], ['KZ'], ['KX'], ['KY'], ['KX', 'KY'], ['WORKA7']],
            'i1': ['', '', '', '1', '', '', '', '', '', '', '', '', '1', '', '', ''], \
            'i2': ['', '', '', '30', '', '', '', '', '', '', '', '', '20', '', '', ''], \
            'j1': ['', '', '', '1', '', '', '', '', '', '', '', '', '1', '', '', ''], \
            'j2': ['', '', '', '30', '', '', '', '', '', '', '', '', '40', '', '', ''], \
            'k1': ['', '', '', '1', '', '', '', '', '', '', '', '', '1', '', '', ''], \
            'k2': ['', '', '', '5', '', '', '', '', '', '', '', '', '10', '', '', ''], \
            }

    expected_functions_df = pd.DataFrame(data_dict)
    expected_functions_df.set_index('FUNCTION #', inplace=True)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict=
                                     {'mock/str_grid/path.inc': structured_grid_file_contents}).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    test_input_grid_file_object: NexusFile = NexusFile.generate_file_include_structure('mock/str_grid/path.inc')
    new_sim_grid = NexusGrid.load_structured_grid_file(test_input_grid_file_object)
    func_list = new_sim_grid.get_array_functions_list()
    func_summary_df = new_sim_grid.get_array_functions_df()

    # Assert
    assert_frame_equal(expected_functions_df, func_summary_df)
    assert len(func_summary_df) == len(expected_functions)
    assert func_list == expected_functions


def test_odd_range_input_to_obj(recwarn):
    # Arrange
    functions_list = ['FUNCTION', 'ANALYT POLYN 2.0', 'RANGE INPUT 4 5 6', 'WORKA6 OUTPUT WORKA7']

    expected_object = NexusGridArrayFunction(
        function_type=GridFunctionTypeEnum.POLYN,
        function_values=[2.0],
        input_range=[(4, 5)],
        output_array=['WORKA7'],
        input_array=['WORKA6']
    )

    # Act
    func_obj = object_from_array_function_block(array_function=functions_list,
                                                function_number=1)
    # Assert
    assert func_obj == expected_object
    assert len(recwarn) == 1
    user_warning = recwarn.pop(UserWarning)
    assert str(user_warning.message) == """RANGE INPUT for function 1 has an odd number of entries.
Ignoring the last value: \"6\" from the range input.
In line: \"RANGE INPUT 4 5 6\""""
