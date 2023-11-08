import warnings

import pytest
from pytest_mock import MockerFixture

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusRelPermEndPoint import NexusRelPermEndPoint
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.load_wells import load_wells
from tests.Nexus.nexus_simulator.test_nexus_simulator import mock_multiple_opens
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


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
                          ],
                         ids=["basic case", "swapped columns", "number name", "comments", "different cases", "WELLMOD"])
def test_load_basic_wellspec(mocker, file_contents, expected_name):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    expected_completion_1 = NexusCompletion(date=start_date, i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                            grid=None, date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_completion_2 = NexusCompletion(date=start_date, i=6, j=7, k=8, well_radius=9.11, date_format=date_format,
                                            unit_system=UnitSystem.ENGLISH)
    expected_well = NexusWell(well_name=expected_name, completions=[expected_completion_1, expected_completion_2],
                              unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')
    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

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

    expected_well_1_completion_1 = NexusCompletion(date=start_date, i=1, j=2, k=3, well_radius=4.5,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_2 = NexusCompletion(date=start_date, i=6, j=7, k=8, well_radius=9.11,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)

    expected_well_2_completion_1 = NexusCompletion(date=start_date, i=12, j=12, k=13, well_radius=4.50000000000,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_2_completion_2 = NexusCompletion(date=start_date, i=14, j=15, k=143243, well_radius=0.00002,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_2_completion_3 = NexusCompletion(date=start_date, i=18, j=155, k=143243, well_radius=40.00002,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)

    expected_well_3_completion_1 = NexusCompletion(date=start_date, i=126, j=504, k=3, skin=0, well_radius=0.354,
                                                   partial_perf=1, date_format=date_format,
                                                   unit_system=UnitSystem.ENGLISH)
    expected_well_3_completion_2 = NexusCompletion(date=start_date, i=126, j=504, k=4, skin=0, well_radius=0.354,
                                                   partial_perf=1, date_format=date_format,
                                                   unit_system=UnitSystem.ENGLISH)

    expected_well_4_completion_1 = NexusCompletion(date=start_date, i=1, j=2, k=3, well_radius=4.5,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_4_completion_2 = NexusCompletion(date=start_date, i=6, j=7, k=8, well_radius=9.11,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)

    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2],
                                unit_system=UnitSystem.ENGLISH)
    expected_well_2 = NexusWell(well_name='DEV2',
                                completions=[expected_well_2_completion_1, expected_well_2_completion_2,
                                             expected_well_2_completion_3], unit_system=UnitSystem.ENGLISH)
    expected_well_3 = NexusWell(well_name='WEL1234',
                                completions=[expected_well_3_completion_1, expected_well_3_completion_2],
                                unit_system=UnitSystem.ENGLISH)
    expected_well_4 = NexusWell(well_name='LINEAPPENDTOFIRSTLINE',
                                completions=[expected_well_4_completion_1, expected_well_4_completion_2],
                                unit_system=UnitSystem.ENGLISH)

    expected_wells = [expected_well_1, expected_well_2, expected_well_3, expected_well_4]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

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

    expected_well_1_completion_1 = NexusCompletion(date='01/08/2023', i=1, j=2, k=3, well_radius=4.5,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_2 = NexusCompletion(date='01/08/2023', i=6, j=7, k=8, well_radius=9.11,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_3 = NexusCompletion(date='15/10/2023', i=4, j=8, k=6, well_radius=23.0,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_4 = NexusCompletion(date='15/10/2023', i=5, j=9, k=56, well_radius=37.23,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_5 = NexusCompletion(date='15/12/2023', i=1, j=2, k=4, perm_thickness_ovr=1.423,
                                                   peaceman_well_block_radius=1.55, date_format=date_format,
                                                   unit_system=UnitSystem.ENGLISH)

    expected_well_2_completion_1 = NexusCompletion(date='01/08/2023', i=12, j=12, k=13, well_radius=4.50000000000,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_2_completion_2 = NexusCompletion(date='01/08/2023', i=14, j=15, k=143243, well_radius=0.00002,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_2_completion_3 = NexusCompletion(date='01/08/2023', i=18, j=155, k=143243, well_radius=40.00002,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_2_completion_4 = NexusCompletion(date='15/10/2023', i=15, j=28, k=684, well_radius=4.500000000001,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_2_completion_5 = NexusCompletion(date='15/10/2023', i=18, j=63, k=1234, well_radius=1.00002,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)

    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2,
                                             expected_well_1_completion_3, expected_well_1_completion_4,
                                             expected_well_1_completion_5],
                                unit_system=UnitSystem.ENGLISH)
    expected_well_2 = NexusWell(well_name='DEV2',
                                completions=[expected_well_2_completion_1, expected_well_2_completion_2,
                                             expected_well_2_completion_3, expected_well_2_completion_4,
                                             expected_well_2_completion_5], unit_system=UnitSystem.ENGLISH)

    expected_wells = [expected_well_1, expected_well_2]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

    # Assert
    assert result_wells == expected_wells


def test_load_wells_all_columns_present_structured_grid(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    file_contents = """
    TIME 01/03/2023 !658 days
    WELLSPEC WELL_3
    IW JW L RADW    MD      SKIN    DEPTH   X               Y   ANGLA  ANGLV  GRID       WI    DTOP    DBOT  KH  KHMULT RADB
    1  2  3  4.5    1.38974  8.9    7.56    89787.5478      1.24    0.98    3   GRID_A  2.84   TOP   BOT  1.23  0.363 1234
    6 7 8   9.11    1.568   4.52    8.955   9000.48974      2   1   5.68    GRID_B  0.2874   0.2132  5.45454 4.56      1.567 1.589
       """

    expected_well_completion_1 = NexusCompletion(date='01/03/2023', i=1, j=2, k=3, skin=8.9, depth=7.56,
                                                 well_radius=4.5, x=89787.5478, y=1.24, angle_a=0.98, angle_v=3,
                                                 grid='GRID_A', measured_depth=1.38974, well_indices=2.84,
                                                 depth_to_top=None, depth_to_top_str='TOP', depth_to_bottom_str='BOT',
                                                 depth_to_bottom=None, perm_thickness_ovr=1.23,
                                                 kh_mult=0.363, date_format=date_format, unit_system=UnitSystem.ENGLISH,
                                                 peaceman_well_block_radius=1234)
    expected_well_completion_2 = NexusCompletion(date='01/03/2023', i=6, j=7, k=8, skin=4.52, depth=8.955,
                                                 well_radius=9.11, x=9000.48974, y=2, angle_a=1, angle_v=5.68,
                                                 grid='GRID_B', measured_depth=1.568, well_indices=0.2874,
                                                 depth_to_top=0.2132, depth_to_bottom=5.45454, perm_thickness_ovr=4.56,
                                                 kh_mult=1.567, date_format=date_format, unit_system=UnitSystem.ENGLISH,
                                                 peaceman_well_block_radius=1.589)

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2],
                              unit_system=UnitSystem.ENGLISH)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

    # Assert
    assert result_wells == expected_wells

    # Check that each individual property of the completion is accessible and loaded correctly
    assert result_wells[0].completions[0].measured_depth == expected_wells[0].completions[0].measured_depth
    assert result_wells[0].completions[0].well_indices == expected_wells[0].completions[0].well_indices
    assert result_wells[0].completions[0].partial_perf == expected_wells[0].completions[0].partial_perf
    assert result_wells[0].completions[0].cell_number == expected_wells[0].completions[0].cell_number
    assert result_wells[0].completions[0].peaceman_well_block_radius == expected_wells[0].completions[0].peaceman_well_block_radius
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
    assert result_wells[0].completions[0].polymer_block_radius == expected_wells[0].completions[0].polymer_block_radius
    assert result_wells[0].completions[0].polymer_well_radius == expected_wells[0].completions[0].polymer_well_radius
    assert result_wells[0].completions[0].rel_perm_end_point == expected_wells[0].completions[0].rel_perm_end_point
    assert result_wells[0].completions[0].kh_mult == expected_wells[0].completions[0].kh_mult
    assert result_wells[0].completions[0].depth_to_top_str == expected_wells[0].completions[0].depth_to_top_str
    assert result_wells[0].completions[0].depth_to_bottom_str == expected_wells[0].completions[0].depth_to_bottom_str


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

    expected_well_completion_1 = NexusCompletion(date='01/03/2023', rel_perm_method=1, dfactor=0.005, status='OFF',
                                                 cell_number=1, perm_thickness_ovr=2000.3, peaceman_well_block_radius=2.2,
                                                 fracture_mult=0.5, sector=1, well_group='well_group', zone=1,
                                                 angle_open_flow=10.2, temperature=60.3, flowsector=2,
                                                 parent_node='NODe', mdcon=10.765, pressure_avg_pattern=7,
                                                 length=150.66, permeability=300.2, non_darcy_model='nondarcy',
                                                 comp_dz=0.5, layer_assignment=20, polymer_bore_radius=0.25,
                                                 polymer_well_radius=0.35, portype='FRACTURE', date_format=date_format,
                                                 unit_system=UnitSystem.ENGLISH)

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1],
                              unit_system=UnitSystem.ENGLISH)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

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
                                                         swro=0.01, sgro=1, sgrw=1, krw_swro=0.5, krw_swu=0.2,
                                                         krg_sgro=1, krg_sgu=0.2,
                                                         kro_swl=0.4, kro_swr=1, kro_sgl=1, kro_sgr=0.2, krw_sgl=0.3,
                                                         krw_sgr=0.1,
                                                         krg_sgrw=0.125, sgtr=0.134, sotr=0.7, )
    expected_rel_perm_end_point_2 = NexusRelPermEndPoint(swl=0.05, swr=0.15, swu=0.49, sgl=0.45, sgr=0.35, sgu=0.15,
                                                         swro=0, sgro=0.95, sgrw=0.95, krw_swro=0.45, krw_swu=0.15,
                                                         krg_sgro=0.95, krg_sgu=0.15,
                                                         kro_swl=0.35, kro_swr=0.95, kro_sgl=0.95, kro_sgr=0.15,
                                                         krw_sgl=0.25, krw_sgr=0.05,
                                                         krg_sgrw=0.075, sgtr=0.084, sotr=0.65, )

    expected_well_completion_1 = NexusCompletion(date=start_date, cell_number=1,
                                                 rel_perm_end_point=expected_rel_perm_end_point_1,
                                                 date_format=date_format, unit_system=UnitSystem.ENGLISH)

    expected_well_completion_2 = NexusCompletion(date=start_date, cell_number=2,
                                                 rel_perm_end_point=expected_rel_perm_end_point_2,
                                                 date_format=date_format, unit_system=UnitSystem.ENGLISH)

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2],
                              unit_system=UnitSystem.ENGLISH)

    expected_wells = [expected_well]

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2],
                              unit_system=UnitSystem.ENGLISH)
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

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

    expected_well_completion_1 = NexusCompletion(date='01/03/2023', i=1, j=2, k=3, skin=8.9, depth=7.56,
                                                 well_radius=4.5, x=None, y=1.24, angle_a=0.98, angle_v=3,
                                                 grid='GRID_A', measured_depth=1.38974, date_format=date_format,
                                                 unit_system=UnitSystem.ENGLISH)
    expected_well_completion_2 = NexusCompletion(date='01/03/2023', i=6, j=None, k=8, skin=4.52, depth=8.955,
                                                 well_radius=None, x=9000.48974, y=2, angle_a=1, angle_v=5.68,
                                                 grid='GRID_B', measured_depth=1.568, date_format=date_format,
                                                 unit_system=UnitSystem.ENGLISH)
    expected_well_completion_3 = NexusCompletion(date='01/03/2023', i=None, j=None, k=None, skin=None, depth=None,
                                                 well_radius=None, x=None, y=None, angle_a=None, angle_v=None,
                                                 grid='NA', measured_depth=None, date_format=date_format,
                                                 unit_system=UnitSystem.ENGLISH)

    expected_well = NexusWell(well_name='WELL_3', completions=[expected_well_completion_1, expected_well_completion_2,
                                                               expected_well_completion_3],
                              unit_system=UnitSystem.ENGLISH)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

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

    expected_completion_1 = NexusCompletion(date=start_date, i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                            grid=None, date_format=date_format, unit_system=expected_units)
    expected_completion_2 = NexusCompletion(date=start_date, i=6, j=7, k=8, well_radius=9.11, date_format=date_format,
                                            unit_system=expected_units)
    expected_well = NexusWell(well_name='DEV1', completions=[expected_completion_1, expected_completion_2],
                              unit_system=expected_units)
    expected_wells = [expected_well]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format)[0]

    # Assert
    assert result_wells == expected_wells


@pytest.mark.parametrize("first_line_wellspec, first_line_fcs_file, expected_format",
                         [("DATEFORMAT DD/MM/YYYY", "DATEFORMAT MM/DD/YYYY", DateFormat.DD_MM_YYYY),
                          ("DATEFORMAT MM/DD/YYYY", "DATEFORMAT DD/MM/YYYY", DateFormat.MM_DD_YYYY),
                          ("", "DATEFORMAT DD/MM/YYYY", DateFormat.DD_MM_YYYY),
                          ("", "", DateFormat.MM_DD_YYYY)],
                         ids=['Date format in wellspec file', 'American Date format in wellspec file',
                              'Date format in FCS file only', 'No date format specified'])
def test_load_full_model_with_wells(mocker: MockerFixture, first_line_wellspec,
                                    first_line_fcs_file, expected_format):
    # Arrange
    wellspec_contents = f"""
    {first_line_wellspec}
    TIME 01/08/2023 !232 days
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5"""

    fcs_file_contents = f"{first_line_fcs_file} \n WELLS Set 1 data/wells.dat\n"

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'model.fcs': fcs_file_contents,
            'data/wells.dat': wellspec_contents
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='model.fcs', mock_open=False)

    # Assert
    assert model.wells.date_format == expected_format
    assert model.wells.wells[0].completions[0].date_format == expected_format


