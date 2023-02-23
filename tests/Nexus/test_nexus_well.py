import pytest

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.UnitsEnum import Units


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
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5)],
     # Expected:
     [NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1),
      NexusCompletion(i=1, j=2, k=5, well_radius=9.11, date='01/02/2024', status='ON'),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2025', status='ON', partial_perf=1, well_indices=1),
      NexusCompletion(i=1, j=2, k=10, well_radius=9.11, date='01/02/2028', well_indices=3),
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5)]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1, status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, status='OFF')],
     # Expected:
     []),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')],
     # Expected:
     []),

    ([], [])

], ids=['basic case', 'mixture of perf and not perf', 'no perforations', 'no perf info', 'empty list'])
def test_get_perforations(completions, expected_perforations):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     units=Units.OILFIELD)

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
                     units=Units.OILFIELD)

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
      NexusCompletion(i=1, j=2, k=38, well_radius=9.11, date='01/02/2034', partial_perf=0.5)],
     # Expected:
     [NexusCompletion(i=1, j=2, k=4, well_radius=9.11, date='01/02/2024', partial_perf=0),
      NexusCompletion(i=1, j=2, k=6, well_radius=9.11, date='01/02/2024', status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=7, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=0.000),
      NexusCompletion(i=1, j=2, k=8, well_radius=9.11, date='01/02/2024', status='OFF', partial_perf=1),
      NexusCompletion(i=1, j=2, k=9, well_radius=9.11, date='01/02/2024', status='ON', partial_perf=1, well_indices=0),
      ]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1, status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, status='OFF')],
     # Expected:
     [NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None,
                      partial_perf=0.1, status='ON', well_indices=0),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023', partial_perf=0.5, well_indices=5, status='OFF')
      ]),

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')],
     # Expected:
     [NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')
      ]),

    ([], [])

], ids=['basic case', 'mixture of perf and not perf', 'no shutins', 'no perf info', 'empty list'])
def test_get_shutins(completions, expected_shutins):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     units=Units.OILFIELD)

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

    ([NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date='01/01/2023', grid='GRID1', skin=None, angle_v=None),
      NexusCompletion(i=1, j=2, k=3, date='01/02/2023')],
     # Expected:
     NexusCompletion(i=1, j=2, k=3, date='01/02/2023')),

    ([], None)

], ids=['basic case', 'mixture of perf and not perf', 'no shutins', 'no perf info', 'empty list'])
def test_get_last_shutin(completions, expected_shutin):
    # Arrange
    well = NexusWell(well_name='test well', completions=completions,
                     units=Units.OILFIELD)

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

    well = NexusWell(well_name='test well', completions=completions, units=Units.OILFIELD)

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

    well = NexusWell(well_name='test well', completions=completions, units=Units.OILFIELD)

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
