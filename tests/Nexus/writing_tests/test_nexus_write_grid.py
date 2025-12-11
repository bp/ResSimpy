import pandas as pd
from ResSimpy.Enums.GridFunctionTypes import GridFunctionTypeEnum
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusFtrans import NexusFtrans
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGridArrayFunction import NexusGridArrayFunction


def test_write_simple_grid():
    # Arrange
    grid = NexusGrid(model_unit_system=UnitSystem.METRIC, assume_loaded=True)

    grid._range_x = 10
    grid._range_y = 20
    grid._range_z = 10

    grid.kx.name = 'KX'
    grid.kx.modifier = 'VALUE'
    grid.kx.value = '/some/path/to/file.dat'
    grid.kx.mods = {
        'MOD': pd.DataFrame(
            columns=['i1', 'i2', 'j1', 'j2', 'k1', 'k2', '#v'],
            data=[[1, 10, 1, 20, 1,  5, '=100'],
                  [1, 10, 1, 20, 6, 10, '=200']])
    }

    grid.ky.name = 'KY'
    grid.ky.modifier = 'CON'
    grid.ky.value = 150

    grid_faults_df = pd.DataFrame({'I1': [1, 6, 1, 1, 1, 6, 3, 3],
                       'I2': [5, 9, 1, 1, 5, 9, 3, 3],
                       'J1': [2, 2, 2, 6, 4, 4, 2, 6],
                       'J2': [2, 2, 5, 9, 4, 4, 5, 9],
                       'K1': [1, 1, 1, 1, 1, 1, 1, 1],
                       'K2': [10, 10, 10, 10, 10, 10, 10, 10],
                       'MULT': [0.0, 0.0, 0.0, 0.0, 0.02, 0.02, 0.02, 0.02],
                       'GRID': ['ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT', 'ROOT'],
                       'NAME': ['F1', 'F1', 'F1', 'F1', 'F2', 'F2', 'F2', 'F2'],
                       'FACE': ['I', 'I', 'J', 'J', 'I-', 'I-', 'J', 'J']}
                      )

    grid.__setattr__('_NexusGrid__faults_df', grid_faults_df)

    grid_array_funcs = [
        NexusGridArrayFunction(
            input_array=['KX'],
            output_array=['KZ'],
            function_type=GridFunctionTypeEnum.MULT,
            function_values = [0.1],
        ),
    ]

    grid.__setattr__('_NexusGrid__grid_array_functions', grid_array_funcs)
    
    grid_ftrans = [
        NexusFtrans(i1=1, i2=10, j1=1, j2=10, k1=1, k2=5, value=100.0, unit_system=UnitSystem.METRIC),
        NexusFtrans(i1=1, i2=10, j1=1, j2=10, k1=6, k2=10, value=200.0, unit_system=UnitSystem.METRIC, 
                    fault_name='FAULT1')
    ]
    grid.__setattr__('_NexusGrid__ftrans', grid_ftrans)
    
    expected_result = """NX NY NZ
10 20 10

KX VALUE
INCLUDE /some/path/to/file.dat
MOD
1 10 1 20 1  5 =100
1 10 1 20 6 10 =200

KY CON
150

FTRANS
1 1 1 10 10 5 100.0
FTRANS
FAULT FAULT1
1 1 6 10 10 10 200.0

MULT TX ALL PLUS MULT
FNAME F1
1 5 2 2 1 10 0.0
6 9 2 2 1 10 0.0

MULT TY ALL PLUS MULT
FNAME F1
1 1 2 5 1 10 0.0
1 1 6 9 1 10 0.0

MULT TX ALL MINUS MULT
FNAME F2
1 5 4 4 1 10 0.02
6 9 4 4 1 10 0.02

MULT TY ALL PLUS MULT
FNAME F2
3 3 2 5 1 10 0.02
3 3 6 9 1 10 0.02

FUNCTION
ANALYT MULT 0.1
KX OUTPUT KZ

"""

    # Act
    result = grid.to_string()

    # Assert
    assert result == expected_result
