from datetime import datetime
from pytest_mock import MockerFixture
import pandas as pd

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.Network.NexusStations import NexusStations
from ResSimpy.Nexus.DataModels.Network.NexusStation import NexusStation
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Nexus.nexus_collect_tables import collect_all_tables_to_objects
from ResSimpy.Nexus.nexus_load_list_table import load_list_from_table
from tests.utility_for_tests import get_fake_nexus_simulator


class TestNexusStations:
    start_date = "01/01/2023"
    file_contents = f"""
TIME {start_date}
STATION
    NAME        NUMBER  LEVEL   PARENT
    GRP1        1       2       NONE
    GRP2        2       2       NONE
    GRP1PRD     1       1       GRP1
    GRP1INJ     2       1       GRP1
    GRP2PRD     3       1       GRP2
    GRP2INJ     4       1       GRP2
ENDSTATION
"""

    def test_get_by_name(self, mocker):

        station_1 = NexusStation(
            name="GRP1",
            number=1,
            level=2,
            parent=None,
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_2 = NexusStation(
            name="GRP1PRD",
            number=1,
            level=1,
            parent="GRP1",
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_3 = NexusStation(
            name="GRP1INJ",
            number=2,
            level=1,
            parent="GRP1",
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_4 = NexusStation(
            name="GRP2",
            number=2,
            level=2,
            parent=None,
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_5 = NexusStation(
            name="GRP2PRD",
            number=3,
            level=1,
            parent="GRP2",
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_6 = NexusStation(
            name="GRP2INJ",
            number=4,
            level=1,
            parent="GRP2",
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )

        # get a mock network
        mock_nexus_network = mocker.MagicMock()
        nexus_stations = NexusStations(mock_nexus_network)
        nexus_stations._stations = [
            station_1,
            station_2,
            station_3,
            station_4,
            station_5,
            station_6,
        ]

        assert nexus_stations.get_by_name("GRP1") == station_1
        assert nexus_stations.get_by_name("GRP1PRD") == station_2
        assert nexus_stations.get_by_name("GRP1INJ") == station_3
        assert nexus_stations.get_by_name("GRP2") == station_4
        assert nexus_stations.get_by_name("GRP2PRD") == station_5
        assert nexus_stations.get_by_name("GRP2INJ") == station_6

    def test_stations_get_df(self, mocker: MockerFixture):

        date_2 = "01/01/2024"
        station_1 = NexusStation(
            name="GRP1",
            number=1,
            level=2,
            parent=None,
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_2 = NexusStation(
            name="GRP1PRD",
            number=1,
            level=1,
            parent="GRP1",
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_3 = NexusStation(
            name="GRP1INJ",
            number=2,
            level=1,
            parent="GRP1",
            start_date=self.start_date,
            date=self.start_date,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_4 = NexusStation(
            name="GRP2",
            number=2,
            level=2,
            parent=None,
            start_date=self.start_date,
            date=date_2,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_5 = NexusStation(
            name="GRP2PRD",
            number=3,
            level=1,
            parent="GRP2",
            start_date=self.start_date,
            date=date_2,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )
        station_6 = NexusStation(
            name="GRP2INJ",
            number=4,
            level=1,
            parent="GRP2",
            start_date=self.start_date,
            date=date_2,
            unit_system=UnitSystem.ENGLISH,
            date_format=DateFormat.MM_DD_YYYY,
        )

        # get a mock network
        mock_nexus_network = mocker.MagicMock()
        nexus_stations = NexusStations(mock_nexus_network)
        nexus_stations._stations = [
            station_1,
            station_2,
            station_3,
            station_4,
            station_5,
            station_6,
        ]

        expected_result = pd.DataFrame(
            {
                "name": [
                    "GRP1",
                    "GRP1PRD",
                    "GRP1INJ",
                    "GRP2",
                    "GRP2PRD",
                    "GRP2INJ",
                ],
                "number": [1, 1, 2, 2, 3, 4],
                "level": [2, 1, 1, 2, 1, 1],
                "parent": [None, "GRP1", "GRP1", None, "GRP2", "GRP2"],
                "date": [self.start_date] * 3 + [date_2] * 3,
                "iso_date": [datetime(2023, 1, 1, 0, 0, 0)] * 3 + [
                    datetime(2024, 1, 1, 0, 0, 0)
                ] * 3,
                "unit_system": ["ENGLISH"] * 6,
            }
        )
        # Act
        result = nexus_stations.get_df()

        # Assert
        pd.testing.assert_frame_equal(result, expected_result)