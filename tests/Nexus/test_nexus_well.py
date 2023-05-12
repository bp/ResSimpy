import os
from unittest.mock import PropertyMock, patch, Mock
import pytest
from ResSimpy.Enums.HowEnum import OperationEnum

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from ResSimpy.Nexus.NexusWells import NexusWells
from tests.multifile_mocker import mock_multiple_files


@pytest.mark.parametrize('completions, expected_perforations', [
    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2023', partial_perf=0.5)],
     # Expected:
     [NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2023', partial_perf=0.5)]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=4, well_radius=9.11, date='01/02/2024', partial_perf=0),
      NexusCompletion(i=1, j=2, k=5, well_radius=9.11, date='01/02/2024', status='ON'),
      NexusCompletion(i=1, j=2, k=6, well_radius=9.11, date='01/02/2024', status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=7, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=0.000),
      NexusCompletion(i=1, j=2, k=8, well_radius=9.11, date='01/02/2024', status='OFF', partial_perf=1),
      NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2025', status='ON', partial_perf=1, well_indices=1),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2028', well_indices=3),
      NexusCompletion(i=1, j=2, k=11, well_radius=9.11, date='01/02/2028', perm_thickness_ovr=1),
      NexusCompletion(i=1, j=2, k=11, well_radius=9.11, date='01/05/2028', perm_thickness_ovr=1, partial_perf=1,
                      kh_mult=1),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/03/2034', partial_perf=0.5, length=100),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/05/2034', partial_perf=0.5, length=0)],
     # Expected:
     [NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=5, well_radius=9.11, date='01/02/2024', status='ON'),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2025', status='ON', partial_perf=1, well_indices=1),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2028', well_indices=3),
      NexusCompletion(i=1, j=2, k=11, well_radius=9.11, date='01/02/2028', perm_thickness_ovr=1),
      NexusCompletion(i=1, j=2, k=11, well_radius=9.11, date='01/05/2028', perm_thickness_ovr=1, partial_perf=1,
                      kh_mult=1),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/03/2034', partial_perf=0.5, length=100)]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1, status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, status='OFF'),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, perm_thickness_ovr=0),
      NexusCompletion(i=1, j=2, k=4, date='01/02/2023', partial_perf=0.5, well_indices=5, perm_thickness_ovr=5,
                      length=0),
      NexusCompletion(i=1, j=2, k=5, date='01/02/2023', partial_perf=0.5, well_indices=5, kh_mult=0)],
     # Expected:
     []),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')],
     # Expected:
     [NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1',  skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')]),

    ([], [])

], ids=['basic case', 'mixture of perf and not perf', 'no perforations', 'using defaults', 'empty list'])
def test_get_perforations(completions, expected_perforations):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     units=UnitSystem.ENGLISH)

    # Act
    result = well.perforations

    # Assert
    assert result == expected_perforations


@pytest.mark.parametrize('completions, expected_perforation', [
    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2023', partial_perf=0.5)],
     # Expected:
     NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                     partial_perf=0.1)),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=4, well_radius=9.11, date='01/02/2024', partial_perf=0),
      NexusCompletion(i=1, j=2, k=5, well_radius=9.11, date='01/02/2024', status='ON'),
      NexusCompletion(i=1, j=2, k=6, well_radius=9.11, date='01/02/2024', status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=7, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=0.000),
      NexusCompletion(i=1, j=2, k=8, well_radius=9.11, date='01/02/2024', status='OFF', partial_perf=1),
      NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2025', status='ON', partial_perf=1, well_indices=1),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2028', well_indices=3),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5)],
     # Expected:
     NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                     partial_perf=0.1)),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1, status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, status='OFF')],
     # Expected:
     None),

    ([], None)

], ids=['basic case', 'mixture of perf and not perf', 'no perforations', 'empty list'])
def test_get_first_perforation(completions, expected_perforation):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     units=UnitSystem.ENGLISH)

    # Act
    result = well.first_perforation

    # Assert
    assert result == expected_perforation


