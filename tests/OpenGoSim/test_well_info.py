from ResSimpy.Enums.WellTypeEnum import WellType
from ResSimpy.OpenGoSim.DataModels.OpenGoSimCompletion import OpenGoSimCompletion
from ResSimpy.OpenGoSim.DataModels.OpenGoSimWell import OpenGoSimWell


def test_get_printable_well_info():
    # Arrange
    expected_well_info_string = """
Well Name: test_well 1
Well Type: GAS_INJECTOR
Completions:
i: 1 j: 2 k: 3 | Opened on 1 JAN 2024 | Shut on 15 OCT 2025
i: 8 j: 222 k: 76 | Opened on 1 OCT 2025 | Shut on 15 OCT 2025

Dates well is Changed: 1 JAN 2024, 1 OCT 2025, 15 OCT 2025
"""

    completion_1 = OpenGoSimCompletion(date='1 JAN 2024', i=1, j=2, k=3)
    completion_2 = OpenGoSimCompletion(date='1 OCT 2025', i=8, j=222, k=76)
    completion_3 = OpenGoSimCompletion(date='15 OCT 2025', i=1, j=2, k=3, is_open=False)
    completion_4 = OpenGoSimCompletion(date='15 OCT 2025', i=8, j=222, k=76, is_open=False)
    completions = [completion_1, completion_2, completion_3, completion_4]
    well = OpenGoSimWell(well_name='test_well 1', completions=completions, well_type=WellType.GAS_INJECTOR)

    # Act
    result = well.printable_well_info

    # Assert
    assert result == expected_well_info_string
