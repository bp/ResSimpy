import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.NexusRockMethod import NexusRockMethod
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem

@pytest.mark.parametrize("file_contents, expected_rock_properties",
    [(
    """
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    ! Reference Pressure
    PREF 2000.0
    ! Rock Compressibility
    CR 1E-6
    ! Constant Permeability Multiplier
    KP 0.003

    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'CR': 1.e-6, 'PREF': 2000., 'KP': 0.003
          }
    ),
    (
    """
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    COMPR
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'COMPR': ''
          }
    ),
    (
    """
    ENGLISH
    ! Compressibility and ref pressure
    CR 1E-6 PREF 2000.0
    ! Compaction table 
    CMT
    DP   PVMULT TAMULT
    -200 0.79 0.02
    0    0.81 0.05 ! Inline comment
    ! Comment in between rows of table
    300 0.85 0.08
    400 0.9 0.5
    REVERSIBLE

    TOLREV_P 2
    CR_REPRESSURE 2e-6

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'CR': 1.e-6, 'PREF': 2000., 'REVERSIBLE': '', 'TOLREV_P': 2, 'CR_REPRESSURE': 2e-6,
          'CMT': pd.DataFrame({'DP': [-200, 0, 300, 400],
                               'PVMULT': [0.79, 0.81, 0.85, 0.9],
                               'TAMULT': [0.02, 0.05, 0.08, 0.5]
                               })
          }
    ),
    (
    """
    ENGLISH
    ! Compaction table 
    CMT
    P PVMULT
    1500 0.76
    2000 0.81
    3500 0.85
    REVERSIBLE

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'REVERSIBLE': '',
          'CMT': pd.DataFrame({'P': [1500, 2000, 3500],
                               'PVMULT': [0.76, 0.81, 0.85]
                               })
          }
    ),
    (
    """
    ENGLISH
    ! Water-induced rock compaction table 
    WIRCT
    !
    SWINIT 0.10
    DSW PVMULT TAMULT
    0.0 1.0 1.0
    0.02 1.0 1.0
    0.12 0.94 0.40
    0.22 0.88 0.25
    0.32 0.82 0.09
    0.42 0.76 0.09

    ! In the table below, PVMULT is treated as being 1.0 everywhere
    SWINIT 0.50
    DSW TAMULT
    0.02 1.0
    0.12 0.9
    0.35 0.8

    IRREVERSIBLE WIRCTONLY
    TOLREV_SW 0.01

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'IRREVERSIBLE': 'WIRCTONLY', 'TOLREV_SW': 0.01,
          'WIRCT': {'0.10': pd.DataFrame({'DSW': [0.0, 0.02, 0.12, 0.22, 0.32, 0.42],
                                          'PVMULT': [1., 1., 0.94, 0.88, 0.82, 0.76],
                                          'TAMULT': [1., 1., 0.40, 0.25, 0.09, 0.09]
                                          }),
                    '0.50': pd.DataFrame({'DSW': [0.02, 0.12, 0.35],
                                          'TAMULT': [1., 0.9, 0.8]
                                          })
                    }
          }
    ),
    (
    """
    ENGLISH
    ! Compaction table 
    CMT
    P PVMULT
    1500 0.76
    2000 0.81
    3500 0.85
    REVERSIBLE CMTONLY
    TOLREV_P 2.5
    ! Water-induced rock compaction table 
    WIRCT
    !
    SWINIT 0.10
    DSW PVMULT TAMULT
    0.0 1.0 1.0
    0.02 1.0 1.0
    0.12 0.94 0.40
    0.22 0.88 0.25
    0.32 0.82 0.09
    0.42 0.76 0.09

    ! In the table below, PVMULT is treated as being 1.0 everywhere
    SWINIT 0.50
    DSW TAMULT
    0.02 1.0
    0.12 0.9
    0.35 0.8
    IRREVERSIBLE WIRCTONLY
    TOLREV_SW 0.01
    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'REVERSIBLE': 'CMTONLY', 'IRREVERSIBLE': 'WIRCTONLY',
          'TOLREV_P': 2.5, 'TOLREV_SW': 0.01,
          'CMT': pd.DataFrame({'P': [1500, 2000, 3500],
                               'PVMULT': [0.76, 0.81, 0.85]
                               }),
          'WIRCT': {'0.10': pd.DataFrame({'DSW': [0.0, 0.02, 0.12, 0.22, 0.32, 0.42],
                                          'PVMULT': [1., 1., 0.94, 0.88, 0.82, 0.76],
                                          'TAMULT': [1., 1., 0.40, 0.25, 0.09, 0.09]
                                          }),
                    '0.50': pd.DataFrame({'DSW': [0.02, 0.12, 0.35],
                                          'TAMULT': [1., 0.9, 0.8]
                                          })
                    }
          }
    ),
    ], ids=['basic_rock', 'compr_only', 'cmt_dp', 'cmt_p', 'wirct', 'cmt_wirct']
)
def test_read_rock_properties_from_file(mocker, file_contents, expected_rock_properties):
    # Arrange
    rock_obj = NexusRockMethod(file_path='test/file/rock.dat', method_number=1)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    rock_obj.read_properties()
    props = rock_obj.properties

    # Assert
    for key in expected_rock_properties:
        if isinstance(expected_rock_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_rock_properties[key], props[key])
        elif isinstance(expected_rock_properties[key], dict):
            for subkey in expected_rock_properties[key].keys():
                pd.testing.assert_frame_equal(expected_rock_properties[key][subkey], props[key][subkey])
        else:
            assert props[key] == expected_rock_properties[key]


def test_nexus_rock_repr():
    # Arrange
    rock_obj = NexusRockMethod(file_path='test/file/rock.dat', method_number=1)
    rock_obj.properties = {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'REVERSIBLE': '',
                           'CMT': pd.DataFrame({'P': [1500, 2000, 3500],
                                                'PVMULT': [0.76, 0.81, 0.85]
                                                })}
    expected_output = """
FILE_PATH: test/file/rock.dat
UNIT_SYSTEM: ENGLISH
REVERSIBLE
CMT:
""" + rock_obj.properties['CMT'].to_string(na_rep='') + '\n\n'

    # Act
    result = rock_obj.__repr__()

    # Assert
    assert result == expected_output
