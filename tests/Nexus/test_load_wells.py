import pytest

from ResSimpy.Completion import Completion
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.load_wells import load_wells


@pytest.mark.parametrize("file_contents, expected_name",
                         [("""
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    """, "WELL1"),
                          ("""
    WELLSPEC ANOTHER_WELL
    JW IW L RADW
    2  1  3  4.5
    7 6 8   9.11
    """, "ANOTHER_WELL"),
                          ("""
    WELLSPEC "3"
    JW IW L RADW
    2  1  3  4.5
    7 6 8   9.11
    """, "3"),
                          ("""
    WELLSPEC Well3
    JW IW L RADW
    2  1  3  4.5 !Inline Comment Here
    !Another Comment here
    7 6 8   9.11
    """, "Well3")

                          ], ids=["basic case", "swapped columns", "number name", "Comments"])
def test_load_basic_wellspec(mocker, file_contents, expected_name):
    # Arrange
    start_date = '01/01/2023'

    expected_completion_1 = NexusCompletion(i=1, j=2, k=3, well_radius=4.5, date=start_date)
    expected_completion_2 = NexusCompletion(i=6, j=7, k=8, well_radius=9.11, date=start_date)
    expected_well = NexusWell(well_name=expected_name, completions=[expected_completion_1, expected_completion_2])

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    result_wells = load_wells('test/file/location.dat', start_date=start_date)

    # Assert
    # assert result_wells[0].completions[0] == expected_completion_1
    # assert result_wells[0].completions[1] == expected_completion_2

    # Check that well radius is a useable float
    assert result_wells[0].completions[0].well_radius * 2 == 9.0

    assert result_wells[0] == expected_well

    assert result_wells[0].well_name == expected_name

    # TODO: check that absent columns are set to None


def test_load_wells_multiple_wells(mocker):
    # Arrange
    start_date = '01/01/2023'

    file_contents = """
    WELLSPEC DEV1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    
    WELSPEC DEV2
    12 12   13 4.50000000000
    14 15 143243            0.00002
    18 155 143243 40.00002
    """

    expected_well_1_completion_1 = Completion(i=1, j=2, k=3, well_radius=4.5, date=start_date)
    expected_well_1_completion_2 = Completion(i=6, j=7, k=8, well_radius=9.11, date=start_date)

    expected_well_2_completion_1 = Completion(i=12, j=12, k=13, well_radius=4.50000000000, date=start_date)
    expected_well_2_completion_2 = Completion(i=14, j=15, k=143243, well_radius=0.00002, date=start_date)
    expected_well_2_completion_3 = Completion(i=18, j=155, k=143243, well_radius=40.00002, date=start_date)

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    result_wells = load_wells('/another/test/file/location.dat', start_date=start_date)

    # Assert
    assert result_wells[0].completions[0] == expected_well_1_completion_1
    assert result_wells[0].completions[1] == expected_well_1_completion_2
    assert result_wells[1].completions[0] == expected_well_2_completion_1
    assert result_wells[1].completions[1] == expected_well_2_completion_2
    assert result_wells[1].completions[2] == expected_well_2_completion_3

    # Check that well radius is a useable float
    assert result_wells[0].completions[0].well_radius * 2 == 9.0

    assert result_wells[0].well_name == "DEV1"

# Date in file

# All Columns Present

# NA Values

# Multiple times and wells

# Units - if no units specified, assume same as run units
