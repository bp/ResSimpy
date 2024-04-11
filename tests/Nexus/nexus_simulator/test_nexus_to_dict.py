from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion


def test_nexus_completion_to_dict():
    # Arrange
    expected_completion = {'date': '01/02/2023', 'grid': 'GRID1', 'i': 1, 'j': 2, 'k': 3,
                           'partial_perf': 0.1, 'well_radius': 4.5}
    # Act
    result = NexusCompletion(date='01/02/2023', i=1, j=2, k=3, skin=None, well_radius=4.5, angle_v=None,
                             grid='GRID1', partial_perf=0.1,
                             date_format=DateFormat.DD_MM_YYYY).to_dict(add_units=True, include_nones=False)

    # Assert
    assert result == expected_completion
