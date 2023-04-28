from unittest.mock import PropertyMock, patch
import pytest
from ResSimpy.Enums.HowEnum import OperationEnum

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusWells import NexusWells


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

    changed_completion = NexusCompletion(i=1, j=5, k=6, date='01/03/2023', status='ON', partial_perf=1, well_indices=0,
                                         depth_to_top=1156, depth_to_bottom=1234, perm_thickness_ovr=10000.4)
    expected_completions = existing_completions[:-1] + [changed_completion]
    completion_id = existing_completions[-1].id
    changes = {'i': 1, 'j': 5, 'k': 6, 'perm_thickness_ovr': 10000.4}

    well = NexusWell(well_name='test well', completions=existing_completions, units=UnitSystem.METKGCM2)
    expected_well = NexusWell(well_name='test well', completions=expected_completions, units=UnitSystem.METKGCM2)

    # Act
    well.modify_completion(new_completion_properties=changes, completion_to_modify=completion_id)

    # Assert
    assert well.completions[-1] == changed_completion
    # check the id is still the same:
    assert well.find_completion(NexusCompletion(i=1, j=5, k=6, date='01/03/2023', status='ON', partial_perf=1, well_indices=0,
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

    well = NexusWells()

    well.__setattr__('_NexusWells__wells', [NexusWell(well_name='well1', completions=well_1_completions, units=UnitSystem.METRIC),
                                NexusWell(well_name='well2', completions=well_2_completions, units=UnitSystem.METRIC)])

    expected_result = {'01/01/2023', '01/02/2023', '01/03/2023'}
    # Act
    result = well.get_wells_dates()

    # Assert
    assert result == expected_result


def test_wells_modify():
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

    wells = NexusWells()

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