def test_load_full_model_with_wells_no_date_format(mocker: MockerFixture):
    # Arrange
    wellspec_contents = f"""    
    TIME 01/08/2023 !232 days
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5
DATEFORMAT 
"""

    fcs_file_contents = f" WELLS Set 1 data/wells.dat\n"

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'model.fcs': fcs_file_contents,
            'data/wells.dat': wellspec_contents
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_error_str = "Cannot find the date format associated with the DATEFORMAT card in line='DATEFORMAT \\n' " \
                         "at line number 5"

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='model.fcs', mock_open=False)

    # Act
    with pytest.raises(ValueError) as ve:
        _ = model.wells.date_format

    # Assert
    result_error_msg = str(ve.value)
    assert result_error_msg == expected_error_str


def test_load_full_model_with_wells_invalid_date_format(mocker: MockerFixture):
    # Arrange
    wellspec_contents = f"""
    DATEFORMAT DD.MM.YYYY    
    TIME 01/08/2023 !232 days
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5
"""

    fcs_file_contents = f" WELLS Set 1 data/wells.dat\n"

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'model.fcs': fcs_file_contents,
            'data/wells.dat': wellspec_contents
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_error_str = "Invalid Date Format found: 'DD.MM.YYYY' at line 1"

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='model.fcs', mock_open=False)

    # Act
    with pytest.raises(ValueError) as ve:
        _ = model.wells.date_format

    # Assert
    result_error_msg = str(ve.value)
    assert result_error_msg == expected_error_str