@pytest.mark.parametrize('completions, expected_shutins', [
    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0),
      NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2023', partial_perf=0.5, status='OFF')],
     # Expected:
     [NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0),
      NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2023', partial_perf=0.5, status='OFF')]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=4, well_radius=9.11, date='01/02/2024', partial_perf=0),
      NexusCompletion(i=1, j=2, k=5, well_radius=9.11, date='01/02/2024', status='ON'),
      NexusCompletion(i=1, j=2, k=6, well_radius=9.11, date='01/02/2024', status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=7, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=0.000),
      NexusCompletion(i=1, j=2, k=8, well_radius=9.11, date='01/02/2024', status='OFF', partial_perf=1),
      NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2025', status='ON', partial_perf=1, well_indices=1),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2028', well_indices=3),
      NexusCompletion(i=1, j=2, k=11, well_radius=9.11, date='01/02/2028', well_indices=3, partial_perf=1, length=0),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5)],
     # Expected:
     [NexusCompletion(i=1, j=2, k=4, well_radius=9.11, date='01/02/2024', partial_perf=0),
      NexusCompletion(i=1, j=2, k=6, well_radius=9.11, date='01/02/2024', status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=7, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=0.000),
      NexusCompletion(i=1, j=2, k=8, well_radius=9.11, date='01/02/2024', status='OFF', partial_perf=1),
      NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0),
      NexusCompletion(i=1, j=2, k=11, well_radius=9.11, date='01/02/2028', well_indices=3, partial_perf=1, length=0)
      ]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1, status='ON'),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5)],
     # Expected:
     []),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')],
     # Expected:
     []),

    ([], [])

], ids=['basic case', 'mixture of perf and not perf', 'no shutins', 'no perf info', 'empty list'])
def test_get_shutins(completions, expected_shutins):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     units=UnitSystem.ENGLISH)

    # Act
    result = well.shutins

    # Assert
    assert result == expected_shutins


@pytest.mark.parametrize('completions, expected_shutin', [
    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0),
      NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2023', partial_perf=0.5, status='OFF')],
     # Expected:
     NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2023', partial_perf=0.5, status='OFF')),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=4, well_radius=9.11, date='01/02/2024', partial_perf=0),
      NexusCompletion(i=1, j=2, k=5, well_radius=9.11, date='01/02/2024', status='ON'),
      NexusCompletion(i=1, j=2, k=6, well_radius=9.11, date='01/02/2024', status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=7, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=0.000),
      NexusCompletion(i=1, j=2, k=8, well_radius=9.11, date='01/02/2024', status='OFF', partial_perf=1),
      NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2025', status='ON', partial_perf=1, well_indices=1),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2028', well_indices=3),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5)],
     # Expected:
     NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0)),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1, status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, status='OFF')],
     # Expected:
     NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, status='OFF')),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5)],
     # Expected:
     None),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')],
     # Expected:
     None),

    ([], None)

], ids=['basic case', 'mixture of perf and not perf', 'only shutins', 'no shutins', 'no perf info', 'empty list'])
def test_get_last_shutin(completions, expected_shutin):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     units=UnitSystem.ENGLISH)

    # Act
    result = well.last_shutin

    # Assert
    assert result == expected_shutin


