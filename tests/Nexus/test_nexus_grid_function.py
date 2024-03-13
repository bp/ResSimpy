from ResSimpy.Enums.GridFunctionTypes import GridFunctionTypeEnum
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction
from ResSimpy.Nexus.array_function_operations import object_from_array_function_block
import pytest
import pandas as pd


# class TestNexusGridFunction:
def test_load_nexus_grid_function():
    # Arrange
    input_file = '''FUNCTION IREGION
1 2 3
ANALYT POLYN 1.0 0.0
KX OUTPUT KY

FUNCTION
ANALYT POLYN 3.0 2 1.0 0
BLOCKS 1 5 1 7 1 9
KX OUTPUT KY KZ

FUNCTION
BLOCKS 1 5 1 7 1 9
ANALYT POLYN 3.0 2 1.0 0
KX OUTPUT KY KZ

FUNCTION ITRAN
1 3 5 7
GRID LGR1
RANGE INPUT -1e10 0 1e5 1e10
ANALYT POLYN 0
KX OUTPUT KX

FUNCTION
GRID ROOT
RANGE OUTPUT -1e12 0
ANALYT POLYN 0
KX OUTPUT KX
'''

    file = NexusFile(location='path/to/file.dat',
                     file_content_as_list=[str(line) for line in input_file.splitlines(keepends=True)])

    expected_result = [
     NexusGridArrayFunction(
        region_type='IREGION',
        region_number=[1, 2, 3],
        function_type=GridFunctionTypeEnum.POLYN,
        input_array=['KX'],
        output_array=['KY'],
        function_values=[1.0, 0.0]),
     NexusGridArrayFunction(
        blocks=[1, 5, 1, 7, 1, 9],
        function_type=GridFunctionTypeEnum.POLYN,
        input_array=['KX'],
        output_array=['KY', 'KZ'],
        function_values=[3.0, 2.0, 1.0, 0.0]),
     NexusGridArrayFunction(
        blocks=[1, 5, 1, 7, 1, 9],
        function_type=GridFunctionTypeEnum.POLYN,
        input_array=['KX'],
        output_array=['KY', 'KZ'],
        function_values=[3.0, 2.0, 1.0, 0.0]),
     NexusGridArrayFunction(
        region_type='ITRAN',
        region_number=[1, 3, 5, 7],
        grid_name='LGR1',
        function_type=GridFunctionTypeEnum.POLYN,
        input_range=[(-1.e10, 0.), (1.e5, 1.e10)],
        input_array=['KX'],
        output_array=['KX'],
        function_values=[0.0]),
     NexusGridArrayFunction(
        grid_name='ROOT',
        function_type=GridFunctionTypeEnum.POLYN,
        output_range=[(-1.e12, 0.)],
        input_array=['KX'],
        output_array=['KX'],
        function_values=[0.0])
    ]
    grid = NexusGrid(file)
    # Act
    result = grid.array_functions
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("function_number, function_list, expected_grid_array_function_obj",
                         [(1, ['FUNCTION IREGION', '1 3', 'ANALYT POLYN 0.0 1212.59288582951', 'KX OUTPUT KX'],
                           NexusGridArrayFunction(
                               region_type='IREGION',
                               region_number=[1, 3],
                               function_type=GridFunctionTypeEnum.POLYN,
                               input_array=['KX'],
                               output_array=['KX'],
                               function_values=[0.0, 1212.59288582951])
                           ),
                          (2, ['FUNCTION', 'ANALYT ADD', 'WORKA5 WORKA4 OUTPUT WORKA5'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.ADD,
                               input_array=['WORKA5', 'WORKA4'],
                               output_array=['WORKA5'])
                           ),
                          (3, ['FUNCTION ITRAN', '799', 'ANALYT GE 0.1 0.1', 'NETGRS OUTPUT NETGRS'],
                           NexusGridArrayFunction(
                               region_type='ITRAN',
                               region_number=[799],
                               function_type=GridFunctionTypeEnum.GE,
                               function_values=[0.1, 0.1],
                               input_array=['NETGRS'],
                               output_array=['NETGRS'])
                           ),
                          (4, ['FUNCTION', 'BLOCKS 156 163 139 154 31 37', 'ANALYT GE 0.385 0.385',
                               'NETGRS OUTPUT NETGRS'],
                           NexusGridArrayFunction(
                               blocks=[156, 163, 139, 154, 31, 37],
                               function_type=GridFunctionTypeEnum.GE,
                               function_values=[0.385, 0.385],
                               input_array=['NETGRS'],
                               output_array=['NETGRS'])
                           ),
                          (5, ['FUNCTION ITRAN', '817 819 839 879', 'ANALYT POLYN 0.', 'NETGRS OUTPUT NETGRS'],
                           NexusGridArrayFunction(
                               region_type='ITRAN',
                               region_number=[817, 819, 839, 879],
                               function_type=GridFunctionTypeEnum.POLYN,
                               function_values=[0.],
                               input_array=['NETGRS'],
                               output_array=['NETGRS'])
                           ),
                          (6, ['FUNCTION', 'ANALYT LOG10', 'POROSITY OUTPUT WORKA1'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.LOG10,
                               input_array=['POROSITY'],
                               output_array=['WORKA1'])
                           ),
                          (7, ['FUNCTION', 'ANALYT MULT', 'WORKA1 KX OUTPUT KX'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.MULT,
                               input_array=['WORKA1', 'KX'],
                               output_array=['KX'])
                           ),
                          (8, ['FUNCTION', 'ANALYT EXP10', 'KX OUTPUT KX'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.EXP10,
                               input_array=['KX'],
                               output_array=['KX'])
                           ),
                          (9, ['FUNCTION', 'RANGE OUTPUT 0 5000', 'ANALYT MULT', 'WORKA1 KX OUTPUT KX'],
                           NexusGridArrayFunction(
                               output_range=[(0., 5000.)],
                               function_type=GridFunctionTypeEnum.MULT,
                               input_array=['WORKA1', 'KX'],
                               output_array=['KX'])
                           ),
                          (10, ['FUNCTION', 'ANALYT POLYN 5. 4. 3. 2. 1. 0.', 'KX OUTPUT KY'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.POLYN,
                               function_values=[5., 4., 3., 2., 1., 0.],
                               input_array=['KX'],
                               output_array=['KY'])
                           ),
                          (11, ['FUNCTION IREGION', '8', 'ANALYT DIV', 'KZ PVMULT OUTPUT KZ'],
                           NexusGridArrayFunction(
                               region_type='IREGION',
                               region_number=[8],
                               function_type=GridFunctionTypeEnum.DIV,
                               input_array=['KZ', 'PVMULT'],
                               output_array=['KZ'])
                           ),
                          (12, ['FUNCTION', 'RANGE OUTPUT 0.00001 10000', 'ANALYT SUBT', 'WORKA1 MDEPTH OUTPUT WORKA1'],
                           NexusGridArrayFunction(
                               output_range=[(0.00001, 10000)],
                               function_type=GridFunctionTypeEnum.SUBT,
                               input_array=['WORKA1', 'MDEPTH'],
                               output_array=['WORKA1'])
                           ),
                          (13, ['FUNCTION', 'ANALYT LOG', 'SW OUTPUT SW'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.LOG,
                               input_array=['SW'],
                               output_array=['SW'])
                           ),
                          (14, ['FUNCTION', 'ANALYT POLYN 1.0  0.0', 'RANGE INPUT  0.0  0.5', 'SW OUTPUT SWL'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.POLYN,
                               function_values=[1., 0.],
                               input_range=[(0., 0.5)],
                               input_array=['SW'],
                               output_array=['SWL'])
                           ),
                          (15, ['FUNCTION ITRAN', '1 2 3', 'BLOCKS 216 270 140 176 67 68', 'ANALYT POLYN 0.56 0.0',
                                'KZ OUTPUT KZ'],
                           NexusGridArrayFunction(
                               region_type='ITRAN',
                               region_number=[1, 2, 3],
                               blocks=[216, 270, 140, 176, 67, 68],
                               function_type=GridFunctionTypeEnum.POLYN,
                               function_values=[0.56, 0.],
                               input_array=['KZ'],
                               output_array=['KZ'])
                           ),
                          (16, ['FUNCTION ITRAN', '1 2 3', 'BLOCKS 216 270 140 176 67 68', 'GRID ROOT',
                                'ANALYT POLYN 0.56 0.0', 'KZ OUTPUT KZ'],
                           NexusGridArrayFunction(
                               region_type='ITRAN',
                               region_number=[1, 2, 3],
                               grid_name='ROOT',
                               blocks=[216, 270, 140, 176, 67, 68],
                               function_type=GridFunctionTypeEnum.POLYN,
                               function_values=[0.56, 0.],
                               input_array=['KZ'],
                               output_array=['KZ'])
                           ),
                          (17, ['FUNCTION', 'GRID LGR1', 'ANALYT LE 5000 5000', 'KX OUTPUT KX'],
                           NexusGridArrayFunction(
                               grid_name='LGR1',
                               function_type=GridFunctionTypeEnum.LE,
                               function_values=[5000., 5000.],
                               input_array=['KX'],
                               output_array=['KX'])
                           ),
                          (18, ['FUNCTION', 'ANALYT MIN', 'KX KZ OUTPUT KZ'],
                           NexusGridArrayFunction(
                               function_type=GridFunctionTypeEnum.MIN,
                               input_array=['KX', 'KZ'],
                               output_array=['KZ'])
                           ),
                          (19, ['FUNCTION IREGION', '1 2 3 4 5', 'ANALYT MAX', 'KX KZ OUTPUT KX'],
                           NexusGridArrayFunction(
                               region_type='IREGION',
                               region_number=[1, 2, 3, 4, 5],
                               function_type=GridFunctionTypeEnum.MAX,
                               input_array=['KX', 'KZ'],
                               output_array=['KX'])
                           ),
                          ],
                         ids=['region_polyn', 'add', 'ge', 'blocks', 'multi_itran', 'log10', 'mult',
                              'exp10', 'range_output', 'basic_polyn', 'div', 'subt', 'log', 'range_input',
                              'itran_blocks', 'grid', 'le', 'min', 'max'])