def test_load_full_model_with_wells_multiple_wellspecs(mocker: MockerFixture):
    # Arrange
    wellspec_1_contents = f"""
DATEFORMAT     DD/MM/YYYY
    TIME 01/08/2023 !232 days
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5
"""

    wellspec_2_contents = f"""    
    DATEFORMAT     MM/DD/YYYY
        TIME 01/08/2023 !232 days
        WELLSPEC WELL2
        IW JW L RADW
        1  2  3  4.5
    """

    fcs_file_contents = """
    DATEFORMAT DD/MM/YYYY 
    WELLS Set 1 data/wells1.dat
     WELLS Set 2 data/wells2.dat"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'model.fcs': fcs_file_contents,
            'data/wells1.dat': wellspec_1_contents,
            'data/wells2.dat': wellspec_2_contents
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    expected_well_1_format = DateFormat.DD_MM_YYYY
    expected_well_2_format = DateFormat.MM_DD_YYYY

    warnings_mock = mocker.Mock()
    mocker.patch("warnings.warn", warnings_mock)

    expected_wells_overview = """
    Well Name: WELL1
    First Perforation: 01/08/2023
    Last Shut-in: N/A
    Dates Changed: 01/08/2023
    
    Well Name: WELL2
    First Perforation: 01/08/2023
    Last Shut-in: N/A
    Dates Changed: 01/08/2023
    """

    # Act
    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='model.fcs', mock_open=False)
    _ = model.wells.wells[0] # Used to stimulate loading as we are lazy loading this part

    # Assert
    warnings_mock.assert_called_once_with('Wells date format of MM/DD/YYYY inconsistent with base model format of DD/MM/YYYY')
    assert model.wells.wells[0].completions[0].date_format == expected_well_1_format
    assert model.wells.date_format == expected_well_2_format
    assert model.wells.wells[1].completions[0].date_format == expected_well_2_format
    assert model.wells.get_wells_overview() == expected_wells_overview