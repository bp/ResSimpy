import numpy as np
import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.NexusValveMethod import NexusValveMethod

@pytest.mark.parametrize("file_contents, expected_valve_properties",
    [("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    VALVE QALL
    SETTING VC
    1 NOFLOW ! Note NOFLOW
    2 5.4
    3 0.8

    ! Comment in middle of table
    4 0.3
    5 0.01
    ENDVALVE
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'DP_RATE': 'QALL',
          'VALVE': pd.DataFrame({'SETTING': [1, 2, 3, 4, 5],
                                 'VC': ['NOFLOW', '5.4', '0.8', '0.3', '0.01']
                                 })
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    ICV 
    SETTING CV
    1 0.
    2 4.2
    3 6.2
    4 10.4
    5 16.7
    ENDICV
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'ICV': pd.DataFrame({'SETTING': [1, 2, 3, 4, 5],
                               'CV': [0, 4.2, 6.2, 10.4, 16.7]
                               })
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    CHOKE
    SETTING ID
    20.5 0.014465
    21.5 0.050908
    22.5 0.079637
    ENDCHOKE
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'CHOKE': pd.DataFrame({'SETTING': [20.5, 21.5, 22.5],
                                 'ID': [0.014465, 0.050908, 0.079637]
                                 })
          }
    )
    ], ids=['valve','icv','choke']
)
def test_read_valve_properties_from_file(mocker, file_contents, expected_valve_properties):
    # Arrange
    valve_obj = NexusValveMethod(file_path='test/file/valve.dat', method_number=1)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    valve_obj.read_properties()
    props = valve_obj.properties

    # Assert
    for key in expected_valve_properties:
        if isinstance(expected_valve_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_valve_properties[key], props[key])
        else:
            assert props[key] == expected_valve_properties[key]


def test_nexus_valve_repr():
    # Arrange
    valve_obj = NexusValveMethod(file_path='test/file/valve.dat', method_number=1)
    valve_obj.properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                            'DP_RATE': 'QALL',
                            'VALVE': pd.DataFrame({'SETTING': [1, 2, 3, 4, 5],
                                                   'VC': ['NOFLOW', '5.4', '0.8', '0.3', '0.01']
                                                   })}
    expected_output = """
FILE_PATH: test/file/valve.dat
DESC: ['This is first line of description', 'and this is second line of description']
VALVE: QALL
""" + valve_obj.properties['VALVE'].to_string(na_rep='') + '\n\n'

    # Act
    result = valve_obj.__repr__()

    # Assert
    assert result == expected_output
