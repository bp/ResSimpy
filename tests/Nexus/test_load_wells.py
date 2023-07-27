import pytest

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusRelPermEndPoint import NexusRelPermEndPoint
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.load_wells import load_wells


@pytest.mark.parametrize("file_contents, expected_name",
                         [("""
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5
C    2  2  2  2 (commented line using 'C')
    6 7 8   9.11
    """, "WELL1"),
                          ("""
    WELLspec ANOTHER_WELL
    JW IW L RADW
    2  1  3  4.5
    7 6 8   9.11
    """, "ANOTHER_WELL"),
                          ("""
    WELLSPEC "3"
    
    JW IW L RADW
    
    2  1  3  4.5
    7 6 8   9.11
    """, "3"),
                          ("""
    WELLSPEC "Well3"
    ! RADW
    JW IW L RADW !Another inline comment 
    2  1  3  4.5 !Inline Comment Here
    !Another Comment here
    7 6 8   9.11""", "Well3"),
                          ("""
    WELLSPEC well3
    ! RADW radw
    JW iw l radw
    2  1  3  4.5
    7 6 8   9.11
    """, "well3"),
    ("""
    WELLSPEC well3
    ! RADW radw
    JW iw l radw
    2  1  3  4.5
    7 6 8   9.11
    WELLMOD PD---_BB KHMULT CON 0.4""", "well3"),
    ], ids=["basic case", "swapped columns", "number name", "comments", "different cases", "WELLMOD"])
def test_load_basic_wellspec(mocker, file_contents, expected_name):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    expected_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date=start_date, grid=None, skin=None,
                                            angle_v=None, date_format=date_format)
    expected_completion_2 = NexusCompletion(i=6, j=7, k=8, well_radius=9.11, date=start_date, date_format=date_format)
    expected_well = NexusWell(well_name=expected_name, completions=[expected_completion_1, expected_completion_2],
                              units=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')
    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format)

    # Assert
    # Deep compare expected and received wells
    assert result_wells[0] == expected_well

    # Check that well radius is a useable float
    well_to_compare = result_wells[0]
    assert well_to_compare.completions[0].well_radius * 2 == 9.0
    assert well_to_compare.well_name == expected_name


def test_load_wells_multiple_wells(mocker):
    # Arrange
    start_date = '01/01/2023'

    date_format = DateFormat.DD_MM_YYYY

    file_contents = """
    WELLSPEC DEV1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    
    WELLSPEC DEV2
    IW JW L RADW
    12 12   13 4.50000000000
    14 15 143243            0.00002
    18 155 143243 40.00002
    
    WELLSPEC	WEL1234
	IW	JW	L	PPERF	RADW	SKIN
	126	504	3	1	0.354	0
	
	126	504	4	1	0.354	0
    
    WELLSPEC LINE>
APPENDTOFIRSTLINE
    IW JW L RADW
    1  2  3  >
    4.5
    6 7 8   9.11>
    !this is a comment
    
WELLMOD	RU001	DKH	CON	0
    """

    expected_well_1_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date=start_date, date_format=date_format)
    expected_well_1_completion_2 = NexusCompletion(i=6, j=7, k=8, well_radius=9.11, date=start_date, date_format=date_format)

    expected_well_2_completion_1 = NexusCompletion(i=12, j=12, k=13, well_radius=4.50000000000, date=start_date, date_format=date_format)
    expected_well_2_completion_2 = NexusCompletion(i=14, j=15, k=143243, well_radius=0.00002, date=start_date, date_format=date_format)
    expected_well_2_completion_3 = NexusCompletion(i=18, j=155, k=143243, well_radius=40.00002, date=start_date, date_format=date_format)

    expected_well_3_completion_1 = NexusCompletion(i=126, j=504, k=3, well_radius=0.354, skin=0, date=start_date,
                                                   partial_perf=1, date_format=date_format)
    expected_well_3_completion_2 = NexusCompletion(i=126, j=504, k=4, well_radius=0.354, skin=0, date=start_date,
                                                   partial_perf=1, date_format=date_format)

    expected_well_4_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date=start_date, date_format=date_format)
    expected_well_4_completion_2 = NexusCompletion(i=6, j=7, k=8, well_radius=9.11, date=start_date, date_format=date_format)
    
    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2],
                                units=UnitSystem.ENGLISH)
    expected_well_2 = NexusWell(well_name='DEV2',
                                completions=[expected_well_2_completion_1, expected_well_2_completion_2,
                                             expected_well_2_completion_3], units=UnitSystem.ENGLISH)
    expected_well_3 = NexusWell(well_name='WEL1234',
                                completions=[expected_well_3_completion_1, expected_well_3_completion_2],
                                units=UnitSystem.ENGLISH)
    expected_well_4 = NexusWell(well_name='LINEAPPENDTOFIRSTLINE',
                                completions=[expected_well_4_completion_1, expected_well_4_completion_2],
                                units=UnitSystem.ENGLISH)

    expected_wells = [expected_well_1, expected_well_2, expected_well_3, expected_well_4]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format) 

    # Assert
    assert result_wells == expected_wells


