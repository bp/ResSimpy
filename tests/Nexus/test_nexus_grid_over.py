from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusOver import NexusOver


def test_read_nexus_over():
    # Arrange
    file_content = """! comment
    OVER TX
    1 12  1 46 10 11 *0.0		! North
    1 13  1 45 11 12  +1.5
    !south
    1 14  1 44 12 13  -1.5
    1 15  1 43 13 14  /2.0
    1 16  1 42 14 15  =2.0
    298 306 46 62 16 17 * 0.1
    2 3  4  5  6  7   0.5
    """

    expected_result = [NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=0.0,
                                 array='TX', grid='ROOT'),
                       NexusOver(i1=1, i2=13, j1=1, j2=45, k1=11, k2=12, operator='+', value=1.5,
                                 array='TX', grid='ROOT'),
                       NexusOver(i1=1, i2=14, j1=1, j2=44, k1=12, k2=13, operator='-', value=1.5,
                                 array='TX', grid='ROOT'),
                       NexusOver(i1=1, i2=15, j1=1, j2=43, k1=13, k2=14, operator='/', value=2.0,
                                 array='TX', grid='ROOT'),
                       NexusOver(i1=1, i2=16, j1=1, j2=42, k1=14, k2=15, operator='=', value=2.0,
                                 array='TX', grid='ROOT'),
                       NexusOver(i1=298, i2=306, j1=46, j2=62, k1=16, k2=17, operator='*', value=0.1,
                                 array='TX', grid='ROOT'),
                       NexusOver(i1=2, i2=3, j1=4, j2=5, k1=6, k2=7, operator='*', value=0.5,
                                 array='TX', grid='ROOT')]

    # Act
    result = NexusGrid.load_nexus_overs(file_content.splitlines(keepends=True))

    # Assert
    assert result == expected_result


def test_read_nexus_over_grids():
    # Arrange
    file_content = """! comment
    OVER PVF
    GRID LGR_01
    1 12  1 46 10 11 *0.0		! North 
    """

    expected_result = [NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=0.0,
                                 array='PVF', grid='LGR_01')]

    # Act
    result = NexusGrid.load_nexus_overs(file_content.splitlines(keepends=True))

    # Assert
    assert result == expected_result


def test_read_nexus_over_faultnames():
    # Arrange
    file_content = """! comment
    OVER TXF TYF TZF
    FNAME  fault_name_1
    1    12  1    46 10 11 +0.5 0.2 GE 1 *0.1
    2    13  2    45 11 12 -0.5 0.2 LE 1 *0.1
    
    POR CON
    1
    
    OVER PVF
    FNAME fault_name_2
    1 12  1 46 10 11 *1.1
    
    KX CON 
    300
    
    ! DON't read this line
    1 13 1 2 1 2 *1.2

    """

    expected_result = [NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='+', value=0.5,
                                 array='TXF', fault_name='fault_name_1', grid='ROOT'),
                       NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='GE', value=0.2,
                                 array='TYF', fault_name='fault_name_1', grid='ROOT', threshold=1),
                       NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=0.1,
                                 array='TZF', fault_name='fault_name_1', grid='ROOT'),
                       NexusOver(i1=2, i2=13, j1=2, j2=45, k1=11, k2=12, operator='-', value=0.5,
                                 array='TXF', fault_name='fault_name_1', grid='ROOT'),
                       NexusOver(i1=2, i2=13, j1=2, j2=45, k1=11, k2=12, operator='LE', value=0.2,
                                 array='TYF', fault_name='fault_name_1', grid='ROOT', threshold=1),
                       NexusOver(i1=2, i2=13, j1=2, j2=45, k1=11, k2=12, operator='*', value=0.1,
                                 array='TZF', fault_name='fault_name_1', grid='ROOT'),
                       NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=1.1,
                                 array='PVF', fault_name='fault_name_2', grid='ROOT')]

    # Act
    result = NexusGrid.load_nexus_overs(file_content.splitlines(keepends=True))

    # Assert
    assert result == expected_result


def test_read_nexus_over_with_GE():
    # Arrange
    file_content = """! comment
    OVER TX
    1 12  1 46 10 11  2.5 GE 0.5		! North 
    
    OVER TY
    1 14 1 44 12 13  2.5 LE 0.5		! South
    """

    expected_result = [NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='GE', value=2.5,
                                 array='TX', threshold=0.5, grid='ROOT'), 
                       NexusOver(i1=1, i2=14, j1=1, j2=44, k1=12, k2=13, operator='LE', value=2.5,
                                 array='TY', threshold=0.5, grid='ROOT')]

    # Act
    result = NexusGrid.load_nexus_overs(file_content.splitlines(keepends=True))

    # Assert
    assert result == expected_result


def test_read_nexus_over_from_grid():
    # Arrange
    grid_file_content = """
    NX NY NZ
    20 50 100
    ARRAYS
    KX CON
    1
    ! comment
    OVER TX
    1 12  1 46 10 11 *0.0		! North 
    """

    expected_result = [NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=0.0,
                                 array='TX', grid='ROOT')]
    grid = NexusGrid(grid_nexus_file=NexusFile(location='loc.dat',
                                               file_content_as_list=grid_file_content.splitlines(keepends=True)),
                     model_unit_system=UnitSystem.ENGLISH)
    # Act
    result = grid.overs

    # Assert
    assert result == expected_result


def test_over_multiple_values_arrays():
    # Arrange
    expected_result = [NexusOver(i1=227, i2=240, j1=91, j2=91, k1=29, k2=40, operator='*', value=0.0,
                                 array='TY', grid='ROOT'),
                       NexusOver(i1=227, i2=240, j1=91, j2=91, k1=29, k2=40, operator='*', value=0.0,
                                 array='TYF', grid='ROOT'),
                       NexusOver(i1=1, i2=1, j1=2, j2=2, k1=3, k2=3, operator='/', value=2.5,
                                 array='TY', grid='ROOT'),
                       NexusOver(i1=1, i2=1, j1=2, j2=2, k1=3, k2=3, operator='*', value=2.5,
                                 array='TYF', grid='ROOT'),
                       ]
    
    file_content = """OVER	TY TYF							
GRID	ROOT							
227 	240 	91 	91 	29 	40	*0.0	*0.0
1      1        2   2   3   3   / 2.5   *    2.5 ! COMMENT
"""
    # Act
    result = NexusGrid.load_nexus_overs(file_content.splitlines(keepends=True))

    # Assert
    assert result == expected_result


def test_over_to_string():
    # Arrange
    over = NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=0.0,
                     array='TX', grid='ROOT')
    expected_result = """OVER TX
1 12 1 46 10 11 *0.0
"""
    # Act
    result = over.to_string()
    # Assert
    assert result == expected_result
