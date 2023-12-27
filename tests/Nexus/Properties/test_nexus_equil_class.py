import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.NexusEquilMethod import NexusEquilMethod
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import UnitSystem, SUnits, TemperatureUnits
from ResSimpy.Nexus.NexusEquilMethods import NexusEquilMethods

@pytest.mark.parametrize("file_contents, expected_equil_properties",
    [("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH

    ! This is a comment
    PINIT 3600 DINIT 9035
    GOC 8800 WOC 9950
    PSAT 3600

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PSAT': 3600
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    SUNITS PPM

    ! This is a comment
    PINIT 3600 DINIT 9035
    GOC 8800 WOC 9950
    PSAT 3600
    WATERZONE_NEW_INIT
    LI_FACTOR 0.9
    LI_AUTO_GAS
    AUTOGOC_COMP EQUIL
    OVERREAD SG
    OVERREAD SW
    SALINITY 300000

    INTSAT
    VIP_INIT 3 7 ! Test inline comment

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PSAT': 3600, 'LI_FACTOR': 0.9,
          'WATERZONE_NEW_INIT': '', 'AUTOGOC_COMP': 'EQUIL', 'LI_AUTO_GAS': '',
          'OVERREAD': ['SG', 'SW'], 'SALINITY': 300000, 'INTSAT': '', 'VIP_INIT': '3 7'
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    SUNITS PPM

    ! This is a comment
    PINIT 3600 DINIT 9035
    GOC 8800 WOC 9950
    WOC_PALEO 10000
    PSAT 3600
    SALINITY 300000
    HONOR_GZONE
    HONOR_GASPRESSURE_GWC

    PCADJ_SCALING
    NONEQ

    VIP_INIT ALL

    INTSAT MOBILE SORWMN 0.1
                  SORGMN 0.1
                  SGCMN 0.05

    OVERREAD SW
    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PSAT': 3600, 'SALINITY': 300000,
          'OVERREAD': ['SW'], 'INTSAT': 'MOBILE', 'SORWMN': 0.1, 'SORGMN': 0.1, 'SGCMN': 0.05,
          'HONOR_GZONE': '', 'PCADJ_SCALING': '', 'NONEQ': '', 'WOC_PALEO': 10000., 'VIP_INIT': 'ALL'
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    SUNITS PPM

    ! This is a comment
    PINIT 3600 DINIT 9035
    GOC 8800 WOC 9950
    PSAT 3600
    OVERREAD SG SW PRESSURE
    KEEPSG


    VAITS MOBILE SORWMN 0.1
                 SORGMN 0.1
                 SGCMN 0.05
          VAITS_TOLSG 0.001
          VAITS_TOLSW 1e-4

    POROSITY_INDEPENDENCE

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PSAT': 3600,
          'OVERREAD': ['SG', 'SW', 'PRESSURE'], 'VAITS': 'MOBILE', 'SORWMN': 0.1, 'SORGMN': 0.1, 'SGCMN': 0.05,
          'VAITS_TOLSG': 1e-3, 'VAITS_TOLSW': 1e-4, 'POROSITY_INDEPENDENCE': ''
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    FAHR
    SUNITS PPM

    ! This is a comment
    PINIT 3600 DINIT 9035
    GOC 8800 WOC 9950
    DEPTHVAR
    DEPTH  PSAT    TEMP   SALINITY
    2000.0 1000.0  200.1  1000 ! Inline table comment
    2500.0 1175.0  250.2  2000
    ! comment between table rows
    3000.0 1200.0  300.3  3000
    
    LI_AUTO_GAS

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'TEMP_UNIT': TemperatureUnits.FAHR, 'SUNITS': SUnits.PPM,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'LI_AUTO_GAS': '',
          'DEPTHVAR': pd.DataFrame({'DEPTH': [2000., 2500., 3000.],
                                    'PSAT': [1000., 1175., 1200.],
                                    'TEMP': [200.1, 250.2, 300.3],
                                    'SALINITY': [1000, 2000, 3000]
                                    })
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    PINIT 3600 DINIT 9035
    GOC 8800 WOC 9950
    OILMF
    P1     P2     P3       P4       P5
    0.5627 0.2429 0.096672 0.084232 0.013496

    SEDIMENTATION
    MATCHVIPPRES

    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'SEDIMENTATION': '', 'MATCHVIPPRES': '',
          'OILMF': pd.DataFrame({'P1': [0.5627],
                                 'P2': [0.2429],
                                 'P3': [0.096672],
                                 'P4': [0.084232],
                                 'P5': [0.013496]})
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    FAHR
    SUNITS PPM

    ! This is a comment
    
    COMPOSITION X 50 Y -50
    DEPTH PSAT   TEMP SALINITY C1   C3    C6    C10+
    8000  2302.3 160  10000    0.50 0.03  0.07  0.40
    8540  2302.3 165  15000    0.50 0.03  0.07  0.40
    8740  1800   170  20000    0.40 0.032 0.075 0.492
    PINIT 3600 DINIT 9035 GOC 8800 WOC 9950 PCGOC 0 PCWOC 0 PSAT 3400

    CRINIT
    AUTOGOC_COMP USE_CLOSEST_OIL
    VIP_INIT 3 4 5 7

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH, 'TEMP_UNIT': TemperatureUnits.FAHR, 'SUNITS': SUnits.PPM,
          'DESC': ['This is first line of description', 'and this is second line of description'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PCGOC': 0, 'PCWOC': 0, 'PSAT': 3400,
          'X': 50, 'Y': -50, 'VIP_INIT': '3 4 5 7',
          'CRINIT': '', 'AUTOGOC_COMP': 'USE_CLOSEST_OIL',
          'COMPOSITION': pd.DataFrame({'DEPTH': [8000, 8540, 8740],
                                       'PSAT': [2302.3, 2302.3, 1800.],
                                       'TEMP': [160, 165, 170],
                                       'SALINITY': [10000, 15000, 20000],
                                       'C1': [0.5, 0.5, 0.4],
                                       'C3': [0.03, 0.03, 0.032],
                                       'C6': [0.07, 0.07, 0.075],
                                       'C10+': [0.40, 0.40, 0.492]
                                       })
          }
    ),
    ("""
    DESC This is first line of description >
and continuation for the first line  
    ENGLISH

    ! This is a comment
    PINIT 3600 DINIT 9035
    GOC 8800 WOC 9950
    PSAT 3600

    """, {'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'DESC': ['This is first line of description and continuation for the first line'],
          'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PSAT': 3600
          }
    )
    ], ids=['basic_equil', 'adv_equil', 'intsat_equil', 'vaits_equil', 'depthvar', 'oilmf', 'compvar', 'line_continuation']
)
def test_read_equil_properties_from_file(mocker, file_contents, expected_equil_properties):
    # Arrange
    file_contents_as_list = file_contents.splitlines()
    if '>' in file_contents_as_list[1]:
        file_contents_as_list[1] = file_contents_as_list[1].split('>')[0] + file_contents_as_list[2]
        del file_contents_as_list[2]

    eq_file = NexusFile(location='', file_content_as_list=file_contents_as_list)
    equil_obj = NexusEquilMethod(file=eq_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    equil_obj.read_properties()
    props = equil_obj.properties

    # Assert
    for key in expected_equil_properties:
        if isinstance(expected_equil_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_equil_properties[key], props[key])
        else:
            assert props[key] == expected_equil_properties[key]


def test_nexus_equil_repr():
    # Arrange
    eq_file = NexusFile(location='test/file/equil.dat')
    equil_obj = NexusEquilMethod(file=eq_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    equil_obj.properties = {'PINIT': 3600., 'DINIT': 9035., 'GOC': 8800., 'WOC': 9950., 'PCGOC': 0., 'PCWOC': 0.,
                            'PSAT': 3400., 'X': 50., 'Y': -50., 'VIP_INIT': '3 4 5 7', 'CRINIT': '', 
                            'AUTOGOC_COMP': 'USE_CLOSEST_OIL', 'OVERREAD': ['SG', 'SW', 'PRESSURE'],
                            'VAITS': 'MOBILE', 'SORWMN': 0.1, 'SORGMN': 0.1, 'SGCMN': 0.05,
                            'VAITS_TOLSG': 1.e-3, 'VAITS_TOLSW': 1.e-4, 'POROSITY_INDEPENDENCE': '',
                            'COMPOSITION': pd.DataFrame({'DEPTH': [8000, 8540, 8740],
                                                         'PSAT': [2302.3, 2302.3, 1800.],
                                                         'TEMP': [160, 165, 170],
                                                         'SALINITY': [10000, 15000, 20000],
                                                         'C1': [0.5, 0.5, 0.4],
                                                         'C3': [0.03, 0.03, 0.032],
                                                         'C6': [0.07, 0.07, 0.075],
                                                         'C10+': [0.40, 0.40, 0.492]
                                                         })}
    expected_output = """
FILE_PATH: test/file/equil.dat

PINIT 3600.0
DINIT 9035.0
GOC 8800.0
WOC 9950.0
PCGOC 0.0
PCWOC 0.0
PSAT 3400.0
VIP_INIT 3 4 5 7
CRINIT
AUTOGOC_COMP USE_CLOSEST_OIL
OVERREAD SG SW PRESSURE
VAITS
    MOBILE
        SORWMN 0.1
        SORGMN 0.1
        SGCMN 0.05
    VAITS_TOLSG 0.001
    VAITS_TOLSW 0.0001
POROSITY_INDEPENDENCE
COMPOSITION X 50.0 Y -50.0
""" + equil_obj.properties['COMPOSITION'].to_string(na_rep='', index=False) + '\n\n'

    # Act
    result = equil_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_equil_methods_repr():
    # Arrange
    eq_file = NexusFile(location='test/file/equil.dat')
    properties = {'UNIT_SYSTEM': UnitSystem.ENGLISH,
                  'DESC': ['This is first line of description', 'and this is second line of description'],
                  'PINIT': 3600, 'DINIT': 9035, 'GOC': 8800, 'WOC': 9950, 'PSAT': 3600
                  }
    equil_obj = NexusEquilMethod(file=eq_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                 properties=properties)
    equil_methods_obj = NexusEquilMethods(model_unit_system=UnitSystem.ENGLISH, inputs={1: equil_obj,
                                                                                        2: equil_obj})
    expected_output = """
--------------------------------
EQUIL method 1
--------------------------------

FILE_PATH: test/file/equil.dat

ENGLISH
DESC This is first line of description
DESC and this is second line of description
PINIT 3600
DINIT 9035
GOC 8800
WOC 9950
PSAT 3600



--------------------------------
EQUIL method 2
--------------------------------

FILE_PATH: test/file/equil.dat

ENGLISH
DESC This is first line of description
DESC and this is second line of description
PINIT 3600
DINIT 9035
GOC 8800
WOC 9950
PSAT 3600


"""

    # Act
    result = equil_methods_obj.__repr__()

    # Assert
    assert result == expected_output