def test_load_wells_multiple_wells_multiple_dates(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    file_contents = """
    
    TIME 01/08/2023 !232 days
    WELLSPEC DEV1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11

    WELLSPEC DEV2
        IW JW L RADW
    12 12   13 4.50000000000
    14 15 143243            0.00002
    18 155 143243 40.00002
    
    TIME 15/10/2023
    WELLSPEC DEV1
    JW IW L RADW ! Switch column order
    8  4  6  23.0
    9 5 56   37.23

    WELLSPEC DEV2
        IW JW L RADW
    15 28   684 4.500000000001
    18 63 1234            1.00002
    
    TIME 15/12/2023
    WELLSPEC DEV1
    IW  JW L    RADB   KH! Columns not present above
    1   2  4    1.55   1.423 
    """

    expected_well_1_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/08/2023', date_format=date_format)
    expected_well_1_completion_2 = NexusCompletion(i=6, j=7, k=8, well_radius=9.11, date='01/08/2023', date_format=date_format)
    expected_well_1_completion_3 = NexusCompletion(j=8, i=4, k=6, well_radius=23.0, date='15/10/2023', date_format=date_format)
    expected_well_1_completion_4 = NexusCompletion(j=9, i=5, k=56, well_radius=37.23, date='15/10/2023', date_format=date_format)
    expected_well_1_completion_5 = NexusCompletion(j=2, i=1, k=4, bore_radius=1.55, perm_thickness_ovr=1.423, date='15/12/2023', date_format=date_format)

    expected_well_2_completion_1 = NexusCompletion(i=12, j=12, k=13, well_radius=4.50000000000, date='01/08/2023', date_format=date_format)
    expected_well_2_completion_2 = NexusCompletion(i=14, j=15, k=143243, well_radius=0.00002, date='01/08/2023', date_format=date_format)
    expected_well_2_completion_3 = NexusCompletion(i=18, j=155, k=143243, well_radius=40.00002, date='01/08/2023', date_format=date_format)
    expected_well_2_completion_4 = NexusCompletion(i=15, j=28, k=684, well_radius=4.500000000001, date='15/10/2023', date_format=date_format)
    expected_well_2_completion_5 = NexusCompletion(i=18, j=63, k=1234, well_radius=1.00002, date='15/10/2023', date_format=date_format)

    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2,
                                             expected_well_1_completion_3, expected_well_1_completion_4,
                                             expected_well_1_completion_5],
                                units=UnitSystem.ENGLISH)
    expected_well_2 = NexusWell(well_name='DEV2',
                                completions=[expected_well_2_completion_1, expected_well_2_completion_2,
                                             expected_well_2_completion_3, expected_well_2_completion_4,
                                             expected_well_2_completion_5], units=UnitSystem.ENGLISH)

    expected_wells = [expected_well_1, expected_well_2]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format)

    # Assert
    assert result_wells == expected_wells