def test_object_from_array_function_block(function_number, function_list, expected_grid_array_function_obj):
    # Arrange

    # Act
    result = object_from_array_function_block(function_list, function_number)

    # Assert
    assert result == expected_grid_array_function_obj


def test_tabular_array_function_block():

    # Arrange
    input_file = '''FUNCTION 1
WORKA5 OUTPUT WORKA1

! Section 1
1 10.  ! S1
2  9.
3  8.  ! S3

! Section 2
4  7.
5  6.
! Section 3
6  5.
7  4.

FUNCTION
ANALYT POLYN 3.0 2 1.0 0
BLOCKS 1 5 1 7 1 9
KX OUTPUT KY KZ

INCLUDE /random/path

IEQUIL CON 1
'''

    file = NexusFile(location='path/to/file.dat',
                     file_content_as_list=[str(line) for line in input_file.splitlines(keepends=True)])

    expected_result = [
     NexusGridArrayFunction(
        function_type=GridFunctionTypeEnum.FUNCTION_TABLE,
        input_array=['WORKA5'],
        output_array=['WORKA1'],
        function_table_m=1,
        function_table=pd.DataFrame({'WORKA5': [1, 2, 3, 4, 5, 6, 7],
                                     'WORKA1': [10., 9., 8., 7., 6., 5., 4.]})),
     NexusGridArrayFunction(
        blocks=[1, 5, 1, 7, 1, 9],
        function_type=GridFunctionTypeEnum.POLYN,
        input_array=['KX'],
        output_array=['KY', 'KZ'],
        function_values=[3.0, 2.0, 1.0, 0.0])
    ]
    grid = NexusGrid(file)

    # Act
    result = grid.array_functions

    # Assert
    for i in range(len(expected_result)):
        if result is not None and len(result) > 0 and result[i] is not None:
            result_dict = result[i].__dict__
        else:
            raise AssertionError('Result has the wrong format or is None.')
        expected_result_dict = expected_result[i].__dict__
        for key in expected_result_dict.keys():
            if isinstance(expected_result_dict[key], pd.DataFrame):
                pd.testing.assert_frame_equal(result_dict[key], expected_result_dict[key])
                print(key)
            else:
                assert result_dict[key] == expected_result_dict[key]