def test_printable_well_info():
    # Arrange
    completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None,
                                   angle_v=None, status='ON')
    completion_2 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2024', grid='GRID1', skin=None,
                                   angle_v=None, status='ON', partial_perf=1)
    completion_3 = NexusCompletion(i=1, j=2, k=3, date='01/02/2025', partial_perf=0)
    completions = [completion_1, completion_2, completion_3]

    well = NexusWell(well_name='test well', completions=completions, units=UnitSystem.LAB)

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

    well = NexusWell(well_name='test well', completions=completions, units=UnitSystem.METRIC)

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
    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      well_indices=3),
      NexusCompletion(i=1, j=2, k=3, well_radius=9.11, date='01/02/2024', partial_perf=0.5)],
     # Expected:
     [('01/01/2023', 3), ('01/02/2024', 3)]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=4, well_radius=9.11, date='01/02/2024', partial_perf=0),
      NexusCompletion(i=1, j=2, k=5, well_radius=9.11, date='01/02/2024', status='ON'),
      NexusCompletion(i=1, j=2, k=6, well_radius=9.11, date='01/02/2024', status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=7, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=0.000),
      NexusCompletion(i=1, j=2, k=8, well_radius=9.11, date='01/02/2024', status='OFF', partial_perf=1),
      NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2025', status='ON', partial_perf=1, well_indices=1),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2028', well_indices=3),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5)],
     # Expected:
     [('01/01/2023', 3), ('01/02/2024', 5), ('01/02/2025', 10), ('01/02/2028', 10), ('01/02/2034', 38)]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None, partial_perf=0),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1, well_indices=0)],
     # Expected:
     []),

    ([], []),

    ([NexusCompletion(i=1, j=2, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      depth_to_top=1000, depth_to_bottom=1300, well_indices=1),
      NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=1, depth_to_top=1156,
                      depth_to_bottom=1234),
      NexusCompletion(i=1, j=2, date='01/02/2023', status='OFF', partial_perf=1, depth_to_top=1156,
                      depth_to_bottom=1234)],
     # Expected:
     [('01/01/2023', (1000, 1300)), ('01/02/2023', (1156, 1234))]),

    ([NexusCompletion(i=1, j=2, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      depth_to_top=1000, depth_to_bottom=1300, well_indices=1),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
      NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=2, depth_to_top=1156,
                      depth_to_bottom=1234),
      NexusCompletion(i=1, j=2,k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
      NexusCompletion(i=1, j=2, date='01/03/2025', status='ON', partial_perf=1, well_indices=3, depth_to_top=1156,
                      depth_to_bottom=1234),
      ],
     # Expected:
     [('01/01/2023', (1000, 1300)),
      ('01/02/2023', (1156, 1234)),
      ('01/03/2025', (1156, 1234)),]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      well_indices=1),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
      NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                      depth_to_bottom=1234),
      NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
      NexusCompletion(i=1, j=2, date='01/03/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                      depth_to_bottom=1234),
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
                     units=UnitSystem.METKGCM2)

    # Act
    result = well.completion_events

    # Assert
    assert result == expected_shutin
@pytest.mark.parametrize('existing_completions',[
([
        NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      well_indices=1),
        NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                      depth_to_bottom=1234),
        NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
        NexusCompletion(i=1, j=2, date='01/03/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                      depth_to_bottom=1234),
        ]),]
)
def test_find_completion(mocker, existing_completions):
    # Arrange
    completion_to_find = {'date': '01/02/2023', 'i': 1, 'j': 2, 'k': 3,}
    completion_to_fail = {'date': '01/02/2023'}
    expected_completions = [
        NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                      depth_to_bottom=1234),
        NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
        ]
    completion_to_find_as_completion = NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON',)
    well = NexusWell(well_name='test well', completions=existing_completions, units=UnitSystem.METKGCM2)
    expected_result = NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1)

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
        NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      well_indices=1),
        NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                      depth_to_bottom=1234),
        NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
        NexusCompletion(i=1, j=2, date='01/03/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                      depth_to_bottom=1234),
        ]
    new_completion_props = {'i': 3, 'j': 3, 'k': 5, 'well_radius': 1005.2}

    new_nexus_completion = NexusCompletion(date=new_date, i=3, j=3, k=5, well_radius=1005.2)

    expected_completions = [x for x in existing_completions]
    expected_completions.append(new_nexus_completion)

    expected_well = NexusWell(well_name='test well', completions=expected_completions,
                              units=UnitSystem.METKGCM2)
    well = NexusWell(well_name='test well', completions=existing_completions,
                                    units=UnitSystem.METKGCM2)
    # Act
    well.add_completion(date=new_date, completion_properties=new_completion_props)
    # Assert
    assert well == expected_well