def test_load_wells_all_columns_present_structured_grid(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    file_contents = """
    TIME 01/03/2023 !658 days
    WELLSPEC WELL_3
    IW JW L RADW    MD      SKIN    DEPTH   X               Y   ANGLA  ANGLV  GRID       WI    DTOP    DBOT  KH  KHMULT
    1  2  3  4.5    1.38974  8.9    7.56    89787.5478      1.24    0.98    3   GRID_A  2.84    8.95   7.1564 1.23  0.363
    6 7 8   9.11    1.568   4.52    8.955   9000.48974      2   1   5.68    GRID_B  0.2874   0.2132  5.45454 4.56      1.567
       """

    expected_well_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/03/2023',
                                                 measured_depth=1.38974, skin=8.9, depth=7.56, x=89787.5478, y=1.24,
                                                 angle_a=0.98, angle_v=3, grid='GRID_A', well_indices=2.84,
                                                 depth_to_top=8.95, depth_to_bottom=7.1564, perm_thickness_ovr=1.23,
                                                 kh_mult=0.363, date_format=date_format)
    expected_well_completion_2 = NexusCompletion(i=6, j=7, k=8, well_radius=9.11, date='01/03/2023',
                                                 measured_depth=1.568, skin=4.52, depth=8.955, x=9000.48974, y=2,
                                                 angle_a=1, angle_v=5.68, grid='GRID_B', well_indices=0.2874,
                                                 depth_to_top=0.2132, depth_to_bottom=5.45454, perm_thickness_ovr=4.56,
                                                 kh_mult=1.567, date_format=date_format)

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2],
                              units=UnitSystem.ENGLISH)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format)

    # Assert
    assert result_wells == expected_wells

    # Check that each individual property of the completion is accessible and loaded correctly
    assert result_wells[0].completions[0].measured_depth == expected_wells[0].completions[0].measured_depth
    assert result_wells[0].completions[0].well_indices == expected_wells[0].completions[0].well_indices
    assert result_wells[0].completions[0].partial_perf == expected_wells[0].completions[0].partial_perf
    assert result_wells[0].completions[0].cell_number == expected_wells[0].completions[0].cell_number
    assert result_wells[0].completions[0].bore_radius == expected_wells[0].completions[0].bore_radius
    assert result_wells[0].completions[0].portype == expected_wells[0].completions[0].portype
    assert result_wells[0].completions[0].fracture_mult == expected_wells[0].completions[0].fracture_mult
    assert result_wells[0].completions[0].sector == expected_wells[0].completions[0].sector
    assert result_wells[0].completions[0].well_group == expected_wells[0].completions[0].well_group
    assert result_wells[0].completions[0].zone == expected_wells[0].completions[0].zone
    assert result_wells[0].completions[0].angle_open_flow == expected_wells[0].completions[0].angle_open_flow
    assert result_wells[0].completions[0].temperature == expected_wells[0].completions[0].temperature
    assert result_wells[0].completions[0].flowsector == expected_wells[0].completions[0].flowsector
    assert result_wells[0].completions[0].parent_node == expected_wells[0].completions[0].parent_node
    assert result_wells[0].completions[0].mdcon == expected_wells[0].completions[0].mdcon
    assert result_wells[0].completions[0].pressure_avg_pattern == expected_wells[0].completions[0].pressure_avg_pattern
    assert result_wells[0].completions[0].length == expected_wells[0].completions[0].length
    assert result_wells[0].completions[0].permeability == expected_wells[0].completions[0].permeability
    assert result_wells[0].completions[0].non_darcy_model == expected_wells[0].completions[0].non_darcy_model
    assert result_wells[0].completions[0].comp_dz == expected_wells[0].completions[0].comp_dz
    assert result_wells[0].completions[0].layer_assignment == expected_wells[0].completions[0].layer_assignment
    assert result_wells[0].completions[0].polymer_bore_radius == expected_wells[0].completions[0].polymer_bore_radius
    assert result_wells[0].completions[0].polymer_well_radius == expected_wells[0].completions[0].polymer_well_radius
    assert result_wells[0].completions[0].rel_perm_end_point == expected_wells[0].completions[0].rel_perm_end_point
    assert result_wells[0].completions[0].kh_mult == expected_wells[0].completions[0].kh_mult






