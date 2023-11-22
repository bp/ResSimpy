import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

from ResSimpy.Nexus.DataModels.NexusGasliftMethod import NexusGasliftMethod
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusGasliftMethods import NexusGasliftMethods

@pytest.mark.parametrize("file_contents, expected_gaslift_properties",
    [(
    """
    DESC Optimal Gaslift Data

    ENGLISH

    ! Comment
    WCUT 0.0 0.2 0.4      !  comment ! water cut
    QLIQ 1000 3500
    PRESSURE 2500 4500 ! No GOR used
    IPRES IWCUT IQLIQ GLR
    1 1 1 0.8
    1 1 2 0.7
    1 2 1 0.9
    1 2 2 0.8 ! Comment at end of table line

    ! Comment with QLIQ keyword in the middle of table
    1 3 1 1.0
    1 3 2 0.9
    2 1 1 0.5
    2 1 2 0.4
    2 2 1 0.6
    2 2 2 0.5
    2 3 1 0.7
    2 3 2 0.6

    """, {'DESC': ['Optimal Gaslift Data'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'WCUT': '0.0 0.2 0.4',
          'QLIQ': '1000 3500',
          'PRESSURE': '2500 4500',
          'GL_TABLE': pd.DataFrame({'IPRES': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                    'IWCUT': [1, 1, 2, 2, 3, 3, 1, 1, 2, 2, 3, 3],
                                    'IQLIQ': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                                    'GLR': [0.8, 0.7, 0.9, 0.8, 1, 0.9, 0.5, 0.4, 0.6, 0.5, 0.7, 0.6]
                                    })
          }
    )
    ], ids=['basic_gaslift']
)
def test_read_gaslift_properties_from_file(mocker, file_contents, expected_gaslift_properties):
    # Arrange
    gl_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    gaslift_obj = NexusGasliftMethod(file=gl_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    gaslift_obj.read_properties()
    props = gaslift_obj.properties

    # Assert
    for key in expected_gaslift_properties:
        if isinstance(expected_gaslift_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_gaslift_properties[key], props[key])
        else:
            assert props[key] == expected_gaslift_properties[key]


def test_nexus_gaslift_repr():
    # Arrange
    gl_file = NexusFile(location='test/file/gaslift.dat')
    gaslift_obj = NexusGasliftMethod(file=gl_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    gaslift_obj.properties = {'DESC': ['Optimal Gaslift Data'],
                              'UNIT_SYSTEM': UnitSystem.ENGLISH,
                              'WCUT': '0.0 0.2 0.4',
                              'QLIQ': '1000 3500',
                              'PRESSURE': '2500 4500',
                              'GL_TABLE': pd.DataFrame({'IPRES': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                                        'IWCUT': [1, 1, 2, 2, 3, 3, 1, 1, 2, 2, 3, 3],
                                                        'IQLIQ': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                                                        'GLR': [0.8, 0.7, 0.9, 0.8, 1,   0.9,
                                                                0.5, 0.4, 0.6, 0.5, 0.7, 0.6]
                                                        })}
    expected_output = """
FILE_PATH: test/file/gaslift.dat

DESC Optimal Gaslift Data
ENGLISH
WCUT 0.0 0.2 0.4
QLIQ 1000 3500
PRESSURE 2500 4500
""" + gaslift_obj.properties['GL_TABLE'].to_string(na_rep='', index=False) + '\n\n'

    # Act
    result = gaslift_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_gaslift_methods_repr():
    # Arrange
    gl_file = NexusFile(location='test/file/gaslift.dat')
    properties = {'DESC': ['Optimal Gaslift Data'],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'WCUT': '0.0 0.2 0.4',
                  'QLIQ': '1000 3500',
                  'PRESSURE': '2500 4500',
                  'GL_TABLE': pd.DataFrame({'IPRES': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                            'IWCUT': [1, 1, 2, 2, 3, 3, 1, 1, 2, 2, 3, 3],
                                            'IQLIQ': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
                                            'GLR': [0.8, 0.7, 0.9, 0.8, 1,   0.9,
                                                    0.5, 0.4, 0.6, 0.5, 0.7, 0.6]
                                            })
                  }
    gl_obj = NexusGasliftMethod(file=gl_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                properties=properties)
    gl_methods_obj = NexusGasliftMethods(model_unit_system=UnitSystem.ENGLISH, inputs={1: gl_obj, 2: gl_obj})
    expected_output = """
--------------------------------
GASLIFT method 1
--------------------------------

FILE_PATH: test/file/gaslift.dat

DESC Optimal Gaslift Data
ENGLISH
WCUT 0.0 0.2 0.4
QLIQ 1000 3500
PRESSURE 2500 4500
""" + properties['GL_TABLE'].to_string(na_rep='', index=False) + '\n\n\n' + """
--------------------------------
GASLIFT method 2
--------------------------------

FILE_PATH: test/file/gaslift.dat

DESC Optimal Gaslift Data
ENGLISH
WCUT 0.0 0.2 0.4
QLIQ 1000 3500
PRESSURE 2500 4500
""" + properties['GL_TABLE'].to_string(na_rep='', index=False) + '\n\n\n'

    # Act
    result = gl_methods_obj.__repr__()

    # Assert
    assert result == expected_output