def test_remove_completion():
    # Arrange
    existing_completions = [
        NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                       well_indices=1),
        NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                       depth_to_bottom=1234),
        NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
        NexusCompletion(i=1, j=2, date='01/03/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                       depth_to_bottom=1234),
        ]
    expected_completions_after_removal = [
    NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                    well_indices=1),
    NexusCompletion(i=1, j=2, date='01/03/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                                        depth_to_bottom=1234),
    ]
    expected_result = NexusWell(well_name='test well', completions=expected_completions_after_removal,
                                units=UnitSystem.METKGCM2)
    perfs_to_remove = {'date': '01/02/2023', 'i': 1, 'j': 2,}
    remove_well = NexusWell(well_name='test well', completions=existing_completions,
                     units=UnitSystem.METKGCM2)

    # Act
    comp_to_remove = remove_well.find_completions(perfs_to_remove)
    remove_well.remove_completions(completions_to_remove=comp_to_remove)
    # Assert
    assert remove_well == expected_result


def test_modify_completion():
    # Arrange
    existing_completions = [
        NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                       well_indices=1),
        NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                       depth_to_bottom=1234),
        NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
        NexusCompletion(i=1, j=2, date='01/03/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                       depth_to_bottom=1234),
        ]

    changed_completion = NexusCompletion(i=1, j=5, k=6, date='01/03/2023', status='ON', partial_perf=0.5, well_indices=0,
                                         depth_to_top=1156, depth_to_bottom=1234, perm_thickness_ovr=10000.4)
    expected_completions = existing_completions[:-1] + [changed_completion]
    completion_id = existing_completions[-1].id
    changes = {'i': 1, 'j': 5, 'k': 6, 'perm_thickness_ovr': 10000.4, 'partial_perf': 0.5}

    well = NexusWell(well_name='test well', completions=existing_completions, units=UnitSystem.METKGCM2)
    expected_well = NexusWell(well_name='test well', completions=expected_completions, units=UnitSystem.METKGCM2)

    # Act
    well.modify_completion(new_completion_properties=changes, completion_to_modify=completion_id)

    # Assert
    assert well.completions[-1] == changed_completion
    # check the id is still the same:
    assert well.find_completion(NexusCompletion(i=1, j=5, k=6, date='01/03/2023', status='ON', partial_perf=0.5, well_indices=0,
                                         depth_to_top=1156, depth_to_bottom=1234, perm_thickness_ovr=10000.4)).id == completion_id

