import os
import uuid
from unittest.mock import Mock
import pytest
from pytest_mock import MockerFixture
from ResSimpy.Enums.HowEnum import OperationEnum

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusWells import NexusWells
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


def check_file_read_write_is_correct(expected_file_contents: str, modifying_mock_open: Mock,
                                     mocker_fixture: MockerFixture, write_file_name: str):
    assert len(modifying_mock_open.call_args_list) == 1
    assert modifying_mock_open.call_args_list[0] == mocker_fixture.call(
        write_file_name, 'w')

    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [
        call for call in modifying_mock_open.mock_calls if 'call().write' in str(call)]
    assert len(list_of_writes) == 1
    assert list_of_writes[0].args[0] == expected_file_contents


@pytest.mark.parametrize('completions, expected_perforations', [
    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=4, well_radius=9.11, partial_perf=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=5, well_radius=9.11, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=6, well_radius=9.11, well_indices=0, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=7, well_radius=9.11, status='ON', partial_perf=0.000,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=8, well_radius=9.11, status='OFF', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=9, well_radius=9.11, well_indices=0, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2025', i=1, j=2, k=10, well_radius=9.11, well_indices=1, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=10, well_radius=9.11, well_indices=3,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=11, well_radius=9.11, perm_thickness_ovr=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/05/2028', i=1, j=2, k=11, well_radius=9.11, partial_perf=1, perm_thickness_ovr=1,
                      kh_mult=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/03/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5, length=100,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/05/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5, length=0,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=5, well_radius=9.11, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2025', i=1, j=2, k=10, well_radius=9.11, well_indices=1, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=10, well_radius=9.11, well_indices=3,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=11, well_radius=9.11, perm_thickness_ovr=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/05/2028', i=1, j=2, k=11, well_radius=9.11, partial_perf=1, perm_thickness_ovr=1,
                      kh_mult=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/03/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5, length=100,
                      date_format=DateFormat.DD_MM_YYYY)]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      well_indices=0, status='ON', partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=5, status='OFF', partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=5, partial_perf=0.5, perm_thickness_ovr=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=4, well_indices=5, partial_perf=0.5, perm_thickness_ovr=5,
                      length=0, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=5, partial_perf=0.5, kh_mult=0,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     []),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, date_format=DateFormat.DD_MM_YYYY)]),

    ([], [])

], ids=['basic case', 'mixture of perf and not perf', 'no perforations', 'using defaults', 'empty list'])
def test_get_perforations(completions, expected_perforations):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     unit_system=UnitSystem.ENGLISH)

    # Act
    result = well.perforations

    # Assert
    assert result == expected_perforations


@pytest.mark.parametrize('completions, expected_perforation', [
    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                     partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY)),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=4, well_radius=9.11, partial_perf=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=5, well_radius=9.11, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=6, well_radius=9.11, well_indices=0, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=7, well_radius=9.11, status='ON', partial_perf=0.000,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=8, well_radius=9.11, status='OFF', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=9, well_radius=9.11, well_indices=0, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2025', i=1, j=2, k=10, well_radius=9.11, well_indices=1, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=10, well_radius=9.11, well_indices=3,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                     partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY)),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      well_indices=0, status='ON', partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=5, status='OFF', partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     None),

    ([], None)

], ids=['basic case', 'mixture of perf and not perf', 'no perforations', 'empty list'])
def test_get_first_perforation(completions, expected_perforation):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     unit_system=UnitSystem.ENGLISH)

    # Act
    result = well.first_perforation

    # Assert
    assert result == expected_perforation


@pytest.mark.parametrize('completions, expected_shutins', [
    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_radius=9.11, status='OFF', partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_radius=9.11, status='OFF', partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=4, well_radius=9.11, partial_perf=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=5, well_radius=9.11, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=6, well_radius=9.11, well_indices=0, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=7, well_radius=9.11, status='ON', partial_perf=0.000,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=8, well_radius=9.11, status='OFF', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=9, well_radius=9.11, well_indices=0, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2025', i=1, j=2, k=10, well_radius=9.11, well_indices=1, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=10, well_radius=9.11, well_indices=3,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=11, well_radius=9.11, well_indices=3, partial_perf=1, length=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [NexusCompletion(date='01/02/2024', i=1, j=2, k=4, well_radius=9.11, partial_perf=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=6, well_radius=9.11, well_indices=0, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=7, well_radius=9.11, status='ON', partial_perf=0.000,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=8, well_radius=9.11, status='OFF', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=9, well_radius=9.11, well_indices=0, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=11, well_radius=9.11, well_indices=3, partial_perf=1, length=0,
                      date_format=DateFormat.DD_MM_YYYY)
      ]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      status='ON', partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=5, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     []),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     []),

    ([], [])

], ids=['basic case', 'mixture of perf and not perf', 'no shutins', 'no perf info', 'empty list'])
def test_get_shutins(completions, expected_shutins):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     unit_system=UnitSystem.ENGLISH)

    # Act
    result = well.shutins

    # Assert
    assert result == expected_shutins


