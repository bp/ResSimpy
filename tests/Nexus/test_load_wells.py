import pytest

from ResSimpy.Completion import Completion
from ResSimpy.Nexus.load_wells import load_wells


@pytest.mark.parametrize("file_contents",
[("""
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    """),
 ("""
    WELLSPEC ANOTHER_WELL
    JW IW L RADW
    2  1  3  4.5
    7 6 8   9.11
    """),
 ("""
    WELLSPEC "3"
    JW IW L RADW
    2  1  3  4.5
    7 6 8   9.11
    """)
 ], ids=["basic case", "swapped columns", "number name"])
def test_load_wellspec(mocker, file_contents):
    # Arrange
    start_date = '01/01/2023'

    expected_completion_1 = Completion(i=1, j=2, k=3, well_radius=4.5, date=start_date)
    expected_completion_2 = Completion(i=6, j=7, k=8, well_radius=9.11, date=start_date)

    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    result_wells = load_wells('test/file/location.dat', start_date=start_date)

    # Assert
    assert result_wells[0].completions[0] == expected_completion_1
    assert result_wells[0].completions[1] == expected_completion_2
    # Check that well radius is a useable float
    assert result_wells[0].completions[0].well_radius * 2 == 9.0
