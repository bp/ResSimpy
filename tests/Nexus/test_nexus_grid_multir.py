import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid


@pytest.mark.parametrize("file_content, expected_result", [
    # Basic test
    ("""! comment
    
    MULTIR
    
    1	2	0.1	XYZ	ALL
    1	3	0	XYZ	ALL
    1	4	0	XYZ	ALL
    
    1	5	0	XYZ	ALL
    1	6	0	XYZ	ALL""", pd.DataFrame({'REGION_1': [1, 1, 1, 1, 1],
                       'REGION_2': [2, 3, 4, 5, 6],
                       'TMULT': [0.1, 0, 0, 0, 0],
                       'DIRECTIONS': ['XYZ', 'XYZ', 'XYZ', 'XYZ', 'XYZ'],
                       'CONNECTIONS': ['ALL', 'ALL', 'ALL', 'ALL', 'ALL']})),
    # Empty MULTIR table
    ("""
    MULTIR
    """,
     pd.DataFrame(columns=['REGION_1', 'REGION_2', 'TMULT', 'DIRECTIONS', 'CONNECTIONS']).astype({'REGION_1': 'int',
                                                'REGION_2': 'int',
                                                'TMULT': 'float64'})),

    # Test with a keyword after MULTIR
    ("""KX CON 
     5.1
     
     MULTIR
     2 2 3.1 X StD
     2 4 5 XYZ ALL
     KZ CON
     5.1
     """,
     pd.DataFrame({'REGION_1': [2, 2],
                   'REGION_2': [2, 4],
                   'TMULT': [3.1, 5],
                   'DIRECTIONS': ['X', 'XYZ'],
                   'CONNECTIONS': ['StD', 'ALL']})),
    
    # multiple MULTIR tables
    ("""MULTIR
    1 2 3 X StD
    1 4 5 XYZ ALL
    
    
    MULTIR
    2 2 3 X StD
    2 4 5.5 XYZ ALL
    """,
     pd.DataFrame({'REGION_1': [1, 1, 2, 2],
                   'REGION_2': [2, 4, 2, 4],
                   'TMULT': [3, 5, 3, 5.5],
                   'DIRECTIONS': ['X', 'XYZ', 'X', 'XYZ'],
                   'CONNECTIONS': ['StD', 'ALL', 'StD', 'ALL']})),
]
    , ids=['basic', 'empty', 'stop_on_keyword', 'multiple_tables'])
def test_load_nexus_multir_table_from_list(file_content, expected_result):
    file_content_as_list = file_content.splitlines(keepends=True)

    # Act
    result = NexusGrid.load_nexus_multir_table_from_list(file_content_as_list)

    # Assert
    pd.testing.assert_frame_equal(result, expected_result)

def test_load_multir():
    # Arrange
    file_content = """! comment

    MULTIR

    1	2	0	XYZ	ALL
    1	3	0	XYZ	ALL
    1	4	0.1	XYZ	ALL
    1	5	0	XYZ	ALL
    1	6	0	XYZ	ALL
    """
    nexus_grid_file = NexusFile('loc.dat', file_content_as_list=file_content.splitlines(keepends=True))
    
    grid = NexusGrid(grid_nexus_file=nexus_grid_file)
    grid._nexus_file_content = file_content
    
    # Act
    result = grid.multir

    # Assert
    expected_result = pd.DataFrame({'REGION_1': [1, 1, 1, 1, 1],
                                    'REGION_2': [2, 3, 4, 5, 6],
                                    'TMULT': [0, 0, 0.1, 0, 0],
                                    'DIRECTIONS': ['XYZ', 'XYZ', 'XYZ', 'XYZ', 'XYZ'],
                                    'CONNECTIONS': ['ALL', 'ALL', 'ALL', 'ALL', 'ALL']})
    pd.testing.assert_frame_equal(result, expected_result)