def test_load_wells_all_columns_unstructured_grid(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    # FM and PORTYPE can't appear in the same file in Nexus but we don't care, just store either
    file_contents = """
    TIME 01/03/2023 !658 days
    WELLSPEC WELL_3
    \n
    CELL  KH     RADB PORTYPE  FM    IRELPM  SECT   GROUP       ZONE   ANGLE   TEMP   FLOWSECT   PARENT   MDCON   IPTN   LENGTH   K         D       ND          DZ   LAYER   STAT   RADBP   RADWP 
    1     2000.3 2.2  FRACTURE 0.5   1       1      well_group  1      10.2    60.3   2          NODe     10.765  7      150.66   300.2     0.005   nondarcy    0.5  20      OFF    0.25    0.35
       """

    expected_well_completion_1 = NexusCompletion(
        date='01/03/2023', cell_number=1, perm_thickness_ovr=2000.3, bore_radius=2.2, portype='FRACTURE',
        fracture_mult=0.5, rel_perm_method=1, sector=1, well_group='well_group', zone=1, angle_open_flow=10.2,
        temperature=60.3, flowsector=2, parent_node='NODe', mdcon=10.765, pressure_avg_pattern=7,length=150.66,
        permeability=300.2, dfactor=0.005, non_darcy_model='nondarcy', comp_dz=0.5, layer_assignment=20, status='OFF',
        polymer_bore_radius=0.25, polymer_well_radius=0.35, date_format=date_format
    )

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1],
                              units=UnitSystem.ENGLISH)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format)

    # Assert
    assert result_wells == expected_wells


def test_load_wells_rel_perm_tables(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    file_contents = """WELLSPEC WELL_3

    CELL SWL   SWR    swu   SGL   SGR   SGU   SWRO    SGRO   SGRW   KRW_SWRO   KRW_SWU   KRG_SGRO   KRG_SGU   KRO_SWL   KRO_SWR   KRO_SGL   KRO_SGR   KRW_SGL   KRW_SGR   KRG_SGRW   SGTR    SOTR 
    1    0.1    0.2   0.54  .5    0.4   0.2   .01     1      1      0.5        0.2       1          0.2       0.4       1         1         0.2       0.3       0.1       0.125      0.134   0.7
    2    0.05	0.15  0.49	0.45  0.35	0.15  0		  0.95	 0.95	0.45	   0.15		 0.95		0.15	  0.35		0.95	  0.95		0.15	  0.25		0.05	  0.075		 0.084	 0.65

    """
    expected_rel_perm_end_point_1 = NexusRelPermEndPoint(swl=0.1, swr=0.2, swu=0.54, sgl=0.5, sgr=0.4, sgu=0.2,
                                                         swro=0.01, sgro=1, sgrw=1, krw_swro=0.5, krw_swu=0.2, krg_sgro=1, krg_sgu=0.2,
                                                         kro_swl=0.4, kro_swr=1, kro_sgl=1, kro_sgr=0.2, krw_sgl=0.3, krw_sgr=0.1,
                                                         krg_sgrw=0.125, sgtr=0.134, sotr=0.7, )
    expected_rel_perm_end_point_2 = NexusRelPermEndPoint(swl=0.05, swr=0.15, swu=0.49, sgl=0.45, sgr=0.35, sgu=0.15,
                                                         swro=0, sgro=0.95, sgrw=0.95, krw_swro=0.45, krw_swu=0.15, krg_sgro=0.95, krg_sgu=0.15,
                                                         kro_swl=0.35, kro_swr=0.95, kro_sgl=0.95, kro_sgr=0.15, krw_sgl=0.25, krw_sgr=0.05,
                                                         krg_sgrw=0.075, sgtr=0.084, sotr=0.65, )

    expected_well_completion_1 = NexusCompletion(date=start_date, cell_number=1, rel_perm_end_point=expected_rel_perm_end_point_1, date_format=date_format)

    expected_well_completion_2 = NexusCompletion(date=start_date, cell_number=2, rel_perm_end_point=expected_rel_perm_end_point_2, date_format=date_format)

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2],
                              units=UnitSystem.ENGLISH)

    expected_wells = [expected_well]

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2],
                              units=UnitSystem.ENGLISH)
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format)

    # Assert
    assert result_wells == expected_wells


