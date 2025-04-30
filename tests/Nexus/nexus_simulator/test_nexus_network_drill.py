from pytest_mock import MockerFixture

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusDrill import NexusDrill
from ResSimpy.Nexus.DataModels.Network.NexusDrillSite import NexusDrillSite
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from tests.utility_for_tests import get_fake_nexus_simulator


def test_load_nexus_drill(mocker):
    # Arrange
    start_date = '15/01/2025'
    surface_file_contents = """
    TIME 25/07/2026
    DRILL
WELL    DRILLSITE   DRILLTIME   WORKTIME    CMPLTIME RIGS REPLACEMENT
well_1  site_1   240 30  20 rig_1    well_2
well_2  ALL   120 0  0 rig_1    NONE
ENDDRILL
    """
    surface_file = NexusFile(location='surface.dat',
                             file_content_as_list=surface_file_contents.splitlines(keepends=True))

    dummy_model = get_fake_nexus_simulator(mocker=mocker, mock_open=True)
    dummy_model.model_files.surface_files = {1: surface_file}
    dummy_model.start_date = start_date
    dummy_model.date_format = DateFormat.DD_MM_YYYY

    network_object = NexusNetwork(model=dummy_model)

    expected_drill_1 = NexusDrill(drillsite='site_1', name='well_1', date='25/07/2026',
                                  date_format=DateFormat.DD_MM_YYYY,
                                  drill_time=240, workover_time=30, completion_time=20, rigs='rig_1',
                                  start_date=start_date, replacement='well_2')
    expected_drill_2 = NexusDrill(drillsite='ALL', name='well_2', date='25/07/2026', date_format=DateFormat.DD_MM_YYYY,
                                  drill_time=120, workover_time=0, completion_time=0, rigs='rig_1',
                                  start_date=start_date, replacement=None)
    expected_result = [expected_drill_1, expected_drill_2]

    # Act
    result = network_object.drills.get_all()

    # Assert
    assert result == expected_result
    assert result[0].total_drill_time == 260
    assert result[1].total_drill_time == 120


def test_load_nexus_drill_site(mocker):
    # Arrange
    start_date = '15/01/2025'
    surface_file_contents = """
    TIME 25/07/2026
    DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE
    """

    surface_file = NexusFile(location='surface.dat',
                             file_content_as_list=surface_file_contents.splitlines(keepends=True))

    dummy_model = get_fake_nexus_simulator(mocker=mocker, mock_open=True)
    dummy_model.model_files.surface_files = {1: surface_file}
    dummy_model.start_date = start_date
    dummy_model.date_format = DateFormat.DD_MM_YYYY

    network_object = NexusNetwork(model=dummy_model)

    expected_drill_site_1 = NexusDrillSite(name='site_1', max_rigs=5, date='25/07/2026',
                                           date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_drill_site_2 = NexusDrillSite(name='site_2', max_rigs=1, date='25/07/2026',
                                           date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_result = [expected_drill_site_1, expected_drill_site_2]

    # Act
    result = network_object.drill_sites.get_all()

    # Assert
    assert result == expected_result


# Loading both at the same time, checking defaults match Nexus Defaults
def test_load_nexus_drill_and_drill_site(mocker):
    # Arrange
    start_date = '15/01/2025'
    surface_file_contents = """
    TIME 25/07/2026
    DRILLSITE
NAME
site_1
site_2
ENDDRILLSITE

    DRILL
WELL    DRILLSITE   DRILLTIME  
well_1  site_1   123 
well_2  ALL   1.5 
ENDDRILL
    """

    surface_file = NexusFile(location='surface.dat',
                             file_content_as_list=surface_file_contents.splitlines(keepends=True))

    dummy_model = get_fake_nexus_simulator(mocker=mocker, mock_open=True)
    dummy_model.model_files.surface_files = {1: surface_file}
    dummy_model.start_date = start_date
    dummy_model.date_format = DateFormat.DD_MM_YYYY

    network_object = NexusNetwork(model=dummy_model)

    expected_drill_site_1 = NexusDrillSite(name='site_1', max_rigs=1, date='25/07/2026',
                                           date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_drill_site_2 = NexusDrillSite(name='site_2', max_rigs=1, date='25/07/2026',
                                           date_format=DateFormat.DD_MM_YYYY, start_date=start_date)
    expected_drill_sites = [expected_drill_site_1, expected_drill_site_2]

    expected_drill_1 = NexusDrill(drillsite='site_1', name='well_1', date='25/07/2026',
                                  date_format=DateFormat.DD_MM_YYYY,
                                  drill_time=123, workover_time=0, completion_time=0, rigs='ALL',
                                  start_date=start_date, replacement=None)
    expected_drill_2 = NexusDrill(drillsite='ALL', name='well_2', date='25/07/2026', date_format=DateFormat.DD_MM_YYYY,
                                  drill_time=1.5, workover_time=0, completion_time=0, rigs='ALL',
                                  start_date=start_date, replacement=None)
    expected_drills = [expected_drill_1, expected_drill_2]

    # Act
    result_drill_sites = network_object.drill_sites.get_all()
    result_drills = network_object.drills.get_all()

    # Assert
    assert result_drill_sites == expected_drill_sites
    assert result_drills == expected_drills


def test_nexus_load_drill_table(mocker: MockerFixture):
    # Arrange
    mocker.patch(
        "ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4", return_value="uuid_1"
    )

    expected_drills = [
        NexusDrill(
            name="well_1",
            date="01/01/2020",
            date_format=DateFormat.DD_MM_YYYY,
            drillsite='site_1',
            drill_time=654.1,
            start_date='01/01/2019'
        )
    ]

    file_as_list = """TIME 01/01/2020
   DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL
    """.splitlines()

    nexus_file = NexusFile(location="", file_content_as_list=file_as_list)

    expected_object_locations = {'uuid_1': [3]}

    # Act
    nexus_obj_dict, _ = collect_all_tables_to_objects(
        nexus_file=nexus_file,
        table_object_map={
            "DRILL": NexusDrill,
        },
        start_date="01/01/2019",
        default_units=UnitSystem.ENGLISH,
        date_format=DateFormat.DD_MM_YYYY,
    )

    # Assert
    assert nexus_obj_dict["DRILL"] == expected_drills
    # Check that the line numbers are correct
    assert nexus_file.object_locations == expected_object_locations
