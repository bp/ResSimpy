from enum import Enum
import numpy as np
import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

from ResSimpy.Nexus.DataModels.NexusSeparatorMethod import NexusSeparatorMethod
from ResSimpy.Enums.UnitsEnum import UnitSystem, TemperatureUnits
from ResSimpy.Nexus.NexusSeparatorMethods import NexusSeparatorMethods

@pytest.mark.parametrize("file_contents, expected_separator_properties",
    [("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    FAHR

    ! This is a comment
    TEMP PRES METHOD
    ! This is another comment
    150.0 500.0 1
    60.0 14.7 2

    WATERMETHOD 1
    """, {'SEPARATOR_TYPE': 'EOS', 'WATERMETHOD': 1,
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'TEMP_UNIT': TemperatureUnits.FAHR,
          'DESC': ['This is first line of description',
                   'and this is second line of description'],
          'SEPARATOR_TABLE': pd.DataFrame({'TEMP': [150.0, 60.0],
                                           'PRES': [500.0, 14.7],
                                           'METHOD': [1, 2]
                                          }),
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    ! This is a comment
    STAGE METHOD PRES  TEMP IDL1 IDL2 IDV1 IDV2 FDL1 FDV1
      1     1    500.  150.  2    NA   GAS   NA   1.   1. ! comment with WATERMETHOD
      ! comment within table
      2     2     14.7  60.  OIL  NA  VENT   NA   1.   1.

    WATERMETHOD 1
    """, {'SEPARATOR_TYPE': 'EOS', 'WATERMETHOD': 1,
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                             'and this is second line of description'
                                             ],
          'SEPARATOR_TABLE': pd.DataFrame({'STAGE': [1, 2],
                                           'METHOD': [1, 2],
                                           'PRES': [500.0, 14.7],
                                           'TEMP': [150.0, 60.0],
                                           'IDL1': ['2', 'OIL'],
                                           'IDL2': [np.nan, np.nan],  
                                           'IDV1': ['GAS', 'VENT'],
                                           'IDV2': [np.nan, np.nan],
                                           'FDL1': [1., 1.],
                                           'FDV1': [1., 1.]    
                                          }),
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    ! This is a comment
    KEYCPTLIST C8 C10 PS1 PS2

    PRES_STD 20
    TEMP_STD 100
    EOSMETHOD 1
    WATERMETHOD 5
    
    RECFAC_TABLE
    KEYCPTMF 0 0.25 0.50 0.75 0.95
    C1 0.005 0.012 0.031 0.049 0.05
    C2 0.001 0.002 0.002 0.003 0.004
    C3 0.008 0.020 0.052 0.075 0.08
    C4 0.030 0.050 0.078 0.11 0.15
    C5 0.090 0.130 0.22 0.44 0.55
    C7 1.0 1.0 1.0 1.0 1.0
    C10 1.0 1.0 1.0 1.0 1.0
    ENDRECFAC_TABLE

    """, {'SEPARATOR_TYPE': 'GASPLANT', 'WATERMETHOD': 5, 'PRES_STD': 20., 'TEMP_STD': 100.,
          'EOSMETHOD': 1, 'KEYCPTLIST': ['C8', 'C10', 'PS1', 'PS2'],
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                             'and this is second line of description'
                                             ],
          'SEPARATOR_TABLE': pd.DataFrame({'KEYCPTMF': ['C1', 'C2', 'C3', 'C4', 'C5', 'C7', 'C10'],
                                           '0': [0.005, 0.001, 0.008, 0.030, 0.090, 1.0, 1.0],
                                           '0.25': [0.012, 0.002, 0.020, 0.050, 0.130, 1.0, 1.0],
                                           '0.50': [0.031, 0.002, 0.052, 0.078, 0.22, 1.0, 1.0],
                                           '0.75': [0.049, 0.003, 0.075, 0.11, 0.44, 1.0, 1.0],
                                           '0.95': [0.05, 0.004, 0.08, 0.15, 0.55, 1.0, 1.0]
                                          }),
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    ! This is a comment
    BOSEP

    MWOIL 180.
    MWGAS  10.
    ZOIL 0.009
    
    STAGE   KVOIL       KVGAS    IDL1  FDL1  IDV1  FDV1
    1    0.60e-10    0.81e+10     OIL   1.0   GAS   1.0


    """, {'SEPARATOR_TYPE': 'BLACKOIL', 'MWOIL': 180., 'MWGAS': 10., 'ZOIL': 9.e-3,
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                             'and this is second line of description'
                                             ],
          'SEPARATOR_TABLE': pd.DataFrame({'STAGE': [1],
                                           'KVOIL': [6.0e-11],
                                           'KVGAS': [8.1e9],
                                           'IDL1': ['OIL'],
                                           'FDL1': [1.0],
                                           'IDV1': ['GAS'],
                                           'FDV1': [1.0]
                                          }),
          }
    )
    ], ids=['basic eos separator', 'complex eos separator', 'gas plant', 'black oil separator']
)
def test_read_separator_properties_from_file(mocker, file_contents, expected_separator_properties):
    # Arrange
    sep_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    sep_obj = NexusSeparatorMethod(file=sep_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    sep_obj.read_properties()
    props = sep_obj.properties

    # Assert
    assert sep_obj.separator_type == expected_separator_properties['SEPARATOR_TYPE']
    for key in [key for key in expected_separator_properties.keys() if key not in ['SEPARATOR_TYPE']]:
        if isinstance(expected_separator_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_separator_properties[key], props[key])
        else:
            assert expected_separator_properties[key] == props[key]


def test_nexus_eos_separator_repr():
    # Arrange
    sep_file = NexusFile(location='test/file/separator.dat')
    sep_obj = NexusSeparatorMethod(file=sep_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    sep_obj.separator_type = 'EOS'
    sep_obj.properties = {'DESC': ['This is first line of description',
                                   'and this is second line of description'
                                   ],
                          'UNIT_SYSTEM': UnitSystem.ENGLISH,
                          'TEMP_UNIT': TemperatureUnits.FAHR,
                          'SEPARATOR_TABLE': pd.DataFrame({'STAGE': [1, 2],
                                                           'METHOD': [1, 2],
                                                           'PRES': [500.0, 14.7],
                                                           'TEMP': [150.0, 60.0],
                                                           'IDL1': ['2', 'OIL'],
                                                           'IDL2': [np.nan, np.nan],  
                                                           'IDV1': ['GAS', 'VENT'],
                                                           'IDV2': [np.nan, np.nan],
                                                           'FDL1': [1., 1.],
                                                           'FDV1': [1., 1.]
                                                           }),
                          'WATERMETHOD': 1
          }
    expected_output = """
FILE_PATH: test/file/separator.dat

DESC This is first line of description
DESC and this is second line of description
ENGLISH
FAHR
""" + sep_obj.properties['SEPARATOR_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WATERMETHOD 1
""" 

    # Act
    result = sep_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_gas_plant_separator_repr():
    # Arrange
    sep_file = NexusFile(location='test/file/separator.dat')
    sep_obj = NexusSeparatorMethod(file=sep_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    sep_obj.separator_type = 'GASPLANT'
    sep_obj.properties = {'DESC': ['This is first line of description',
                                   'and this is second line of description'],
                          'UNIT_SYSTEM': UnitSystem.ENGLISH,
                          'TEMP_UNIT': TemperatureUnits.FAHR,
                          'KEYCPTLIST': ['C8', 'C10', 'PS1', 'PS2'],
                          'PRES_STD': 20., 'TEMP_STD': 100.,
                          'EOSMETHOD': 1, 'WATERMETHOD': 5,
                          'SEPARATOR_TABLE': pd.DataFrame({'KEYCPTMF': ['C1', 'C2', 'C3', 'C4', 'C5', 'C7', 'C10'],
                                                           '0': [0.005, 0.001, 0.008, 0.030, 0.090, 1.0, 1.0],
                                                           '0.25': [0.012, 0.002, 0.020, 0.050, 0.130, 1.0, 1.0],
                                                           '0.50': [0.031, 0.002, 0.052, 0.078, 0.22, 1.0, 1.0],
                                                           '0.75': [0.049, 0.003, 0.075, 0.11, 0.44, 1.0, 1.0],
                                                           '0.95': [0.05, 0.004, 0.08, 0.15, 0.55, 1.0, 1.0]
                                                           }),
          }
    expected_output = """
FILE_PATH: test/file/separator.dat

DESC This is first line of description
DESC and this is second line of description
ENGLISH
FAHR
KEYCPTLIST C8 C10 PS1 PS2
PRES_STD 20.0
TEMP_STD 100.0
EOSMETHOD 1
WATERMETHOD 5
RECFAC_TABLE
""" + sep_obj.properties['SEPARATOR_TABLE'].to_string(na_rep='', index=False) + \
"""
ENDRECFAC_TABLE

"""

    # Act
    result = sep_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_blackoil_separator_repr():
    # Arrange
    sep_file = NexusFile(location='test/file/separator.dat')
    sep_obj = NexusSeparatorMethod(file=sep_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    sep_obj.separator_type = 'BLACKOIL'
    sep_obj.properties = {'DESC': ['This is first line of description',
                                   'and this is second line of description'
                                   ],
                          'UNIT_SYSTEM': UnitSystem.ENGLISH,
                          'TEMP_UNIT': TemperatureUnits.FAHR,
                          'BOSEP': '', 'MWOIL': 180., 'MWGAS': 10., 'ZOIL': 0.009,
                          'SEPARATOR_TABLE': pd.DataFrame({'STAGE': [1],
                                                           'KVOIL': [6.0e-11],
                                                           'KVGAS': [8.1e9],
                                                           'IDL1': ['OIL'],
                                                           'FDL1': [1.0],
                                                           'IDV1': ['GAS'],
                                                           'FDV1': [1.0]
                                                           })
          }
    expected_output = """
FILE_PATH: test/file/separator.dat

DESC This is first line of description
DESC and this is second line of description
ENGLISH
FAHR
BOSEP
MWOIL 180.0
MWGAS 10.0
ZOIL 0.009
""" + sep_obj.properties['SEPARATOR_TABLE'].to_string(na_rep='', index=False) + '\n\n'

    # Act
    result = sep_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_separator_methods_repr():
    # Arrange
    sep_file = NexusFile(location='test/file/separator.dat')
    properties = {'DESC': ['This is first line of description',
                           'and this is second line of description'
                           ],
                  'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'TEMP_UNIT': TemperatureUnits.FAHR,
                  'SEPARATOR_TABLE': pd.DataFrame({'STAGE': [1, 2],
                                                   'METHOD': [1, 2],
                                                   'PRES': [500.0, 14.7],
                                                   'TEMP': [150.0, 60.0],
                                                   'IDL1': ['2', 'OIL'],
                                                   'IDL2': [np.nan, np.nan],  
                                                   'IDV1': ['GAS', 'VENT'],
                                                   'IDV2': [np.nan, np.nan],
                                                   'FDL1': [1., 1.],
                                                   'FDV1': [1., 1.]
                                                   }),
                  'WATERMETHOD': 1}
    sep_obj = NexusSeparatorMethod(file=sep_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                   properties=properties, separator_type='EOS')
    sep_methods_obj = NexusSeparatorMethods(model_unit_system=UnitSystem.ENGLISH, inputs={1: sep_obj,
                                                                                          2: sep_obj})
    expected_output = """
--------------------------------
SEPARATOR method 1
--------------------------------

SEPARATOR_TYPE: EOS

FILE_PATH: test/file/separator.dat

DESC This is first line of description
DESC and this is second line of description
ENGLISH
FAHR
""" + properties['SEPARATOR_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WATERMETHOD 1


--------------------------------
SEPARATOR method 2
--------------------------------

SEPARATOR_TYPE: EOS

FILE_PATH: test/file/separator.dat

DESC This is first line of description
DESC and this is second line of description
ENGLISH
FAHR
""" + properties['SEPARATOR_TABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WATERMETHOD 1

"""

    # Act
    result = sep_methods_obj.__repr__()

    # Assert
    assert result == expected_output