@pytest.mark.parametrize('completions, expected_shutin', [
    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_radius=9.11, status='OFF', partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_radius=9.11, status='OFF', partial_perf=0.5,
                     date_format=DateFormat.DD_MM_YYYY)),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=4, well_radius=9.11, partial_perf=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=5, well_radius=9.11, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=6, well_radius=9.11, well_indices=0, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=7, well_radius=9.11, status='ON', partial_perf=0.000,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=8, well_radius=9.11, status='OFF', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=9, well_radius=9.11, well_indices=0, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2025', i=1, j=2, k=10, well_radius=9.11, well_indices=1, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=10, well_radius=9.11, well_indices=3,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     NexusCompletion(date='01/02/2024', i=1, j=2, k=9, well_radius=9.11, well_indices=0, status='ON', partial_perf=1,
                     date_format=DateFormat.DD_MM_YYYY)),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      well_indices=0, status='ON', partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=5, status='OFF', partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=5, status='OFF', partial_perf=0.5,
                     date_format=DateFormat.DD_MM_YYYY)),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=5, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     None),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     None),

    ([], None)

], ids=['basic case', 'mixture of perf and not perf', 'only shutins', 'no shutins', 'no perf info', 'empty list'])
def test_get_last_shutin(completions, expected_shutin):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     unit_system=UnitSystem.ENGLISH)

    # Act
    result = well.last_shutin

    # Assert
    assert result == expected_shutin


def test_printable_well_info():
    # Arrange
    completion_1 = NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                   grid='GRID1', status='ON', date_format=DateFormat.DD_MM_YYYY)
    completion_2 = NexusCompletion(date='01/01/2024', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                                   grid='GRID1', status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY)
    completion_3 = NexusCompletion(date='01/02/2025', i=1, j=2, k=3, partial_perf=0, date_format=DateFormat.DD_MM_YYYY)
    completions = [completion_1, completion_2, completion_3]

    well = NexusWell(well_name='test well', completions=completions, unit_system=UnitSystem.LAB)

    expected_info = \
        """
    Well Name: test well
    First Perforation: 01/01/2023
    Last Shut-in: 01/02/2025
    Dates Changed: 01/01/2023, 01/01/2024, 01/02/2025
    """

    # Act
    result = well.printable_well_info

    # Assert
    assert result == expected_info


def test_printable_well_info_missing_info():
    # Arrange
    completions = []

    well = NexusWell(well_name='test well', completions=completions, unit_system=UnitSystem.METRIC)

    expected_info = \
        """
    Well Name: test well
    First Perforation: N/A
    Last Shut-in: N/A
    Dates Changed: N/A
    """

    # Act
    result = well.printable_well_info

    # Assert
    assert result == expected_info


@pytest.mark.parametrize('completions, expected_shutin', [
    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      well_indices=3, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=3, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [('01/01/2023', 3), ('01/02/2024', 3)]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0.1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=4, well_radius=9.11, partial_perf=0,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=5, well_radius=9.11, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=6, well_radius=9.11, well_indices=0, status='ON',
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=7, well_radius=9.11, status='ON', partial_perf=0.000,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=8, well_radius=9.11, status='OFF', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2024', i=1, j=2, k=9, well_radius=9.11, well_indices=0, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2025', i=1, j=2, k=10, well_radius=9.11, well_indices=1, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2028', i=1, j=2, k=10, well_radius=9.11, well_indices=3,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2034', i=1, j=2, k=38, well_radius=9.11, partial_perf=0.5,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [('01/01/2023', 3), ('01/02/2024', 5), ('01/02/2025', 10), ('01/02/2028', 10), ('01/02/2034', 38)]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      partial_perf=0, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, well_indices=0, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     []),

    ([], []),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      well_indices=1, depth_to_top=1000, depth_to_bottom=1300, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=1, depth_to_top=1156, depth_to_bottom=1234, status='ON',
                      partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, depth_to_top=1156, depth_to_bottom=1234, status='OFF',
                      partial_perf=1, date_format=DateFormat.DD_MM_YYYY)],
     # Expected:
     [('01/01/2023', (1000, 1300)), ('01/02/2023', (1156, 1234))]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      well_indices=1, depth_to_top=1000, depth_to_bottom=1300, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=2, depth_to_top=1156, depth_to_bottom=1234, status='ON',
                      partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/03/2025', i=1, j=2, well_indices=3, depth_to_top=1156, depth_to_bottom=1234, status='ON',
                      partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
      ],
     # Expected:
     [('01/01/2023', (1000, 1300)),
      ('01/02/2023', (1156, 1234)),
      ('01/03/2025', (1156, 1234)), ]),

    ([NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                      well_indices=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234, status='ON',
                      partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                      date_format=DateFormat.DD_MM_YYYY),
      NexusCompletion(date='01/03/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234, status='ON',
                      partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
      ],
     # Expected:
     [('01/01/2023', 3),
      ('01/02/2023', 3),
      ('01/02/2023', 5)]),

], ids=['Only perforations', 'mixture of perf and not perf', 'no perforations', 'empty list', 'D Values',
        'Mix D values first', 'Mix K values first'])
def test_get_completion_events(completions, expected_shutin):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     unit_system=UnitSystem.METKGCM2)

    # Act
    result = well.completion_events

    # Assert
    assert result == expected_shutin


@pytest.mark.parametrize('existing_completions', [
    ([
        NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                        well_indices=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON',
                        partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/03/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON',
                        partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
    ]), ]
                         )
