import pandas as pd
import pytest

from ResSimpy.DataModelBaseClasses.Multir import Multir
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusMultir import NexusMultir


@pytest.mark.parametrize("file_content, expected_result", [
    # Basic test
    ("""! comment
    
    MULTIR
    
    1	2	0.1	X Y Z	ALL
    1	3	0	Y Z
    1	4	0	XYZ	STD
    
    1	5	0.24	XYZ	NONSTD
    1	6	0	XYZ	ALL""",
     [NexusMultir(region_1=1, region_2=2, tmult=0.1, directions='XYZ', std_connections=True, non_std_connections=True),
      NexusMultir(region_1=1, region_2=3, tmult=0.0, directions='YZ', std_connections=True, non_std_connections=True),
      NexusMultir(region_1=1, region_2=4, tmult=0.0, directions='XYZ', std_connections=True, non_std_connections=False),
      NexusMultir(region_1=1, region_2=5, tmult=0.24, directions='XYZ', std_connections=False, non_std_connections=True),
      NexusMultir(region_1=1, region_2=6, tmult=0.0, directions='XYZ', std_connections=True, non_std_connections=True)]),
    # Empty MULTIR table
    ("""
    MULTIR
    """,
     []),

    # Test with a keyword after MULTIR
    ("""KX CON 
     5.1
     
     MULTIR
     2 2 3.1 X StD  ! comment after
     2 4 5 XYZ ALL
     KZ CON
     5.1
     """,
     [NexusMultir(region_1=2, region_2=2, tmult=3.1, directions='X', std_connections=True, non_std_connections=False),
      NexusMultir(region_1=2, region_2=4, tmult=5, directions='XYZ', std_connections=True, non_std_connections=True)]),
    # multiple MULTIR tables
    ("""MULTIR
    1 2 3 X StD
    1 4 5 XY Z ALL
    
    
    MULTIR
    2 2 3 X StD
    ! comment line
    2 4 5.5 XYZ ALL
    """,
     [NexusMultir(region_1=1, region_2=2, tmult=3, directions='X', std_connections=True, non_std_connections=False),
      NexusMultir(region_1=1, region_2=4, tmult=5, directions='XYZ', std_connections=True, non_std_connections=True),
      NexusMultir(region_1=2, region_2=2, tmult=3, directions='X', std_connections=True, non_std_connections=False),
      NexusMultir(region_1=2, region_2=4, tmult=5.5, directions='XYZ', std_connections=True, non_std_connections=True)])
]
    , ids=['basic', 'empty', 'stop_on_keyword', 'multiple_tables'])
def test_load_nexus_multir_table_from_list(file_content, expected_result):
    file_content_as_list = file_content.splitlines(keepends=True)

    # Act
    result = NexusGrid.load_nexus_multir_table_from_list(file_content_as_list)

    # Assert
    assert result == expected_result


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
    
    expected_result = [NexusMultir(region_1=1, region_2=2, tmult=0, directions='XYZ', std_connections=True, non_std_connections=True),
                       NexusMultir(region_1=1, region_2=3, tmult=0, directions='XYZ', std_connections=True, non_std_connections=True),
                       NexusMultir(region_1=1, region_2=4, tmult=0.1, directions='XYZ', std_connections=True, non_std_connections=True),
                       NexusMultir(region_1=1, region_2=5, tmult=0, directions='XYZ', std_connections=True, non_std_connections=True),
                       NexusMultir(region_1=1, region_2=6, tmult=0, directions='XYZ', std_connections=True, non_std_connections=True)]

    
    # Act
    result = grid.multir

    # Assert
    assert result == expected_result