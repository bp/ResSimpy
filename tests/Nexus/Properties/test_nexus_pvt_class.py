from enum import Enum
import numpy as np
import pandas as pd
import pytest
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

from ResSimpy.Nexus.DataModels.NexusPVTMethod import NexusPVTMethod
from ResSimpy.Enums.UnitsEnum import UnitSystem, TemperatureUnits
from ResSimpy.Nexus.NexusPVTMethods import NexusPVTMethods



@pytest.mark.parametrize("file_contents, expected_pvt_properties",
    [("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    
    BLACKOIL API 30.0 SPECG 0.6
    
    ! This is a comment
    SATURATED
    ! Comment number 2
    PRES BO BG RS VO VG
    14.7 1.05 225.0 0.005 3.93 0.0105

    115. 1.08 25.0 0.045 2.78 0.0109
    ! This is a comment in a table
    2515 1.25 1.089 0.505 0.99 0.0193 ! VIP 
    3515 1.33 0.787 0.69 0.79 0.0193
    
    UNSATOIL PSAT 2000.0
    PRES BO VO
    2515 1.25 0.99
    3515 1.24 0.98
    """, {'PVT_TYPE': 'BLACKOIL', 'API': 30.0, 'SPECG': 0.6,
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                             'and this is second line of description'
                                             ],
          'SATURATED': pd.DataFrame({'PRES': [14.7, 115., 2515, 3515],
                                     'BO': [1.05, 1.08, 1.25, 1.33],
                                     'BG': [225, 25, 1.089, 0.787],
                                     'RS': [0.005, 0.045, 0.505, 0.69],
                                     'VO': [3.93, 2.78, 0.99, 0.79],
                                     'VG': [0.0105, 0.0109, 0.0193, 0.0193]
                                     }),
          'UNSATOIL_PSAT': {'2000.0': pd.DataFrame({'PRES': [2515, 3515],
                                                    'BO': [1.25, 1.24],
                                                    'VO': [0.99, 0.98]
                                                    })
                            }
          }), 
    ("""
    BLACKOIL API 30.0 SPECG 0.6
    
    OIL
    PRES BO RS VO
    14.7 1.05 0.005 3.93
    115. 1.08 0.045 2.78
    2515 1.25 0.505 0.99
    3515 1.33 0.69 0.79

    GAS
    PRES BG vg
    14.7 225.0 0.0105
    115. 25.0 0.0109
    2515 1.089 0.0193
    3515 0.787 0.0193
    
    UNSATOIL RSSAT 0.5
    PRES BO VO
    2515 1.25 0.99
    3515 1.24 0.98
    """, {'PVT_TYPE': 'BLACKOIL', 'API': 30.0, 'SPECG': 0.6,
          'OIL': pd.DataFrame({'PRES': [14.7, 115., 2515, 3515],
                                'BO': [1.05, 1.08, 1.25, 1.33],
                                'RS': [0.005, 0.045, 0.505, 0.69],
                                'VO': [3.93, 2.78, 0.99, 0.79],
                                }),
          'GAS': pd.DataFrame({'PRES': [14.7, 115., 2515, 3515],
                                'BG': [225, 25, 1.089, 0.787],
                                'VG': [0.0105, 0.0109, 0.0193, 0.0193]
                                }),
          'UNSATOIL_RSSAT': {'0.5': pd.DataFrame({'PRES': [2515, 3515],
                                                    'BO': [1.25, 1.24],
                                                    'VO': [0.99, 0.98]
                                                    })
                            }
          }), 
    ("""
    WATEROIL DENOIL 55.185 ! API 28.5
    
    ENGLISH

    OIL
    PRES BO RS VO
    14.7 1.05 0.005 3.93
    115. 1.08 0.045 2.78
    2515 1.25 0.505 0.99
    3515 1.33 0.69 0.79
    """, {'PVT_TYPE': 'WATEROIL', 'DENOIL': 55.185,
          'UNIT_SYSTEM': UnitSystem.ENGLISH,
          'OIL': pd.DataFrame({'PRES': [14.7, 115., 2515, 3515],
                                'BO': [1.05, 1.08, 1.25, 1.33],
                                'RS': [0.005, 0.045, 0.505, 0.69],
                                'VO': [3.93, 2.78, 0.99, 0.79],
                                })
          }),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ENGLISH
    
    BLACKOIL API 30.0 SPECG 0.6
    
    ! This is a comment
    SATURATED
    ! Comment number 2
    PRES BO BG RS VO VG
    14.7 1.05 225.0 0.005 3.93 0.0105

    115. 1.08 25.0 0.045 2.78 0.0109
    ! This is a comment in a table
    2515 1.25 1.089 0.505 0.99 0.0193 ! This is an inline comment, in a table
    3515 1.33 0.787 0.69 0.79 0.0193
    
    UNSATOIL PSAT 2000.0
    PRES BO VO
    2515 1.25 0.99
    3515 1.24 0.98

    UNSATGAS PRES 3515.0
    RV BG VG
    0.0 0.787 0.0193
    
    """, {'PVT_TYPE': 'BLACKOIL', 'API': 30.0, 'SPECG': 0.6,
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                             'and this is second line of description'
                                             ],
          'SATURATED': pd.DataFrame({'PRES': [14.7, 115., 2515, 3515],
                                     'BO': [1.05, 1.08, 1.25, 1.33],
                                     'BG': [225, 25, 1.089, 0.787],
                                     'RS': [0.005, 0.045, 0.505, 0.69],
                                     'VO': [3.93, 2.78, 0.99, 0.79],
                                     'VG': [0.0105, 0.0109, 0.0193, 0.0193]
                                     }),
          'UNSATOIL_PSAT': {'2000.0': pd.DataFrame({'PRES': [2515, 3515],
                                                    'BO': [1.25, 1.24],
                                                    'VO': [0.99, 0.98]
                                                    })},
          'UNSATGAS_PRES': {'3515.0': pd.DataFrame({'RV': [0.0],
                                                     'BG': [0.787],
                                                     'VG': [0.0193]
                                                     })}
          }),
    ("""
    GASWATER SPECG 0.6
    
    GAS
    PRES BG VG
    14.7 225.0 0.0105
    115. 25.0 0.0109
    2515 1.089 0.0193
    3515 0.787 0.0193
    
    """, {'PVT_TYPE': 'GASWATER', 'SPECG': 0.6,
          'GAS': pd.DataFrame({'PRES': [14.7, 115., 2515, 3515],
                                'BG': [225, 25, 1.089, 0.787],
                                'VG': [0.0105, 0.0109, 0.0193, 0.0193]
                                }),
          }),
    ("""
      DESC SPE 5

      EOS NHC 6
      COMPONENTS C1 C3 C6 C10 C15 C20

      ENGLISH FAHR
      TEMP 160.0

      PROPS
      COMPONENT MOLWT OMEGAA OMEGAB TC PC VC acentr
      C1 16.04 0.4572355 0.0777961 -116.67 667.8 1.598 0.0130
      C3 44.01 0.4572355 0.0777961 206.03 616.3 3.129 0.1524
      C6 86.18 0.4572355 0.0777961 453.73 436.99 5.922 0.3007
      C10 142.29 0.4572355 0.0777961 652.13 304.0 10.09 0.4885
      C15 206.00 0.4572355 0.0777961 810.33 200.0 16.69 0.6500
      C20 282.00 0.4572355 0.0777961 920.33 162.0 21.48 0.8500
      ENDPROPS
      ! This is a random test comment
      BINA
      COMPONENT C1 C3 C6 C10 C15
      C3 0.0
      C6 0.0 0.0
      C10 0.0 0.0 0.0
      C15 0.05 0.005 0.0 0.0
      C20 0.05 0.005 0.0 0.0 0.0
      ENDBINA

      EOSOPTIONS PR
                 ZGIBBS
                 FLASH_GIBBS_ON
                 STKATZOFF
                 CAPILLARYFLASH
                 FUGERR 6
                 TRANSITION
                             NEIGHBOR
                 PHASEID
                             FLASH
                 TRANS_OPTIMIZATION TDELP 1 TDELZ 0.001
                 TRANS_TEST GIBBS
                 TOL 1.0e-4
                 TOLSS 1.0e-2
                 VISPE
                        PEDTUNE
                        INDEX    COEFF
                        1        1.0
                        2        1.0
                        3        1.847
                        4        .5173
                        5        7.378e-3
                        6        3.1e-2
                        ENDPEDTUNE
    
    """, {'PVT_TYPE': 'EOS', 'UNIT_SYSTEM': UnitSystem.ENGLISH, 'TEMP_UNIT': TemperatureUnits.FAHR,
          'DESC': ['SPE 5'], 'TEMP': 160.0, 'NHC': 6, 'COMPONENTS': ['C1', 'C3', 'C6', 'C10', 'C15', 'C20'],
          'EOSOPTIONS': {'EOS_METHOD': 'PR',
                         'EOS_OPT_PRIMARY_LIST': ['ZGIBBS', 'FLASH_GIBBS_ON', 'STKATZOFF', 'CAPILLARYFLASH', 'VISPE'],
                         'FUGERR': 6,
                         'TRANSITION': 'NEIGHBOR',
                         'TRANS_OPTIMIZATION': {'TDELZ': 1e-3, 'TDELP': 1.0},
                         'TRANS_TEST': 'GIBBS',
                         'TOL': 0.0001,
                         'TOLSS': 0.01,
                         'PHASEID': 'FLASH'
                         },
          'PROPS': pd.DataFrame({'COMPONENT': ['C1', 'C3', 'C6', 'C10', 'C15', 'C20'],
                                 'MOLWT': [16.04, 44.01, 86.18, 142.29, 206, 282],
                                 'OMEGAA': [0.4572355, 0.4572355, 0.4572355, 0.4572355, 0.4572355, 0.4572355],
                                 'OMEGAB': [0.0777961, 0.0777961, 0.0777961, 0.0777961, 0.0777961, 0.0777961],
                                 'TC': [-116.67, 206.03, 453.73, 652.13, 810.33, 920.33],
                                 'PC': [667.8, 616.3, 436.99, 304, 200, 162],
                                 'VC': [1.598, 3.129, 5.922, 10.09, 16.69, 21.48],
                                 'ACENTR': [0.013, 0.1524, 0.3007, 0.4885, 0.65, 0.85]
                                 }),
          'BINA': pd.DataFrame({'COMPONENT': ['C3', 'C6', 'C10', 'C15', 'C20'],
                                'C1':  [0.0,    0.0,    0.0,    0.05,   0.05],
                                'C3':  [np.nan, 0.0,    0.0,    0.005,  0.005],
                                'C6':  [np.nan, np.nan, 0.0,    0.0,    0.0],
                                'C10': [np.nan, np.nan, np.nan, 0.0,    0.0],
                                'C15': [np.nan, np.nan, np.nan, np.nan, 0.0]
                                }),
          'PEDTUNE': pd.DataFrame({'INDEX': [1, 2, 3, 4, 5, 6],
                                   'COEFF': [1, 1, 1.847, 0.5173, 0.007378, 0.031]
                                   })
          }),
    ("""
      DESC EOS EXAMPLE WITH NO TABLES

      EOS NHC 5
      COMPONENTS C1 C2 C3-4 C5-6 C7+
      LABEL Test1
      TEMP 520.0

      ENGLISH RANKINE

      EOSOPTIONS PR
                 PHASEID
                     DENSITY THRESHOLD 40
                 ALPHAMU 0.01
                 ZGIBBS
                 CAPILLARYFLASH
                 LI_FACT 0.9
                 LBC1 0.1023
                 LBC2 0.02336
                 LBC3 0.05853
                 LBC4 -0.04076
                 LBC5 0.009332
                 TRANSITION DELTA TCRIT 0.15 TDELZ 0.001
                 TRANS_TEST INCRP PHASEFRAC 0.05
                 VISPE
    
    """, {'PVT_TYPE': 'EOS', 'UNIT_SYSTEM': UnitSystem.ENGLISH, 'TEMP_UNIT': TemperatureUnits.RANKINE,
          'DESC': ['EOS EXAMPLE WITH NO TABLES'], 'NHC': 5, 'COMPONENTS': ['C1', 'C2', 'C3-4', 'C5-6', 'C7+'],
          'TEMP': 520.0,
          'EOSOPTIONS': {'EOS_METHOD': 'PR',
                         'EOS_OPT_PRIMARY_LIST': ['ZGIBBS', 'CAPILLARYFLASH', 'VISPE'],
                         'TRANSITION': ('DELTA', {'TCRIT': 0.15, 'TDELZ': 1e-3}),
                         'TRANS_TEST': ('INCRP', {'PHASEFRAC': 0.05}),
                         'PHASEID': ('DENSITY', {'THRESHOLD': 40.0}),
                         'ALPHAMU': 0.01,
                         'LI_FACT': 0.9,
                         'LBC1': 0.1023,
                         'LBC2': 0.02336,
                         'LBC3': 0.05853,
                         'LBC4': -0.04076,
                         'LBC5': 0.009332,
                         }
          }),
    ("""
      DESC EOS EXAMPLE WITH PEDERSON VISCOSITY COEFFICIENTS MODIFIED

      EOS NHC 5
      COMPONENTS C1 C2 C3-4 C5-6 C7+
      LABEL Test1
      TEMP 520.0

      ENGLISH RANKINE

      EOSOPTIONS PR
                 PHASEID
                     DENSITY THRESHOLD 40
                 ALPHAMU 0.01
                 ZGIBBS
                 CAPILLARYFLASH
                 LI_FACT 0.9
                 LBC1 0.1023
                 LBC2 0.02336
                 LBC3 0.05853
                 LBC4 -0.04076
                 LBC5 0.009332
                 TRANSITION DELTA TCRIT 0.15 TDELZ 0.001
                 TRANS_TEST INCRP PHASEFRAC 0.05
                 VISPE
! This is a random comment
                        VISKJ
                        INDEX COEFF
                        1 -10.4
                        2 17.6
                        3 -3019.4
                        4 188.7
                        5 0.0429
                        6 145.29
                        7 6127.68
                        ENDVISKJ

                        VISKK
                        INDEX COEFF
                        1 9.74
                        2 18.08
                        3 4126.66
                        4 44.6
                        5 0.9765
                        6 81.81
                        7 15649.9
                        ENDVISKK

                        VISKKIJ
                        COMP1 COMP2 COEFF
                        C1 C7+ 0.01
                        C3-4 C5-6 -0.025
                        ENDVISKKIJ
    
    """, {'PVT_TYPE': 'EOS', 'UNIT_SYSTEM': UnitSystem.ENGLISH, 'TEMP_UNIT': TemperatureUnits.RANKINE,
          'DESC': ['EOS EXAMPLE WITH PEDERSON VISCOSITY COEFFICIENTS MODIFIED'], 'NHC': 5,
          'COMPONENTS': ['C1', 'C2', 'C3-4', 'C5-6', 'C7+'],
          'TEMP': 520.0,
          'EOSOPTIONS': {'EOS_METHOD': 'PR',
                         'EOS_OPT_PRIMARY_LIST': ['ZGIBBS', 'CAPILLARYFLASH', 'VISPE'],
                         'TRANSITION': ('DELTA', {'TCRIT': 0.15, 'TDELZ': 1e-3}),
                         'TRANS_TEST': ('INCRP', {'PHASEFRAC': 0.05}),
                         'PHASEID': ('DENSITY', {'THRESHOLD': 40.0}),
                         'ALPHAMU': 0.01,
                         'LI_FACT': 0.9,
                         'LBC1': 0.1023,
                         'LBC2': 0.02336,
                         'LBC3': 0.05853,
                         'LBC4': -0.04076,
                         'LBC5': 0.009332,
                         },
          'VISKJ': pd.DataFrame({'INDEX': [1, 2, 3, 4, 5, 6, 7],
                                 'COEFF': [-10.4, 17.6, -3019.4, 188.7, 0.0429, 145.29, 6127.68]
                                 })
          })
     ], ids=['basic black-oil', 'equiv black-oil', 'water-oil',
             'volatile oil', 'gas-water', 'eos_with_tables', 'eos_notables', 'eos_with_visk'
             ])
