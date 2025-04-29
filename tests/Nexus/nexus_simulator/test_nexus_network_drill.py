import pytest

from ResSimpy.Nexus.DataModels.Network.NexusDrill import NexusDrill
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
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

    expected_drill_1 = NexusDrill(drillsite='site_1', name='well_1', date='25/07/2026', date_format=DateFormat.DD_MM_YYYY,
                                  drill_time=240, workover_time=30, completion_time=20, rigs='rig_1',
                                  start_date=start_date, replacement='well_2')
    expected_drill_2 = NexusDrill(drillsite='ALL', name='well_2', date='25/07/2026', date_format=DateFormat.DD_MM_YYYY,
                                  drill_time=120, workover_time=0, completion_time=0, rigs='rig_1',
                                  start_date=start_date, replacement=None)
    expected_result = [expected_drill_1, expected_drill_2]

    # Act
    # loaded_network_object = network_object.load()
    result = network_object.drills.get_all()

    # Assert
    assert result == expected_result
    assert result[0].total_drill_time == 260
    assert result[1].total_drill_time == 120