def test_well_dates(mocker):
    # Arrange
    well_1_completions = [
        NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                        well_indices=1),
        NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                        depth_to_bottom=1234),]

    well_2_completions = [
        NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
        NexusCompletion(i=1, j=2, date='01/03/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                        depth_to_bottom=1234),
                        ]
    mock_sim = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusSimulator.NexusSimulator', mock_sim)
    well = NexusWells(mock_sim)

    well.__setattr__('_NexusWells__wells', [NexusWell(well_name='well1', completions=well_1_completions, units=UnitSystem.METRIC),
                                NexusWell(well_name='well2', completions=well_2_completions, units=UnitSystem.METRIC)])

    expected_result = {'01/01/2023', '01/02/2023', '01/03/2023'}
    # Act
    result = well.get_wells_dates()

    # Assert
    assert result == expected_result


def test_wells_modify(mocker):
    # Arrange
    well_1_completions = [
        NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                        well_indices=1),
        NexusCompletion(i=1, j=2, k=3, date='01/02/2023', status='ON', partial_perf=1),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                        depth_to_bottom=1234),
                        ]

    well_2_completions = [
        NexusCompletion(i=1, j=2, k=5, date='01/02/2023', status='ON', partial_perf=1, well_indices=3),
        NexusCompletion(i=1, j=2, date='01/02/2023', status='ON', partial_perf=1, well_indices=0, depth_to_top=1156,
                        depth_to_bottom=1234),
                        ]
    well_1 = NexusWell(well_name='well1', completions=well_1_completions, units=UnitSystem.METRIC)
    well_2 = NexusWell(well_name='well2', completions=well_2_completions, units=UnitSystem.METRIC)

    mock_sim = mocker.MagicMock()
    mocker.patch('ResSimpy.Nexus.NexusSimulator.NexusSimulator', mock_sim)
    wells = NexusWells(mock_sim)

    wells.__setattr__('_NexusWells__wells', [well_1, well_2])
    date = '01/02/2023'
    perf_1_to_add = {'date': date, 'i': 3, 'j': 3, 'k': 5, 'well_radius': 1005.2}
    perf_2_to_add = {'date': date, 'i': 1, 'j': 2, 'k': 6, 'permeability': 1005.2}
    perf_to_remove = {'date': date, 'i':1, 'j':2, 'status':'ON', 'partial_perf':1, 'well_indices':0, 'depth_to_top':1156,
                        'depth_to_bottom':1234}

    new_nexus_completion_1 = NexusCompletion(date=date, i=3, j=3, k=5, well_radius=1005.2)
    new_nexus_completion_2 = NexusCompletion(date=date, i=1, j=2, k=6, permeability=1005.2)
    expected_completions = well_1_completions[0:2] + [new_nexus_completion_1, new_nexus_completion_2]

    expected_result = [NexusWell(well_name='well1', completions=expected_completions, units=UnitSystem.METRIC),
                       NexusWell(well_name='well2', completions=well_2_completions, units=UnitSystem.METRIC)]

    # Act
    wells.modify_well(well_name='well1', perforations_properties=[perf_1_to_add, perf_2_to_add],
                      how=OperationEnum.ADD, write_to_file=False)
    wells.modify_well(well_name='well1', perforations_properties=[perf_to_remove], how=OperationEnum.REMOVE,
                      write_to_file=False)
    # Assert
    assert wells.get_wells()[0].completions == expected_result[0].completions

@pytest.mark.parametrize('file_as_list, add_perf_date, preserve_previous_completions, expected_result',[
(['WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5'], '01/01/2020', False,
['WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', '4 5 6 7.5\n']),

(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', 'TIME 01/02/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', True,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', 'TIME 01/02/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', '4 5 6 7.5\n', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2']
  ),

(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', 'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', False,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', '', 'TIME 01/02/2020', 'WELLSPEC well1', 'IW JW L RADB', '4 5 6 7.5\n',
'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2']
  ),

(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', 'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', True,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', '', 'TIME 01/02/2020', 'WELLSPEC well1', 'IW JW L RADB', '1 2 3 1.5', '4 5 6 7.5\n',
'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2']
  ),

(['WELLSPEC well2', 'iw  jw   l    RADB', '13  12   11   3.14', 'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB',
'1  2   5   2.5', 'WELLSPEC well2', 'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020',
'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', True,
['WELLSPEC well2', 'iw  jw   l    RADB', '13  12   11   3.14', '', 'TIME 01/02/2020', 'WELLSPEC well1', 'IW JW L RADB', '4 5 6 7.5\n',
'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2']
  ),


(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', 'TIME 01/02/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', True,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', 'TIME 01/02/2020', 'WELLSPEC well1', 'iw  jw   l    KH RADB', '1  2   5   2.5 NA', '4 5 6 NA 7.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2']
  ),
(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
'iw  jw    KH  PPERF  SKIN  STAT', '!Some comment line', '1  2   2.5   2   3.5  ON', '', '9  8   6.5   40   32.5  OFF',
'11  12   4.5   43   394.5  OFF', '', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', True,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
'iw  jw    KH  PPERF  SKIN  STAT L RADB', '!Some comment line', '1  2   2.5   2   3.5  ON NA NA', '', '9  8   6.5   40   32.5  OFF NA NA',
'11  12   4.5   43   394.5  OFF NA NA', '', '4 5 NA NA NA NA 6 7.5', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  ),

