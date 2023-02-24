import pandas as pd
import pytest

from ResSimpy.Nexus.DataModels.NexusPVT import NexusPVT



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
    2515 1.25 1.089 0.505 0.99 0.0193 ! This is an inline comment, in a table
    3515 1.33 0.787 0.69 0.79 0.0193
    
    UNSATOIL PSAT 2000.0
    PRES BO VO
    2515 1.25 0.99
    3515 1.24 0.98
    """, {'PVT_TYPE': 'BLACKOIL', 'API': 30.0, 'SPECG': 0.6,
          'UNIT_SYSTEM': 'ENGLISH', 'DESC': ['This is first line of description',
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
    PRES BG VG
    14.7 225.0 0.0105
    115. 25.0 0.0109
    2515 1.089 0.0193
    3515 0.787 0.0193
    
    UNSATOIL PSAT 2000.0
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
          'UNSATOIL_PSAT': {'2000.0': pd.DataFrame({'PRES': [2515, 3515],
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
          'UNIT_SYSTEM': 'ENGLISH', 
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
          'UNIT_SYSTEM': 'ENGLISH', 'DESC': ['This is first line of description',
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
          'UNSATGAS': {'3515.0': pd.DataFrame({'RV': [0.0],
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
    ], ids=['basic black-oil', 'equiv black-oil', 'water-oil',
            'volatile oil', 'gas-water'
            ])
def test_read_properties_from_file(mocker, file_contents, expected_pvt_properties):
    # Arrange
    pvt_obj = NexusPVT()

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    pvt_obj.read_properties_from_file('test/file/pvt.dat')
    props = pvt_obj.properties

    # Assert
    for key in expected_pvt_properties.keys():
        if type(expected_pvt_properties[key]) == pd.DataFrame:
            pd.testing.assert_frame_equal(expected_pvt_properties[key], props[key])
        elif type(expected_pvt_properties[key]) == dict:
            for subkey in expected_pvt_properties[key].keys():
                pd.testing.assert_frame_equal(expected_pvt_properties[key][subkey], props[key][subkey])
        else:
            assert expected_pvt_properties[key] == props[key]