def test_find_completion(mocker, existing_completions):
    # Arrange
    completion_to_find = {'date': '01/02/2023', 'i': 1, 'j': 2, 'k': 3, }
    completion_to_fail = {'date': '01/02/2023'}
    expected_completions = [
        NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
    ]
    completion_to_find_as_completion = NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON',
                                                       date_format=DateFormat.DD_MM_YYYY)
    well = NexusWell(well_name='test well', completions=existing_completions, unit_system=UnitSystem.METKGCM2)
    expected_result = NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                                      date_format=DateFormat.DD_MM_YYYY)

    # Act
    result = well.find_completion(completion_to_find)
    result_with_completion = well.find_completion(completion_to_find_as_completion)
    result_find_completions = well.find_completions(completion_to_fail)

    # Assert
    assert result == expected_result
    assert result_with_completion == expected_result
    assert result_find_completions == expected_completions
    with pytest.raises(ValueError):
        well.find_completion(completion_to_fail)


def test_add_completion():
    # Arrange
    new_date = '01/04/2023'
    existing_completions = [
        NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                        well_indices=1, date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.METKGCM2),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.METKGCM2),
        NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY,
                        unit_system=UnitSystem.METKGCM2),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.METKGCM2),
        NexusCompletion(date='01/03/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY,
                        unit_system=UnitSystem.METKGCM2),
    ]
    new_completion_props = {'i': 3, 'j': 3, 'k': 5, 'well_radius': 1005.2, 'date_format': DateFormat.DD_MM_YYYY}

    new_nexus_completion = NexusCompletion(date=new_date, i=3, j=3, k=5, well_radius=1005.2,
                                           date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.METKGCM2)

    expected_completions = [x for x in existing_completions]
    expected_completions.append(new_nexus_completion)

    expected_well = NexusWell(well_name='test well', completions=expected_completions,
                              unit_system=UnitSystem.METKGCM2)
    well = NexusWell(well_name='test well', completions=existing_completions,
                     unit_system=UnitSystem.METKGCM2)
    # Act
    well._add_completion_to_memory(date=new_date, completion_properties=new_completion_props,
                                   date_format=DateFormat.DD_MM_YYYY)
    # Assert
    assert well == expected_well


def test_remove_completion_from_memory():
    # Arrange
    existing_completions = [
        NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                        well_indices=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/03/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
    ]
    expected_completions_after_removal = [
        NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                        well_indices=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/03/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
    ]
    expected_result = NexusWell(well_name='test well', completions=expected_completions_after_removal,
                                unit_system=UnitSystem.METKGCM2)
    perfs_to_remove = {'date': '01/02/2023', 'i': 1, 'j': 2, }
    remove_well = NexusWell(well_name='test well', completions=existing_completions,
                            unit_system=UnitSystem.METKGCM2)

    # Act
    comp_to_remove = remove_well.find_completions(perfs_to_remove)
    remove_well._remove_completions_from_memory(completions_to_remove=comp_to_remove)
    # Assert
    assert remove_well == expected_result


def test_modify_completion():
    # Arrange
    existing_completions = [
        NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                        well_indices=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/03/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
    ]

    changed_completion = NexusCompletion(date='01/03/2023', i=1, j=5, k=6, well_indices=0, depth_to_top=1156,
                                         depth_to_bottom=1234, status='ON', partial_perf=0.5,
                                         perm_thickness_ovr=10000.4, date_format=DateFormat.DD_MM_YYYY)
    expected_completions = existing_completions[:-1] + [changed_completion]
    completion_id = existing_completions[-1].id
    changes = {'i': 1, 'j': 5, 'k': 6, 'perm_thickness_ovr': 10000.4, 'partial_perf': 0.5}

    well = NexusWell(well_name='test well', completions=existing_completions, unit_system=UnitSystem.METKGCM2)
    expected_well = NexusWell(well_name='test well', completions=expected_completions, unit_system=UnitSystem.METKGCM2)

    # Act
    well._modify_completion_in_memory(new_completion_properties=changes, completion_to_modify=completion_id)

    # Assert
    assert well.completions[-1] == changed_completion
    # check the id is still the same:
    assert well.find_completion(
        NexusCompletion(date='01/03/2023', i=1, j=5, k=6, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=0.5, perm_thickness_ovr=10000.4,
                        date_format=DateFormat.DD_MM_YYYY)).id == completion_id


def test_well_dates(mocker):
    # Arrange
    well_1_completions = [
        NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                        well_indices=1, date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY), ]

    well_2_completions = [
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY),
        NexusCompletion(date='01/03/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY),
    ]
    mock_sim = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusSimulator.NexusSimulator', mock_sim)
    well = NexusWells(mock_sim)

    well.__setattr__('_wells',
                     [NexusWell(well_name='well1', completions=well_1_completions, unit_system=UnitSystem.METRIC),
                      NexusWell(well_name='well2', completions=well_2_completions, unit_system=UnitSystem.METRIC)])

    expected_result = {'01/01/2023', '01/02/2023', '01/03/2023'}
    # Act
    result = well.get_wells_dates()

    # Assert
    assert result == expected_result


