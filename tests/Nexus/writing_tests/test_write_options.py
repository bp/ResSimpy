import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.nexus_grid_to_proc import GridToProc


@pytest.mark.parametrize('test_grid_to_proc, expected_value', [
    (
            GridToProc(grid_to_proc_table=pd.DataFrame({
                'GRID': [1, 2, 3, 4],
                'PROCESS': [1, 2, 3, 4],
                'PORTYPE': ['MATRIX', 'MATRIX', 'FRACTURE', 'FRACTURE']
            }), auto_distribute=None),
            """GRIDTOPROC
 GRID  PROCESS PORTYPE 
1     1          MATRIX
2     2          MATRIX
3     3        FRACTURE
4     4        FRACTURE
ENDGRIDTOPROC
"""
    ),
    (
            GridToProc(grid_to_proc_table=None, auto_distribute='GRIDBLOCKS'),
            "GRIDTOPROC\nAUTO GRIDBLOCKS\nENDGRIDTOPROC\n"
    )
])
def test_grid_to_proc_to_string(test_grid_to_proc, expected_value):
    # Arrange

    # Act
    result = test_grid_to_proc.to_string()

    # Assert
    assert result == expected_value