(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', 'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', False,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5',  'TIME 01/02/2020', 'WELLSPEC well2', 'iw  jw   l    RADB',
'13  12   11   3.14', '', 'WELLSPEC well1', 'IW JW L RADB', '4 5 6 7.5\n',
'TIME 01/04/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   5   2.5', 'WELLSPEC well2',
'iw  jw   l    RADB', '12  11   10   3.14', 'TIME 01/05/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2']
  ),

(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
'iw  jw    KH  PPERF  SKIN  STAT', '!Some comment line', '1  2   2.5   2   3.5  ON !COMMMENT', '', '9  8   6.5   40   32.5  OFF',
'11  12   4.5   43   394.5  OFF', '', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', True,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
'iw  jw    KH  PPERF  SKIN  STAT L RADB', '!Some comment line', '1  2   2.5   2   3.5  ON NA NA !COMMMENT', '', '9  8   6.5   40   32.5  OFF NA NA',
'11  12   4.5   43   394.5  OFF NA NA', '', '4 5 NA NA NA NA 6 7.5', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  ),

(['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
'iw  jw    KH  PPERF  SKIN  STAT !COmment!', '!Some comment line', '1  2   2.5   2   3.5  ON !COMMMENT', '', '9  8   6.5   40   32.5  OFF',
'11  12   4.5   43   394.5  OFF', '', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  '01/02/2020', True,
['TIME 01/01/2020', 'WELLSPEC well1', 'iw  jw   l    KH', '1  2   3   1.5', 'TIME 01/02/2020', 'WELLSPEC well1',
'iw  jw    KH  PPERF  SKIN  STAT L RADB !COmment!', '!Some comment line', '1  2   2.5   2   3.5  ON NA NA !COMMMENT', '', '9  8   6.5   40   32.5  OFF NA NA',
'11  12   4.5   43   394.5  OFF NA NA', '', '4 5 NA NA NA NA 6 7.5', 'TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '2 3   4   555.2'],
  ),
], ids=['basic_test', 'insert in middle of file','No time card for new comp', 'preserve previous completions', 'No previous well',
'Not overlapping columns', 'no overlap and multiple rows', 'Time card no comp', 'comment with not overlapping columns',
'comment inline with headers'])
def utest_add_completion_write(mocker, file_as_list, add_perf_date, preserve_previous_completions, expected_result):
    ''' TODO insert into include files
     TODO write multiple completions in a row
    '''
    start_date = '01/01/2020'
    # Arrange
    open_mock = mocker.mock_open(read_data='')
    mocker.patch("builtins.open", open_mock)
    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    file = NexusFile(location='wells.dat', file_content_as_list=file_as_list, )

    mock_nexus_sim = NexusSimulator('/path/fcs_file.fcs')

    # add the required attributes to the model class
    mock_nexus_sim.fcs_file.well_files = {1: file}
    mock_nexus_sim.date_format = DateFormat.DD_MM_YYYY
    mock_nexus_sim.Runcontrol.date_format_string = "%d/%m/%Y"
    mock_nexus_sim.start_date_set(start_date)
    # mock out open
    wells_obj = NexusWells(mock_nexus_sim)
    wells_obj.load_wells()

    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'bore_radius': 7.5}

    add_perf_dict_without_date = {'i': 4, 'j': 5, 'k': 6, 'bore_radius': 7.5}

    # Act
    wells_obj.add_completion(well_name='well1', completion_properties=add_perf_dict,
                             preserve_previous_completions=preserve_previous_completions)
    result = file.file_content_as_list

    # Assert
    assert result == expected_result

    # Act 2 / Assert 2 - failure case without a date
    with pytest.raises(AttributeError):
        wells_obj.add_completion(well_name='well1', completion_properties=add_perf_dict_without_date,)