def test_wells_modify(mocker):
    # Arrange

    fcs_file_data = '''RUN_UNITS ENGLISH
    DEFAULT_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY

    RECURRENT_FILES
    RUNCONTROL ref_runcontrol.dat
    WELLS Set 1 /my/wellspec/file.dat'''
    runcontrol_data = 'START 01/01/2020'
    wells_file = '''TIME 01/01/2020
    well
    TIME 01/01/2023
    wellspec well1
    iw jw l RADW GRID  skin ANGLV WI  
    1 2 3   4.5  GRID1 NA   NA    1 
    
    TIME 01/02/2023
    wellspec well1
    iw jw l  skin ANGLV WI  STAT PPERF DTOP  DBOT
    1 2 3    NA   NA    NA  ON     1     NA    NA
    1 2   NA    NA    0   NA    1      1156    1234
    
    wellsepc well2
    iw jw l STAT PPerf WI DTOP DBOT
    1 2 5   ON      1     3    NA NA
    1 2 NA  ON      1      0  1156 1234
    '''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'fcs_file.fcs': fcs_file_data,
            '/my/wellspec/file.dat': wells_file,
            'ref_runcontrol.dat': runcontrol_data,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    nexus_sim = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='fcs_file.fcs', mock_open=False)

    well_1_completions = [
        NexusCompletion(date='01/01/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None, grid='GRID1',
                        well_indices=1, date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH),
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH)]

    well_2_completions = [
        NexusCompletion(date='01/02/2023', i=1, j=2, k=5, well_indices=3, status='ON', partial_perf=1,
                        date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH),
        NexusCompletion(date='01/02/2023', i=1, j=2, well_indices=0, depth_to_top=1156, depth_to_bottom=1234,
                        status='ON', partial_perf=1, date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH)]

    wells = nexus_sim.wells

    date = '01/02/2023'
    perf_1_to_add = {'date': date, 'i': 3, 'j': 3, 'k': 5, 'well_radius': 1005.2, 'date_format': DateFormat.DD_MM_YYYY}
    perf_2_to_add = {'date': date, 'i': 1, 'j': 2, 'k': 6, 'permeability': 1005.2, 'date_format': DateFormat.DD_MM_YYYY}
    perf_to_remove = {'date': date, 'i': 1, 'j': 2, 'status': 'ON', 'partial_perf': 1, 'well_indices': 0,
                      'depth_to_top': 1156,
                      'depth_to_bottom': 1234}

    new_nexus_completion_1 = NexusCompletion(date=date, i=3, j=3, k=5, well_radius=1005.2,
                                             date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH)
    new_nexus_completion_2 = NexusCompletion(date=date, i=1, j=2, k=6, permeability=1005.2,
                                             date_format=DateFormat.DD_MM_YYYY, unit_system=UnitSystem.ENGLISH)
    expected_completions = well_1_completions[0:2] + [new_nexus_completion_1, new_nexus_completion_2]

    expected_result = [NexusWell(well_name='well1', completions=expected_completions, unit_system=UnitSystem.ENGLISH),
                       NexusWell(well_name='well2', completions=well_2_completions, unit_system=UnitSystem.ENGLISH)]

    # Act
    wells.modify(well_name='well1', completion_properties_list=[perf_1_to_add, perf_2_to_add],
                 how=OperationEnum.ADD)
    wells.modify(well_name='well1', completion_properties_list=[perf_to_remove], how=OperationEnum.REMOVE)
    # Assert
    assert wells.get_all()[0].completions == expected_result[0].completions


