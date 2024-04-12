from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusWells import NexusWells
from ResSimpy.Nexus.load_wells import load_wells
from tests.utility_for_tests import get_fake_nexus_simulator


def test_load_wells_multiple_dates_formats_DD_MM_YYYY_h_m_s(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY_h_m_s
    mocker.patch('ResSimpy.DataObjectMixin.uuid4', return_value='uuid1')
    file_contents = """
    
    TIME 31/08/2023(19:13:01) !232 days
    WELLSPEC DEV1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    """

    expected_well_1_completion_1 = NexusCompletion(date='31/08/2023(19:13:01)', i=1, j=2, k=3, well_radius=4.5,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_2 = NexusCompletion(date='31/08/2023(19:13:01)', i=6, j=7, k=8, well_radius=9.11,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    

    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_wells = NexusWells(model=dummy_model)

    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2],
                                unit_system=UnitSystem.ENGLISH, parent_wells_instance=dummy_wells)
    
    expected_wells = [expected_well_1]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format, parent_wells_instance=dummy_wells)[0]

    # Assert
    assert result_wells == expected_wells
    
def test_load_wells_multiple_dates_formats_MM_DD_YYYY_h_m_s(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.MM_DD_YYYY_h_m_s

    file_contents = """
    
    TIME 10/24/2023(19:13:01) !232 days
    WELLSPEC DEV1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    """

    expected_well_1_completion_1 = NexusCompletion(date='10/24/2023(19:13:01)', i=1, j=2, k=3, well_radius=4.5,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_2 = NexusCompletion(date='10/24/2023(19:13:01)', i=6, j=7, k=8, well_radius=9.11,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    

    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_wells = NexusWells(model=dummy_model)

    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2],
                                unit_system=UnitSystem.ENGLISH, parent_wells_instance=dummy_wells)
    
    expected_wells = [expected_well_1]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format, parent_wells_instance=dummy_wells)[0]

    # Assert
    assert result_wells == expected_wells
    
def test_load_wells_multiple_dates_formats_DD_MM_YYYY_with_time_added(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.DD_MM_YYYY

    file_contents = """
    
    TIME 31/08/2023(19:13:01) !232 days
    WELLSPEC DEV1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    """

    expected_well_1_completion_1 = NexusCompletion(date='31/08/2023(19:13:01)', i=1, j=2, k=3, well_radius=4.5,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_2 = NexusCompletion(date='31/08/2023(19:13:01)', i=6, j=7, k=8, well_radius=9.11,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    

    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_wells = NexusWells(model=dummy_model)

    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2],
                                unit_system=UnitSystem.ENGLISH, parent_wells_instance=dummy_wells)
    
    expected_wells = [expected_well_1]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format, parent_wells_instance=dummy_wells)[0]

    # Assert
    assert result_wells == expected_wells
    
def test_load_wells_multiple_dates_formats_MM_DD_YYYY_with_time_added(mocker):
    # Arrange
    start_date = '01/01/2023'
    date_format = DateFormat.MM_DD_YYYY

    file_contents = """
    
    TIME 10/24/2023(19:13:01) !232 days
    WELLSPEC DEV1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    """

    expected_well_1_completion_1 = NexusCompletion(date='10/24/2023(19:13:01)', i=1, j=2, k=3, well_radius=4.5,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    expected_well_1_completion_2 = NexusCompletion(date='10/24/2023(19:13:01)', i=6, j=7, k=8, well_radius=9.11,
                                                   date_format=date_format, unit_system=UnitSystem.ENGLISH)
    

    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_wells = NexusWells(model=dummy_model)

    expected_well_1 = NexusWell(well_name='DEV1',
                                completions=[expected_well_1_completion_1, expected_well_1_completion_2],
                                unit_system=UnitSystem.ENGLISH, parent_wells_instance=dummy_wells)
    
    expected_wells = [expected_well_1]

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)
    wells_file = NexusFile.generate_file_include_structure('test/file/location.dat')

    # Act
    result_wells = load_wells(wells_file, start_date=start_date, default_units=UnitSystem.ENGLISH,
                              model_date_format=date_format, parent_wells_instance=dummy_wells)[0]

    # Assert
    assert result_wells == expected_wells