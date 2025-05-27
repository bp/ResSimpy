from pytest_mock import MockerFixture

from ResSimpy.Enums.FluidTypeEnums import PhaseType
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.Network.NexusDrill import NexusDrill
from ResSimpy.Nexus.DataModels.Network.NexusDrillSite import NexusDrillSite
from ResSimpy.Nexus.DataModels.Network.NexusDrillSites import NexusDrillSites
from ResSimpy.Nexus.DataModels.Network.NexusDrills import NexusDrills
from ResSimpy.Nexus.DataModels.Network.NexusGuideRate import NexusGuideRate
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from tests.utility_for_tests import get_fake_nexus_simulator


def test_load_nexus_guiderate(mocker):
    # Arrange
    start_date = '15/01/2025'
    surface_file_contents = """
TIME 25/07/2026
GUIDERATE
TARGET    DTMIN   PHASE   A B C D E F INCREASE DAMP
targ1     12      OIL     1 0 2.1 3 8 4 YES  1.15      
ENDGUIDERATE
    """
    surface_file = NexusFile(location='surface.dat',
                             file_content_as_list=surface_file_contents.splitlines(keepends=True))

    dummy_model = get_fake_nexus_simulator(mocker=mocker, mock_open=True)
    dummy_model.model_files.surface_files = {1: surface_file}
    dummy_model.start_date = start_date
    dummy_model.date_format = DateFormat.DD_MM_YYYY

    network_object = NexusNetwork(model=dummy_model)

    expected_guide_rate_1 = NexusGuideRate(date='25/07/2026', date_format=DateFormat.DD_MM_YYYY, name='targ1',
                                           time_interval=12, phase=PhaseType.OIL, a=1, b=0, c=2.1, d=3, e=8, f=4,
                                           increase_permitted=True, damping_factor=1.15, start_date='15/01/2025')

    expected_result = [expected_guide_rate_1]

    # Act
    result = network_object.guide_rates.get_all()

    # Assert
    assert result == expected_result


# Check defaults applied properly