@pytest.mark.parametrize('file_as_list, add_perf_date, preserve_previous_completions, expected_result', [

    # Basic test
    (['WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5'], '01/01/2020', False,
     ['WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', '4 5 6 7.5 ! test user comments\n']),

    # Insert in middle of file
    (['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2',
      'iw  jw   l    RADB',
      '13  12   11   3.14', 'TIME 01/02/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5',
      'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2'],
     '01/02/2020', True,
     ['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2',
      'iw  jw   l    RADB',
      '13  12   11   3.14', 'TIME 01/02/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5',
      '4 5 6 7.5 ! test user comments\n', 'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2']
     ),

    # No time card for new comp
    (['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2',
      'iw  jw   l    RADB',
      '13  12   11   3.14', 'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5',
      'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2'],
     '01/02/2020', False,
     ['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2',
      'iw  jw   l    RADB',
      '13  12   11   3.14', ' ! test user comments\n', 'TIME 01/02/2020\n', 'WELLSPEC well1\n', 'IW JW L RADB\n',
      '4 5 6 7.5\n', '\n',
      'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2']
     ),

    # Preserve previous completions
    (['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2',
      'iw  jw   l    RADB',
      '13  12   11   3.14', 'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5',
      'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2'],
     '01/02/2020', True,
     ['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2',
      'iw  jw   l    RADB',
      '13  12   11   3.14', ' ! test user comments\n', 'TIME 01/02/2020\n', 'WELLSPEC well1\n', 'IW JW L RADB\n',
      '1 2 3 1.5\n', '4 5 6 7.5\n', '\n',
      'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2']
     ),

    # No previous well
    (['WELLSPEC well2', 'iw  jw   l    RADB', '13  12   11   3.14', 'TIME 01/04/2020', 'WELLSPEC well1',
      'iw  jw   l    RADB',
      '1  2   5   2.5', 'WELLSPEC well2', 'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020',
      'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
     '01/02/2020', True,
     ['WELLSPEC well2', 'iw  jw   l    RADB', '13  12   11   3.14', ' ! test user comments\n',
      'TIME 01/02/2020\n', 'WELLSPEC well1\n', 'IW JW L RADB\n', '4 5 6 7.5\n', '\n',
      'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2']
     ),

    # Not overlapping columns
    (['TIME 01/01/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH\n', '1  2   3   1.5\n', 'WELLSPEC well2\n',
      'iw  jw   l    RADB\n',
      '13  12   11   3.14\n', 'TIME 01/02/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH\n', '1  2   5   2.5\n',
      'WELLSPEC well2\n',
      'iw  jw   l    RADB\n', '12  11   10   3.14\n', 'TIME 01/03/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    RADB\n',
      '2 3   4   555.2\n'],
     '01/02/2020', True,
     ['TIME 01/01/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH\n', '1  2   3   1.5\n', 'WELLSPEC well2\n',
      'iw  jw   l    RADB\n',
      '13  12   11   3.14\n', 'TIME 01/02/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH RADB\n', '1  2   5   2.5 NA\n',
      '4 5 6 NA 7.5 ! test user comments\n', 'WELLSPEC well2\n',
      'iw  jw   l    RADB\n', '12  11   10   3.14\n', 'TIME 01/03/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    RADB\n',
      '2 3   4   555.2\n']
     ),

    # No overlap and multiple rows
    (['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
      'iw  jw    KH  PPERF  SKIN  STAT\n', '!Some comment line', '1  2   2.5   2   3.5  ON\n', '',
      '9  8   6.5   40   32.5  OFF\n',
      '11  12   4.5   43   394.5  OFF\n', '', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2'],
     '01/02/2020', True,
     ['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
      'iw  jw    KH  PPERF  SKIN  STAT L RADB\n', '!Some comment line', '1  2   2.5   2   3.5  ON NA NA\n', '',
      '9  8   6.5   40   32.5  OFF NA NA\n',
      '11  12   4.5   43   394.5  OFF NA NA\n', '4 5 NA NA NA NA 6 7.5 ! test user comments\n', '', 'TIME 01/03/2020',
      'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
     ),

    # Time card no comp
    (['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB KH', '1  2   3   1.5 5.5', 'TIME 01/02/2020',
      'WELLSPEC well2', 'iw  jw   l    RADB KH',
      '13  12   11   3.14 5.2', 'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5',
      'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2'],
     '01/02/2020', True,
     ['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB KH', '1  2   3   1.5 5.5', 'TIME 01/02/2020',
      'WELLSPEC well2', 'iw  jw   l    RADB KH',
      '13  12   11   3.14 5.2', ' ! test user comments\n', 'WELLSPEC well1\n', 'IW JW L RADB KH\n', '1 2 3 1.5 5.5\n',
      '4 5 6 7.5 NA\n', '\n',
      'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
      'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2']
     ),

    # Comment with not overlapping columns
    (['TIME 01/01/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH\n', '1  2   3   1.5\n', 'TIME 01/02/2020\n',
      'WELLSPEC well1\n',
      'iw  jw    KH  PPERF  SKIN  STAT\n', '!Some comment line\n', '1  2   2.5   2   3.5  ON !COMMMENT\n', '',
      '9  8   6.5   40   32.5  OFF\n',
      '11  12   4.5   43   394.5  OFF\n', '', 'TIME 01/03/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    RADB\n',
      '2 3   4   555.2\n'],
     '01/02/2020', True,
     ['TIME 01/01/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH\n', '1  2   3   1.5\n', 'TIME 01/02/2020\n',
      'WELLSPEC well1\n',
      'iw  jw    KH  PPERF  SKIN  STAT L RADB\n', '!Some comment line\n', '1  2   2.5   2   3.5  ON NA NA !COMMMENT\n',
      '', '9  8   6.5   40   32.5  OFF NA NA\n',
      '11  12   4.5   43   394.5  OFF NA NA\n', '4 5 NA NA NA NA 6 7.5 ! test user comments\n', '', 'TIME 01/03/2020\n',
      'WELLSPEC well1\n', 'iw  jw   l    RADB\n', '2 3   4   555.2\n'],
     ),

    # Comment inline with headers
    (['TIME 01/01/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH\n', '1  2   3   1.5\n', 'TIME 01/02/2020\n',
      'WELLSPEC well1\n',
      'iw  jw    KH  PPERF  SKIN  STAT !COmment!\n', '!Some comment line\n', '1  2   2.5   2   3.5  ON !COMMMENT\n', '',
      '9  8   6.5   40   32.5  OFF\n',
      '11  12   4.5   43   394.5  OFF\n', '', 'TIME 01/03/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    RADB\n',
      '2 3   4   555.2\n'],
     '01/02/2020', True,
     ['TIME 01/01/2020\n', 'WELLSPEC well1\n', 'iw  jw   l    KH\n', '1  2   3   1.5\n', 'TIME 01/02/2020\n',
      'WELLSPEC well1\n',
      'iw  jw    KH  PPERF  SKIN  STAT L RADB !COmment!\n', '!Some comment line\n',
      '1  2   2.5   2   3.5  ON NA NA !COMMMENT\n', '', '9  8   6.5   40   32.5  OFF NA NA\n',
      '11  12   4.5   43   394.5  OFF NA NA\n', '4 5 NA NA NA NA 6 7.5 ! test user comments\n', '', 'TIME 01/03/2020\n',
      'WELLSPEC well1\n', 'iw  jw   l    RADB\n', '2 3   4   555.2\n'],
     ),

    # Date after end of file
    (['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
      'iw  jw    KH  PPERF  SKIN  STAT !COmment!', '!Some comment line', '1  2   2.5   2   3.5  ON !COMMMENT', '',
      '9  8   6.5   40   32.5  OFF',
      '11  12   4.5   43   394.5  OFF', '', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2'],
     '01/06/2020', True,
     ['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
      'iw  jw    KH  PPERF  SKIN  STAT !COmment!', '!Some comment line', '1  2   2.5   2   3.5  ON !COMMMENT', '',
      '9  8   6.5   40   32.5  OFF',
      '11  12   4.5   43   394.5  OFF', '', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
      '2 3   4   555.2',
      ' ! test user comments\n', 'TIME 01/06/2020\n', 'WELLSPEC well1\n', 'IW JW L RADB\n', '2 3 4 555.2\n',
      '4 5 6 7.5\n', '\n'],
     ),
], ids=['basic_test', 'insert in middle of file', 'No time card for new comp', 'preserve previous completions',
        'No previous well',
        'Not overlapping columns', 'no overlap and multiple rows', 'Time card no comp',
        'comment with not overlapping columns',
        'comment inline with headers', 'date_after_end_of_file'])
def test_add_completion_write(mocker, file_as_list, add_perf_date,
                              preserve_previous_completions, expected_result):
    ''' TODO insert into include files
     TODO write multiple completions in a row
    '''
    start_date = '01/01/2020'
    # Arrange
    file = NexusFile(location='wells.dat', file_content_as_list=file_as_list, )

    fake_nexus_sim = get_fake_nexus_simulator(mocker)

    # add the required attributes to the model class
    fake_nexus_sim.model_files.well_files = {1: file}
    fake_nexus_sim.date_format = DateFormat.DD_MM_YYYY
    fake_nexus_sim._sim_controls.date_format_string = "%d/%m/%Y"
    fake_nexus_sim.start_date = start_date
    # mock out open
    wells_obj = NexusWells(fake_nexus_sim)
    wells_obj._load()

    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'peaceman_well_block_radius': 7.5,
                     'date_format': fake_nexus_sim.date_format}

    add_perf_dict_without_date = {'i': 4, 'j': 5, 'k': 6, 'peaceman_well_block_radius': 7.5}

    # Act
    wells_obj.add_completion(well_name='well1', completion_properties=add_perf_dict,
                             preserve_previous_completions=preserve_previous_completions, comments='test user comments')
    result = file.file_content_as_list

    # Assert
    assert result == expected_result

    # Act 2 / Assert 2 - failure case without a date
    with pytest.raises(AttributeError):
        wells_obj.add_completion(well_name='well1', completion_properties=add_perf_dict_without_date, )


@pytest.mark.parametrize('date_format',
                         ['DD/MM/YYYY',
                          DateFormat.DD_MM_YYYY])
def test_add_completion_correct_wellspec(mocker, date_format):
    start_date = '01/01/2020'
    # Arrange
    add_perf_date = '01/03/2020'

    # build 3 files that the add completion will have to find the right completion
    file_as_list_target = ['TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5']
    file_as_list_1 = ['TIME 01/02/2020', 'WELLSPEC well2', 'iw  jw   l    RADB', '3  5  41   0.3']
    file_as_list_2 = ['TIME 01/03/2020', 'WELLSPEC well3', 'iw  jw   l    RADB', '2  4   3   2222']

    file_target = NexusFile(location='wells_target.dat', file_content_as_list=file_as_list_target, )
    file_1 = NexusFile(location='wells_1.dat', file_content_as_list=file_as_list_1, )
    file_2 = NexusFile(location='wells_2.dat', file_content_as_list=file_as_list_2, )

    mock_nexus_sim = get_fake_nexus_simulator(mocker)

    # add the required attributes to the model class
    mock_nexus_sim.model_files.well_files = {1: file_1, 2: file_2, 3: file_target}
    mock_nexus_sim.date_format = DateFormat.DD_MM_YYYY
    mock_nexus_sim._sim_controls.date_format_string = "%d/%m/%Y"
    mock_nexus_sim.start_date = start_date
    # mock out open
    wells_obj = NexusWells(mock_nexus_sim)
    wells_obj._load()

    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'peaceman_well_block_radius': 7.5, 'date_format': date_format}

    expected_result = ['TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', '4 5 6 7.5\n']
    expected_result_file_1 = ['TIME 01/02/2020', 'WELLSPEC well2', 'iw  jw   l    RADB', '3  5  41   0.3']
    expected_result_file_2 = ['TIME 01/03/2020', 'WELLSPEC well3', 'iw  jw   l    RADB', '2  4   3   2222']

    # Act
    wells_obj.add_completion(well_name='well1', completion_properties=add_perf_dict,
                             preserve_previous_completions=True)
    result = file_target.file_content_as_list

    # Assert
    assert result == expected_result
    assert file_1.file_content_as_list == expected_result_file_1
    assert file_2.file_content_as_list == expected_result_file_2


@pytest.mark.parametrize('fcs_file_contents, wells_file, include_file_contents, add_perf_date, expected_result', [
    ('''DATEFORMAT DD/MM/YYYY
WelLS sEt 1 /my/wellspec/file.dat''',
     ''' ! wells file:
TIME 01/01/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
Include include_file.dat
TIME 01/05/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
''',
     '''! Inc File
TIME 01/03/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
4  5  6 4.2

TIME 01/04/2020
WELLSPEC well1
iw jw l radw
1  2  3 4.5
4  5  6 4.2
''',
     '01/03/2020',
     ['! Inc File\n',
      'TIME 01/03/2020\n',
      'WELLSPEC well1\n',
      'iw jw l radw\n',
      '1  2  3 4.5\n',
      '4  5  6 4.2\n',
      '4 5 6 7.5\n',
      '7 8 9 10.5\n',
      '20 20 20 5.5\n',
      '20 20 20 5.5\n',
      '20 20 20 5.5\n',
      '20 20 20 5.5\n',
      '20 20 20 5.5\n',
      '20 20 20 5.5\n',
      '\n',
      'TIME 01/04/2020\n',
      'WELLSPEC well1\n',
      'iw jw l radw\n',
      '1  2  3 4.5\n',
      '4  5  6 4.2\n', ],
     ),

], ids=['modify well in include_locations file'])
def test_add_completion_include_files(mocker, fcs_file_contents, wells_file,
                                      include_file_contents, add_perf_date, expected_result):
    '''TODO after an include in main file
        TODO inside an include file
     '''
    start_date = '01/01/2020'
    # Arrange
    # Mock out the surface and fcs file
    fcs_file_path = 'fcs_file.fcs'
    include_file_path = os.path.join('/my/wellspec', 'include_file.dat')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_file_path: fcs_file_contents,
            '/my/wellspec/file.dat': wells_file,
            include_file_path: include_file_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    mock_nexus_sim = get_fake_nexus_simulator(mocker=mocker, fcs_file_path=fcs_file_path, mock_open=False)

    mock_nexus_sim.start_date = start_date
    # mock out open
    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 7.5,
                     'date_format': DateFormat.DD_MM_YYYY}
    add_perf_dict_2 = {'date': add_perf_date, 'i': 7, 'j': 8, 'k': 9, 'well_radius': 10.5,
                       'date_format': DateFormat.DD_MM_YYYY}
    add_perf_dict_3 = {'date': add_perf_date, 'i': 20, 'j': 20, 'k': 20, 'well_radius': 5.5,
                       'date_format': DateFormat.DD_MM_YYYY}

    expected_include_file = NexusFile(location=include_file_path, include_locations=[],
                                      origin='/my/wellspec/file.dat', include_objects=None,
                                      file_content_as_list=expected_result)

    expected_wells_file_as_list = wells_file.splitlines(keepends=True)
    expected_wells_file = NexusFile(location='/my/wellspec/file.dat', include_objects=[expected_include_file],
                                    include_locations=[include_file_path], origin=fcs_file_path,
                                    file_content_as_list=expected_wells_file_as_list)
    # Act
    # test adding a load of completions sequentially
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict,
                                        preserve_previous_completions=True)
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict_2,
                                        preserve_previous_completions=True)
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict_3,
                                        preserve_previous_completions=True)
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict_3,
                                        preserve_previous_completions=True)
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict_3,
                                        preserve_previous_completions=True)
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict_3,
                                        preserve_previous_completions=True)
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict_3,
                                        preserve_previous_completions=True)
    mock_nexus_sim.wells.add_completion(well_name='well1', completion_properties=add_perf_dict_3,
                                        preserve_previous_completions=True)

    result = mock_nexus_sim.model_files.well_files[1].include_objects[0]

    # Assert
    assert result.file_content_as_list == expected_include_file.file_content_as_list
    assert result == expected_include_file
    assert mock_nexus_sim.model_files.well_files[1].file_content_as_list == expected_wells_file.file_content_as_list


