import pytest

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusFtrans import NexusFtrans
from ResSimpy.Nexus.DataModels.StructuredGrid.NexusGrid import NexusGrid


@pytest.mark.parametrize("file_content, expected_result", [
    # basic
    ("""! comment
    FTRANS
        1 12  1 46 10 11  0.595959
    1 13  1 45 11 12  2
    !south
    1 14  1 44 12 13   191891.23
    """,

     [NexusFtrans(i1=1, j1=12, k1=1, i2=46, j2=10, k2=11, value=0.595959, grid='ROOT', unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=1, j1=13, k1=1, i2=45, j2=11, k2=12, value=2.0, grid='ROOT', unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=1, j1=14, k1=1, i2=44, j2=12, k2=13, value=191891.23, grid='ROOT',
                  unit_system=UnitSystem.ENGLISH)]),
    # multiple tables
    ("""FTRANS
    1 12  1 46 10 11  0.595959
    1 13  1 45 11 12  2
    
    KX CON 5
    
    FTRANS
    1 14  1 44 12 13   191891.23
    
    KY CON 7
    
    FTRANS
    1 1 1 2 2 2 0.1
""",
     [NexusFtrans(i1=1, j1=12, k1=1, i2=46, j2=10, k2=11, value=0.595959, grid='ROOT', unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=1, j1=13, k1=1, i2=45, j2=11, k2=12, value=2.0, grid='ROOT', unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=1, j1=14, k1=1, i2=44, j2=12, k2=13, value=191891.23, grid='ROOT', unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=1, j1=1, k1=1, i2=2, j2=2, k2=2, value=0.1, grid='ROOT', unit_system=UnitSystem.ENGLISH)]
     ),

    # grid name and fault names
    (""" 
    FTRANS
    GRID LGR_01
    FNAME fault_1
    1 12  1 46 10 11  0.595959
    1 2 3 1 2 4   20.2
    
    FTRANS
    GRID LGR_02
    FNAME fault_2
    5 5 5 5 5 6 0.1
    
    FTRANS
    1 1 1 2 2 2 0.1
    """,
     [NexusFtrans(i1=1, j1=12, k1=1, i2=46, j2=10, k2=11, value=0.595959, grid='LGR_01', fault_name='fault_1',
                  unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=1, j1=2, k1=3, i2=1, j2=2, k2=4, value=20.2, grid='LGR_01', fault_name='fault_1',
                  unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=5, j1=5, k1=5, i2=5, j2=5, k2=6, value=0.1, grid='LGR_02', fault_name='fault_2',
                  unit_system=UnitSystem.ENGLISH),
      NexusFtrans(i1=1, j1=1, k1=1, i2=2, j2=2, k2=2, value=0.1, grid='ROOT', fault_name=None,
                  unit_system=UnitSystem.ENGLISH)]
     ),
], ids=['basic', 'multiple_tables', 'grid_and_fault_names'])
def test_read_nexus_ftrans(file_content, expected_result):
    # Arrange
    # Act
    result = NexusGrid.load_nexus_ftrans(file_content.splitlines(keepends=True), unit_system=UnitSystem.ENGLISH)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("units, expected_units", [
    ('ENGLISH', UnitSystem.ENGLISH),
    ('METRIC', UnitSystem.METRIC),
    ('METBAR', UnitSystem.METBAR)]
                         )
def test_read_nexus_ftrans_from_grid(units, expected_units):
    # Arrange
    grid_file_content = f"""
    {units}
    NX NY NZ
    20 50 100
    ARRAYS
    KX CON
    1
    ! comment
    ! comment
    FTRANS
        1 12  1 46 10 11  0.595959 ! comment
    1 13  1 45 11 12  2
    !south
    1 14  1 44 12 13   191891.23   ! comment
    !comment
    KY CON 
    21 

    FTRANS
    1 1 1 1 2 1 5.2

    """

    expected_ftrans = [NexusFtrans(i1=1, j1=12, k1=1, i2=46, j2=10, k2=11, value=0.595959, grid='ROOT',
                                   unit_system=expected_units),
                       NexusFtrans(i1=1, j1=13, k1=1, i2=45, j2=11, k2=12, value=2.0, grid='ROOT',
                                   unit_system=expected_units),
                       NexusFtrans(i1=1, j1=14, k1=1, i2=44, j2=12, k2=13, value=191891.23, grid='ROOT',
                                   unit_system=expected_units),
                       NexusFtrans(i1=1, j1=1, k1=1, i2=1, j2=2, k2=1, value=5.2, grid='ROOT',
                                   unit_system=expected_units)
                       ]

    grid = NexusGrid(grid_nexus_file=NexusFile(location='loc.dat',
                                               file_content_as_list=grid_file_content.splitlines(keepends=True)),
                     model_unit_system=UnitSystem.ENGLISH)
    # Act
    result = grid.ftrans

    # Assert
    assert result == expected_ftrans
