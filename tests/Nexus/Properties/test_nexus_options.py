import numpy as np
import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

from ResSimpy.Nexus.DataModels.NexusOptions import NexusOptions
from ResSimpy.Enums.UnitsEnum import UnitSystem


@pytest.mark.parametrize("file_contents, expected_options",
                         [("""
    DESC Simulation Options

    ENGLISH

    ! Comment
    PSTD ALL 14.7      !  comment ! standard pressure

    TSTD 60 ! std temp
    ! Another comment

    RES_TEMP 200
    DEF_DATUM 8000.
    """, {'DESC': ['Simulation Options'], 'UNIT_SYSTEM': UnitSystem.ENGLISH,
                             'PSTD': 14.7, 'TSTD': 60.0, 'RES_TEMP': 200.0,
                             'DEF_DATUM': 8000.0
          }
                             ), ("""
    DESC Simulation Options

    ENGLISH

    ! Comment
    PSTD 14.7      !  comment ! standard pressure

    TSTD 60 ! std temp
    ! Another comment

    RES_TEMP 200

    IRF_REPORT
    Zoltan

    BOUNDARY_FLUXIN_SECTORS 1 2 3 4 5

    REGDATA Injection_regions
    NAME NUMBER IBAT
    Reg1 1 2
    Reg2 2 2
    ENDREGDATA

    REGDATA Fruit_regions
    NUMBER  NAME
    1       Apple
    2       Grape
    3       Orange
    ENDREGDATA

    GLOBAL_METHOD_OVERRIDES
        STONE2
        NONEQ OFF
        NOCHK_SAL_TEMP
    ENDGLOBAL_METHOD_OVERRIDES
    """, {'DESC': ['Simulation Options'],
                                 'UNIT_SYSTEM': UnitSystem.ENGLISH,
                                 'PSTD': 14.7,
                                 'TSTD': 60.0,
                                 'RES_TEMP': 200.0,
                                 'IRF_REPORT': '', 'ZOLTAN': '',
                                 'BOUNDARY_FLUXIN_SECTORS': np.array([1, 2, 3, 4, 5]),
                                 'REGDATA': {
                                     'Injection_regions': pd.DataFrame({'NAME': ['Reg1', 'Reg2'],
                                                                        'NUMBER': [1, 2],
                                                                        'IBAT': [2, 2]
                                                                        }),
                                     'Fruit_regions': pd.DataFrame({'NUMBER': [1, 2, 3],
                                                                    'NAME': ['Apple', 'Grape', 'Orange']
                                                                    })
                                             },
          'STONE2': '', 'NONEQ': 'OFF', 'NOCHK_SAL_TEMP': ''}
                             )
                             ], ids=['basic_options', 'opts_w_regdata']
)
def test_read_options_from_file(mocker, file_contents, expected_options):
    # Arrange
    opts_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    opts_obj = NexusOptions(file=opts_file, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    opts_obj.load_nexus_options()
    props = opts_obj.properties

    # Assert
    for key in expected_options:
        if isinstance(expected_options[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_options[key], props[key])
        elif isinstance(expected_options[key], np.ndarray):
            np.testing.assert_array_equal(expected_options[key], props[key])
        elif isinstance(expected_options[key], dict):
            for subkey in expected_options[key]:
                if isinstance(expected_options[key][subkey], pd.DataFrame):
                    pd.testing.assert_frame_equal(expected_options[key][subkey], props[key][subkey])
                else:
                    assert props[key][subkey] == expected_options[key][subkey]
        else:
            assert props[key] == expected_options[key]


def test_nexus_options_repr():
    # Arrange
    opts_file = NexusFile(location='test/file/options.dat')
    opts_obj = NexusOptions(file=opts_file, model_unit_system=UnitSystem.ENGLISH)
    opts_obj.properties = {'DESC': ['Simulation Options'],
                           'UNIT_SYSTEM': UnitSystem.ENGLISH,
                           'PSTD': 14.7,
                           'TSTD': 60.0,
                           'RES_TEMP': 200.0,
                           'IRF_REPORT': '', 'ZOLTAN': '',
                           'BOUNDARY_FLUXIN_SECTORS': np.array([1, 2, 3, 4, 5]),
                           'REGDATA': {
                               'Injection_regions': pd.DataFrame({'NAME': ['Reg1', 'Reg2'],
                                                                  'NUMBER': [1, 2],
                                                                  'IBAT': [2, 2]
                                                                  }),
                               'Fruit_regions': pd.DataFrame({'NUMBER': [1, 2, 3],
                                                              'NAME': ['Apple', 'Grape', 'Orange']
                                                              })
                                        },
          'STONE2': '', 'NONEQ': 'OFF', 'NOCHK_SAL_TEMP': ''
                           }
    expected_output = """
FILE_PATH: test/file/options.dat

DESC Simulation Options
ENGLISH
PSTD 14.7
TSTD 60.0
RES_TEMP 200.0
IRF_REPORT
ZOLTAN
BOUNDARY_FLUXIN_SECTORS 1 2 3 4 5

REGDATA Injection_regions
NAME  NUMBER  IBAT
Reg1       1     2
Reg2       2     2
ENDREGDATA

REGDATA Fruit_regions
 NUMBER   NAME
      1  Apple
      2  Grape
      3 Orange
ENDREGDATA

GLOBAL_METHOD_OVERRIDES
STONE2
NONEQ OFF
NOCHK_SAL_TEMP
ENDGLOBAL_METHOD_OVERRIDES

"""
    # Act
    result = opts_obj.__repr__()

    # Assert
    assert result == expected_output


@pytest.mark.parametrize("region_name, expected_output",[
    ('Reg1', 1),
    ('Reg2', 2),
    ('Reg3', -1),
    ('GrApE', 22),
])
def test_look_up_region_number_by_name(region_name, expected_output):
    # Arrange
    opts_file = NexusFile(location='test/file/options.dat')
    opts_obj = NexusOptions(file=opts_file, model_unit_system=UnitSystem.ENGLISH)
    opts_obj.properties = {'DESC': ['Simulation Options'],
                           'UNIT_SYSTEM': UnitSystem.ENGLISH,
                           'PSTD': 14.7,
                           'TSTD': 60.0,
                           'RES_TEMP': 200.0,
                           'REGDATA': {
                               'Injection_regions': pd.DataFrame({'NAME': ['Reg1', 'Reg2'],
                                                                  'NUMBER': [1, 2],
                                                                  'IBAT': [2, 2]
                                                                  }),
                               'Fruit_regions': pd.DataFrame({'NUMBER': [10, 22, 33, 44],
                                                              'NAME': ['Apple', 'Grape', 'Orange', 'Reg1']
                                                              })}
                           }
    # Act
    result = opts_obj.look_up_region_number_by_name(region_name)
    
    # Assert
    assert result == expected_output