def test_add_completion_other(mocker):
    # Arrange
    fcs_file_data = '''RUN_UNITS ENGLISH

    DATEFORMAT DD/MM/YYYY

    RECURRENT_FILES
    RUNCONTROL ref_runcontrol.dat
    WELLS Set 1 wells.dat'''
    runcontrol_data = 'START 01/01/2020'
    well_file_data = '''
    TIME 01/01/2020
    
    
    WELLSPEC well1
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    111 479  3 NA 0.35400   0.5 0.00000   NA NA
    111 479  4 NA 0.35400   0.5 0.00000   NA NA
    
    
    WELLSPEC well2
    IW  JW L KH    RADW  PPERF    SKIN RADB WI
    79 340 3 NA 0.35400   1 0.00000   NA NA
    79 340 4 NA 0.35400   1 0.00000   NA NA
    
    
    WELLSPEC well3
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    137 479  3 NA 0.35400   0.5 0.00000   NA NA
    137 479  4 NA 0.35400   0.5 0.00000   NA NA
    137 479  5 NA 0.35400   1 0.00000   NA NA
    137 479  6 NA 0.35400   1 0.00000   NA NA
    
    TIME 01/02/2020
    WELLSPEC well2
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    137 479  3 NA 0.35400   0.5 0.00000   NA NA
      
     TIME 01/03/2020
     
     WELLSPEC well2
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    137 479  3 NA 0.35400   0.5 0.00000   NA NA
    137 479  4 NA 0.35400   0.5 0.00000   NA NA'''
    expected_result = '''
    TIME 01/01/2020
    
    
    WELLSPEC well1
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    111 479  3 NA 0.35400   0.5 0.00000   NA NA
    111 479  4 NA 0.35400   0.5 0.00000   NA NA
    
    
    WELLSPEC well2
    IW  JW L KH    RADW  PPERF    SKIN RADB WI
    79 340 3 NA 0.35400   1 0.00000   NA NA
    79 340 4 NA 0.35400   1 0.00000   NA NA
    
    
    WELLSPEC well3
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    137 479  3 NA 0.35400   0.5 0.00000   NA NA
    137 479  4 NA 0.35400   0.5 0.00000   NA NA
    137 479  5 NA 0.35400   1 0.00000   NA NA
    137 479  6 NA 0.35400   1 0.00000   NA NA
    
    TIME 01/02/2020
    WELLSPEC well2
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    137 479  3 NA 0.35400   0.5 0.00000   NA NA
      

WELLSPEC well1
IW JW L RADW SKIN PPERF
111 479 3 0.354 0.0 0.5
111 479 4 0.354 0.0 0.5
4 5 6 7.5 NA NA

     TIME 01/03/2020
     
     WELLSPEC well2
     IW  JW  L KH    RADW  PPERF    SKIN RADB WI
    137 479  3 NA 0.35400   0.5 0.00000   NA NA
    137 479  4 NA 0.35400   0.5 0.00000   NA NA'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'fcs_file.dat': fcs_file_data,
            'wells.dat': well_file_data,
            'ref_runcontrol.dat': runcontrol_data,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='fcs_file.dat', mock_open=False)

    add_perf_date = '01/02/2020'

    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 7.5,
                     'date_format': DateFormat.DD_MM_YYYY}

    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)
    # Act
    model.wells.add_completion(well_name='well1', completion_properties=add_perf_dict)
    model.model_files.well_files[1].write_to_file(overwrite_file=True)

    # Assert

    check_file_read_write_is_correct(expected_file_contents=expected_result,
                                     modifying_mock_open=writing_mock_open,
                                     mocker_fixture=mocker, write_file_name='wells.dat')


@pytest.mark.parametrize('well_file_data, expected_uuid', [
    (''' TIME 01/01/2020
       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5     ! 3
       6 7 8   9.11     ! 4
       
       4 5 6 7.5        ! 6
       2 4 5 11         ! 7
       TIME 01/02/2020
       WELLSPEC DEV1
       IW JW L RADW
       !comment           
       3 4 5 6.5        ! 12
       ''',

     {'uuid1': [3],
      'uuid2': [4],
      'uuid3': [6],
      'uuid4': [7],
      'uuid6': [8],
      'uuid7': [9],
      'uuid5': [14],

      },
     ),

    (''' TIME 01/01/2020

