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
    """

    expected_result = [NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=0.0,
                                 arrays=['TX'], grid='ROOT'),
                       NexusOver(i1=1, i2=13, j1=1, j2=45, k1=11, k2=12, operator='+', value=1.5,
                                 arrays=['TX'], grid='ROOT'),
                       NexusOver(i1=1, i2=14, j1=1, j2=44, k1=12, k2=13, operator='-', value=1.5,
                                 arrays=['TX'], grid='ROOT'),
                       NexusOver(i1=1, i2=15, j1=1, j2=43, k1=13, k2=14, operator='/', value=2.0,
                                 arrays=['TX'], grid='ROOT'),
                       NexusOver(i1=1, i2=16, j1=1, j2=42, k1=14, k2=15, operator='=', value=2.0,
                                 arrays=['TX'], grid='ROOT')]

    # Act
    result = NexusGrid.read_nexus_overs(file_content.splitlines(keepends=True))

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
                                 arrays=['PVF'], grid='LGR_01')]

    # Act
    result = NexusGrid.read_nexus_overs(file_content.splitlines(keepends=True))

    # Assert
    assert result == expected_result


def test_read_nexus_over_faultnames():
    # Arrange
    file_content = """! comment
    OVER TXF TYF TZF
    FNAME fault_name_1
    1 12  1 46 10 11 +0.5
    2 13  2 45 11 12 -0.5
    
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
                                 arrays=['TXF', 'TYF', 'TZF'], fault_name='fault_name_1', grid='ROOT'),
                       NexusOver(i1=2, i2=13, j1=2, j2=45, k1=11, k2=12, operator='-', value=0.5,
                                 arrays=['TXF', 'TYF', 'TZF'], fault_name='fault_name_1', grid='ROOT'),
                       NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='*', value=1.1,
                                 arrays=['PVF'], fault_name='fault_name_2', grid='ROOT')]

    # Act
    result = NexusGrid.read_nexus_overs(file_content.splitlines(keepends=True))

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

    expected_result = [NexusOver(i1=1, i2=12, j1=1, j2=46, k1=10, k2=11, operator='GE', value=0.5,
                                 arrays=['TX'], threshold=2.5, grid='ROOT')
                       , NexusOver(i1=1, i2=14, j1=1, j2=44, k1=12, k2=13, operator='LE', value=0.5,
                                   arrays=['TY'], threshold=2.5, grid='ROOT')]

    # Act
    result = NexusGrid.read_nexus_overs(file_content.splitlines(keepends=True))

    # Assert
    assert result == expected_result