def test_read_pvt_properties_from_file(mocker, file_contents, expected_pvt_properties):
    # Arrange
    pvt_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    pvt_obj = NexusPVTMethod(file=pvt_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    pvt_obj.read_properties()
    props = pvt_obj.properties

    # Assert
    assert pvt_obj.pvt_type == expected_pvt_properties['PVT_TYPE']
    if pvt_obj.pvt_type == 'EOS':
        eos_opts = pvt_obj.eos_options
        assert pvt_obj.eos_temp == expected_pvt_properties['TEMP']
        assert pvt_obj.eos_nhc == expected_pvt_properties['NHC']
        assert pvt_obj.eos_components == expected_pvt_properties['COMPONENTS']
        for key in expected_pvt_properties['EOSOPTIONS'].keys():
            assert expected_pvt_properties['EOSOPTIONS'][key] == eos_opts[key]
    for key in [key for key in expected_pvt_properties.keys()
                if key not in ['PVT_TYPE', 'TEMP', 'NHC', 'COMPONENTS', 'EOSOPTIONS']]:
        if isinstance(expected_pvt_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_pvt_properties[key], props[key])
        elif isinstance(expected_pvt_properties[key], dict):
            for subkey in expected_pvt_properties[key].keys():
                pd.testing.assert_frame_equal(expected_pvt_properties[key][subkey], props[key][subkey])
        elif isinstance(expected_pvt_properties[key], Enum):
            assert expected_pvt_properties[key] == props[key]
        else:
            assert expected_pvt_properties[key] == props[key]


def test_nexus_blackoil_pvt_repr():
    # Arrange
    pvt_file = NexusFile(location='test/file/pvt.dat')
    pvt_obj = NexusPVTMethod(file=pvt_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    pvt_obj.pvt_type = 'BLACKOIL'
    pvt_obj.properties = {'API': 30.0, 'SPECG': 0.6,
          'UNIT_SYSTEM': UnitSystem.ENGLISH, 'DESC': ['This is first line of description',
                                             'and this is second line of description'
                                             ],
          'SATURATED': pd.DataFrame({'PRES': [14.7, 115., 2515, 3515],
                                     'BO': [1.05, 1.08, 1.25, 1.33],
                                     'BG': [225, 25, 1.089, 0.787],
                                     'RS': [0.005, 0.045, 0.505, 0.69],
                                     'VO': [3.93, 2.78, 0.99, 0.79],
                                     'VG': [0.0105, 0.0109, 0.0193, 0.0193]
                                     }),
          'UNSATOIL_PSAT': {'2000.0': pd.DataFrame({'PRES': [2515, 3515],
                                                    'BO': [1.25, 1.24],
                                                    'VO': [0.99, 0.98]
                                                    }),
                            '1900.0': pd.DataFrame({'PRES': [2515, 3515],
                                                    'BO': [1.25, 1.24],
                                                    'VO': [0.99, 0.98]
                                                    })
                            },
          'UNSATGAS_PRES': {'3515.0': pd.DataFrame({'RV': [0.0],
                                                     'BG': [0.787],
                                                     'VG': [0.0193]
                                                  }),
                             '3415.0': pd.DataFrame({'RV': [0.0],
                                                     'BG': [0.787],
                                                     'VG': [0.0193]
                                                  })
                              }
          }
    expected_output = """
FILE_PATH: test/file/pvt.dat

DESC This is first line of description
DESC and this is second line of description
BLACKOIL API 30.0 SPECG 0.6
ENGLISH
SATURATED
""" + pvt_obj.properties['SATURATED'].to_string(na_rep='', index=False) + '\n' + \
"""
UNSATOIL PSAT 2000.0
""" + pvt_obj.properties['UNSATOIL_PSAT']['2000.0'].to_string(na_rep='', index=False) + '\n' + \
"""
UNSATOIL PSAT 1900.0
""" + pvt_obj.properties['UNSATOIL_PSAT']['1900.0'].to_string(na_rep='', index=False) + '\n' + \
"""
UNSATGAS PRES 3515.0
""" + pvt_obj.properties['UNSATGAS_PRES']['3515.0'].to_string(na_rep='', index=False) + '\n' + \
"""
UNSATGAS PRES 3415.0
""" + pvt_obj.properties['UNSATGAS_PRES']['3415.0'].to_string(na_rep='', index=False) + '\n\n'

    # Act
    result = pvt_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_eos_pvt_repr():
    # Arrange
    pvt_file = NexusFile(location='test/file/pvt.dat')
    pvt_obj = NexusPVTMethod(file=pvt_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    pvt_obj.pvt_type = 'EOS'
    pvt_obj.eos_nhc = 6
    pvt_obj.eos_components = ['C1', 'C3', 'C6', 'C10', 'C15', 'C20']
    pvt_obj.eos_temp = 160.
    pvt_obj.eos_options = {'EOS_METHOD': 'PR',
                           'EOS_OPT_PRIMARY_LIST': ['ZGIBBS', 'FLASH_GIBBS_ON', 'STKATZOFF', 'CAPILLARYFLASH', 'VISPE'],
                           'FUGERR': 6,
                           'TRANSITION': 'NEIGHBOR',
                           'PHASEID': 'FLASH',
                           'TRANS_OPTIMIZATION': {'TDELP': 1, 'TDELZ': 0.001, },
                           'TRANS_TEST': 'GIBBS',
                           'TOL': 0.0001,
                           'TOLSS': 0.01
                           }
    pvt_obj.properties = {'DESC': ['This is a', 'long EOS test case'],
                          'UNIT_SYSTEM': UnitSystem.ENGLISH,
                          'TEMP_UNIT': TemperatureUnits.FAHR,
                          'PROPS': pd.DataFrame({'COMPONENT': ['C1', 'C3', 'C6', 'C10', 'C15', 'C20'],
                                                  'MOLWT': [16.04, 44.01, 86.18, 142.29, 206, 282],
                                                  'OMEGAA': [0.4572355, 0.4572355, 0.4572355, 0.4572355, 0.4572355, 0.4572355],
                                                  'OMEGAB': [0.0777961, 0.0777961, 0.0777961, 0.0777961, 0.0777961, 0.0777961],
                                                  'TC': [-116.67, 206.03, 453.73, 652.13, 810.33, 920.33],
                                                  'PC': [667.8, 616.3, 436.99, 304, 200, 162],
                                                  'VC': [1.598, 3.129, 5.922, 10.09, 16.69, 21.48],
                                                  'ACENTR': [0.013, 0.1524, 0.3007, 0.4885, 0.65, 0.85]
                                                  }),
                          'BINA': pd.DataFrame({'COMPONENT': ['C3', 'C6', 'C10', 'C15', 'C20'],
                                                  'C1':  [0.0,    0.0,    0.0,    0.05,   0.05],
                                                  'C3':  [np.nan, 0.0,    0.0,    0.005,  0.005],
                                                  'C6':  [np.nan, np.nan, 0.0,    0.0,    0.0],
                                                  'C10': [np.nan, np.nan, np.nan, 0.0,    0.0],
                                                  'C15': [np.nan, np.nan, np.nan, np.nan, 0.0]
                                                  }),
                          'PEDTUNE': pd.DataFrame({'INDEX': [1, 2, 3, 4, 5, 6],
                                                  'COEFF': [1, 1, 1.847, 0.5173, 0.007378, 0.031]
                                                  })
                            }
    expected_output = """
FILE_PATH: test/file/pvt.dat

DESC This is a
DESC long EOS test case
EOS NHC 6
COMPONENTS C1 C3 C6 C10 C15 C20
TEMP 160.0
ENGLISH
FAHR
PROPS
""" + pvt_obj.properties['PROPS'].to_string(na_rep='', index=False) + \
"""
ENDPROPS

BINA
""" + pvt_obj.properties['BINA'].to_string(na_rep='', index=False) + \
"""
ENDBINA

PEDTUNE
""" + pvt_obj.properties['PEDTUNE'].to_string(na_rep='', index=False) + \
"""
ENDPEDTUNE

EOSOPTIONS PR
    ZGIBBS
    FLASH_GIBBS_ON
    STKATZOFF
    CAPILLARYFLASH
    VISPE
    FUGERR 6
    TRANSITION NEIGHBOR
    PHASEID FLASH
    TRANS_OPTIMIZATION TDELP 1 TDELZ 0.001
    TRANS_TEST GIBBS
    TOL 0.0001
    TOLSS 0.01
"""

    # Act
    result = pvt_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_pvt_methods_repr():
    # Arrange
    pvt_file = NexusFile(location='test/file/pvt.dat')
    pvt_type = 'EOS'
    eos_nhc = 6
    eos_components = ['C1', 'C3', 'C6', 'C10', 'C15', 'C20']
    eos_temp = 160.
    eos_options = {'EOS_METHOD': 'PR',
                           'EOS_OPT_PRIMARY_LIST': ['ZGIBBS', 'FLASH_GIBBS_ON', 'STKATZOFF', 'CAPILLARYFLASH', 'VISPE'],
                           'FUGERR': 6,
                           'TRANSITION': 'NEIGHBOR',
                           'PHASEID': 'FLASH',
                           'TRANS_OPTIMIZATION': {'TDELP': 1, 'TDELZ': 0.001, },
                           'TRANS_TEST': 'GIBBS',
                           'TOL': 0.0001,
                           'TOLSS': 0.01
                           }
    properties = {'DESC': ['This is a', 'long EOS test case'],
                          'UNIT_SYSTEM': UnitSystem.ENGLISH,
                          'TEMP_UNIT': TemperatureUnits.FAHR,
                          'PROPS': pd.DataFrame({'COMPONENT': ['C1', 'C3', 'C6', 'C10', 'C15', 'C20'],
                                                  'MOLWT': [16.04, 44.01, 86.18, 142.29, 206, 282],
                                                  'OMEGAA': [0.4572355, 0.4572355, 0.4572355, 0.4572355, 0.4572355, 0.4572355],
                                                  'OMEGAB': [0.0777961, 0.0777961, 0.0777961, 0.0777961, 0.0777961, 0.0777961],
                                                  'TC': [-116.67, 206.03, 453.73, 652.13, 810.33, 920.33],
                                                  'PC': [667.8, 616.3, 436.99, 304, 200, 162],
                                                  'VC': [1.598, 3.129, 5.922, 10.09, 16.69, 21.48],
                                                  'ACENTR': [0.013, 0.1524, 0.3007, 0.4885, 0.65, 0.85]
                                                  }),
                          'BINA': pd.DataFrame({'COMPONENT': ['C3', 'C6', 'C10', 'C15', 'C20'],
                                                  'C1':  [0.0,    0.0,    0.0,    0.05,   0.05],
                                                  'C3':  [np.nan, 0.0,    0.0,    0.005,  0.005],
                                                  'C6':  [np.nan, np.nan, 0.0,    0.0,    0.0],
                                                  'C10': [np.nan, np.nan, np.nan, 0.0,    0.0],
                                                  'C15': [np.nan, np.nan, np.nan, np.nan, 0.0]
                                                  }),
                          'PEDTUNE': pd.DataFrame({'INDEX': [1, 2, 3, 4, 5, 6],
                                                  'COEFF': [1, 1, 1.847, 0.5173, 0.007378, 0.031]
                                                  })
                            }
    pvt_obj = NexusPVTMethod(file=pvt_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                             pvt_type=pvt_type, eos_nhc=eos_nhc, eos_components=eos_components, eos_temp=eos_temp,
                             eos_options=eos_options, properties=properties
                             )
    
    pvt_methods_obj = NexusPVTMethods(model_unit_system=UnitSystem.ENGLISH, inputs={1: pvt_obj, 2: pvt_obj})
    expected_output = """
--------------------------------
PVT method 1
--------------------------------

FILE_PATH: test/file/pvt.dat

DESC This is a
DESC long EOS test case
EOS NHC 6
COMPONENTS C1 C3 C6 C10 C15 C20
TEMP 160.0
ENGLISH
FAHR
PROPS
""" + pvt_obj.properties['PROPS'].to_string(na_rep='', index=False) + \
"""
ENDPROPS

BINA
""" + pvt_obj.properties['BINA'].to_string(na_rep='', index=False) + \
"""
ENDBINA

PEDTUNE
""" + pvt_obj.properties['PEDTUNE'].to_string(na_rep='', index=False) + \
"""
ENDPEDTUNE

EOSOPTIONS PR
    ZGIBBS
    FLASH_GIBBS_ON
    STKATZOFF
    CAPILLARYFLASH
    VISPE
    FUGERR 6
    TRANSITION NEIGHBOR
    PHASEID FLASH
    TRANS_OPTIMIZATION TDELP 1 TDELZ 0.001
    TRANS_TEST GIBBS
    TOL 0.0001
    TOLSS 0.01


--------------------------------
PVT method 2
--------------------------------

FILE_PATH: test/file/pvt.dat

DESC This is a
DESC long EOS test case
EOS NHC 6
COMPONENTS C1 C3 C6 C10 C15 C20
TEMP 160.0
ENGLISH
FAHR
PROPS
""" + pvt_obj.properties['PROPS'].to_string(na_rep='', index=False) + \
"""
ENDPROPS

BINA
""" + pvt_obj.properties['BINA'].to_string(na_rep='', index=False) + \
"""
ENDBINA

PEDTUNE
""" + pvt_obj.properties['PEDTUNE'].to_string(na_rep='', index=False) + \
"""
ENDPEDTUNE

EOSOPTIONS PR
    ZGIBBS
    FLASH_GIBBS_ON
    STKATZOFF
    CAPILLARYFLASH
    VISPE
    FUGERR 6
    TRANSITION NEIGHBOR
    PHASEID FLASH
    TRANS_OPTIMIZATION TDELP 1 TDELZ 0.001
    TRANS_TEST GIBBS
    TOL 0.0001
    TOLSS 0.01

"""

    # Act
    result = pvt_methods_obj.__repr__()

    # Assert
    assert result == expected_output