TIME 01/02/2020
       WELLSPEC DEV1
       IW JW L RADW
       !comment           
       3 4 5 6.5     ! 6
       
       ''',

     {'uuid1': [12],
      'uuid2': [5],
      'uuid3': [6],
      },
     ),

], ids=['basic_test_2_lines', 'multiple_lines_added'])
def test_object_locations_updating(mocker, well_file_data, expected_uuid):
    # Arrange
    fcs_file_data = '''RUN_UNITS ENGLISH

    DATEFORMAT DD/MM/YYYY

    RECURRENT_FILES
    RUNCONTROL ref_runcontrol.dat
    WELLS Set 1 wells.dat'''
    runcontrol_data = 'START 01/01/2020'
    mocker.patch.object(uuid, 'uuid4', side_effect=['file_uuid', 'runcontrol_uuid', 'wells_file_uuid',
                                                    '1', 'wells_file_uuid', 'uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5',
                                                    'uuid6', 'uuid7'])

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'fcs_file.dat': fcs_file_data,
            'wells.dat': well_file_data,
            'ref_runcontrol.dat': runcontrol_data,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='fcs_file.dat', mock_open=False)

    add_perf_date = '01/01/2020'

    add_perf_dict_1 = {'date': add_perf_date, 'i': 11, 'j': 22, 'k': 33, 'well_radius': 44.5,
                       'date_format': DateFormat.DD_MM_YYYY}
    add_perf_dict_2 = {'date': add_perf_date, 'i': 44, 'j': 55, 'k': 66, 'well_radius': 77.5,
                       'date_format': DateFormat.DD_MM_YYYY}

    # Act
    model.wells.add_completion(well_name='DEV1', completion_properties=add_perf_dict_1)
    model.wells.add_completion(well_name='DEV1', completion_properties=add_perf_dict_2)

    # Assert

    assert model.model_files.well_files[1].object_locations == expected_uuid