def test_add_completion_correct_wellspec(mocker):
    start_date = '01/01/2020'
    # Arrange
    open_mock = mocker.mock_open(read_data='')
    mocker.patch("builtins.open", open_mock)
    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)
    add_perf_date = '01/03/2020'

    # build 3 files that the add completion will have to find the right completion
    file_as_list_target = ['TIME 01/03/2020', 'WELLSPEC well1', 'iw  jw   l    RADB', '1  2   3   1.5']
    file_as_list_1 = ['TIME 01/02/2020', 'WELLSPEC well2', 'iw  jw   l    RADB', '3  5  41   0.3']
    file_as_list_2 = ['TIME 01/03/2020', 'WELLSPEC well3', 'iw  jw   l    RADB', '2  4   3   2222']

    file_target = NexusFile(location='wells_target.dat', file_content_as_list=file_as_list_target, )
    file_1 = NexusFile(location='wells_1.dat', file_content_as_list=file_as_list_1, )
    file_2 = NexusFile(location='wells_2.dat', file_content_as_list=file_as_list_2, )

    mock_nexus_sim = NexusSimulator('/path/fcs_file.fcs')

    # add the required attributes to the model class
    mock_nexus_sim.fcs_file.well_files = {1: file_1, 2: file_2, 3: file_target}
    mock_nexus_sim.date_format = DateFormat.DD_MM_YYYY
    mock_nexus_sim.Runcontrol.date_format_string = "%d/%m/%Y"
    mock_nexus_sim.start_date_set(start_date)
    # mock out open
    wells_obj = NexusWells(mock_nexus_sim)
    wells_obj.load_wells()

    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'bore_radius': 7.5}

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
''' ! Wells file:
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
'''! Include File
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
['! Include File\n',
'TIME 01/03/2020\n',
'WELLSPEC well1\n',
'iw jw l radw\n',
'1  2  3 4.5\n',
'4  5  6 4.2\n',
'\n',
'4 5 6 7.5\n',
'TIME 01/04/2020\n',
'WELLSPEC well1\n',
'iw jw l radw\n',
'1  2  3 4.5\n',
'4  5  6 4.2\n',],
),

], ids=['modify well in includes file'])
def test_add_completion_include_files(mocker, fcs_file_contents, wells_file, include_file_contents, add_perf_date, expected_result):
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

    ls_dir = Mock(side_effect=lambda x: [])
    mocker.patch('os.listdir', ls_dir)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)
    add_perf_date = '01/03/2020'

    mock_nexus_sim = NexusSimulator('fcs_file.fcs')

    mock_nexus_sim.start_date_set(start_date)
    # mock out open
    wells_obj = NexusWells(mock_nexus_sim)
    wells_obj.load_wells()

    add_perf_dict = {'date': add_perf_date, 'i': 4, 'j': 5, 'k': 6, 'well_radius': 7.5}

    expected_include_file = NexusFile(location=include_file_path, includes=[],
    origin='/my/wellspec/file.dat', includes_objects=None, file_content_as_list=expected_result)

    expected_wells_file_as_list = [x.replace('include_file.dat', '') for x in wells_file.splitlines(keepends=True)]
    expected_wells_file_as_list.insert(expected_wells_file_as_list.index('Include \n')+1, expected_include_file)
    expected_wells_file = NexusFile(location='/my/wellspec/file.dat', includes_objects=[expected_include_file],
    includes=[include_file_path], origin=fcs_file_path, file_content_as_list=expected_wells_file_as_list)
    # Act
    wells_obj.add_completion(well_name='well1', completion_properties=add_perf_dict,
                             preserve_previous_completions=True)
    result = mock_nexus_sim.fcs_file.well_files[1].includes_objects[0]

    # Assert
    assert result.file_content_as_list == expected_include_file.file_content_as_list
    assert result == expected_include_file
    assert mock_nexus_sim.fcs_file.well_files[1].file_content_as_list == expected_wells_file.file_content_as_list