def test_load_wells_na_values_converted_to_none(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    file_contents = """
    TIME 01/03/2023 !658 days
    WELLSPEC WELL_3
    IW JW L RADW    MD      SKIN    DEPTH   X               Y   ANGLA  ANGLV  GRID
    1  2  3  4.5    1.38974  8.9    7.56    NA      1.24    0.98    3   GRID_A
    6 NA 8   NA    1.568   4.52    8.955   9000.48974      2   1   5.68    GRID_B
        NA NA NA   NA    NA   NA    NA   NA      NA   NA   NA    NA
       """

    expected_well_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/03/2023',
                                                 measured_depth=1.38974, skin=8.9, depth=7.56, x=None, y=1.24,
                                                 angle_a=0.98, angle_v=3, grid='GRID_A', date_format=date_format)
    expected_well_completion_2 = NexusCompletion(i=6, j=None, k=8, well_radius=None, date='01/03/2023',
                                                 measured_depth=1.568, skin=4.52, depth=8.955, x=9000.48974, y=2,
                                                 angle_a=1, angle_v=5.68, grid='GRID_B', date_format=date_format)
    expected_well_completion_3 = NexusCompletion(i=None, j=None, k=None, well_radius=None, date='01/03/2023',
                                                 measured_depth=None, skin=None, depth=None, x=None, y=None,
                                                 angle_a=None, angle_v=None, grid='NA', date_format=date_format)

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2,
                                                               expected_well_completion_3], units=UnitSystem.ENGLISH)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format)

    # Assert
    assert result_wells == expected_wells


@pytest.mark.parametrize("file_contents, expected_units",
                         [
                             ("""       TIME 01/08/2023 !232 days
       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5
       6 7 8   9.11""", UnitSystem.ENGLISH),

                             ("""       
ENGLish

TIME 01/08/2023 !232 days
       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5
       6 7 8   9.11""", UnitSystem.ENGLISH),

                             (""" 
      TIME 01/08/2023 !232 days
      
      METRIC
      
       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5
       6 7 8   9.11""", UnitSystem.METRIC),

                             (""" 
      ! ENGLISH
      METKG/CM2
      
      TIME 01/08/2023 !232 days
       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5
       6 7 8   9.11""", UnitSystem.METKGCM2),

                             ("""
       METBAR
       TIME 01/08/2023 !232 days
       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5
       6 7 8   9.11""", UnitSystem.METBAR),
                             ("""
                    LAB
       TIME 01/08/2023 !232 days
       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5
       6 7 8   9.11""", UnitSystem.LAB),

                         ],
                         ids=['None specified', 'Oilfield', 'kpa', 'kgcm2 + comment before', 'metbar', 'lab'])
def test_correct_units_loaded(mocker, file_contents, expected_units):
    # Arrange
    start_date = '01/08/2023'
    date_format = DateFormat.DD_MM_YYYY

    expected_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date=start_date, grid=None, skin=None,
                                            angle_v=None, date_format=date_format)
    expected_completion_2 = NexusCompletion(i=6, j=7, k=8, well_radius=9.11, date=start_date, date_format=date_format)
    expected_well = NexusWell(well_name='DEV1', completions=[expected_completion_1, expected_completion_2],
                              units=expected_units)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH, date_format=date_format)

    # Assert
    assert result_wells == expected_wells
