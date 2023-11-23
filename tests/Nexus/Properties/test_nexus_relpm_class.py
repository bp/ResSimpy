import numpy as np
import pandas as pd
import pytest
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile

from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod
from ResSimpy.Nexus.NexusRelPermMethods import NexusRelPermMethods

@pytest.mark.parametrize("file_contents, expected_relpm_properties",
    [("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    WOTABLE LOW_SAL
      SW    KROW   KRW     PCWO
      0.20  1.0    0.0     1.0
      0.250 0.7290 0.0005
      0.350 0.3430 0.0135
      0.425 0.1664 0.0456  0.2
      0.500 0.0640 0.1080
      0.600 0.0080 0.2560
      0.700 0.0000  0.5000 0.0

    GOTABLE
      SG KROG KRG PCGO
      0.00000 1.0000 0.00000 0.0
      0.05000 0.7290 0.00390
      0.20000 0.2160 0.06250
      0.40000 0.0080 0.2500 1.0
      0.55000 0.00 0.4727
      0.65000 0.00 0.6602
      0.80000 0.00 1.0000 5.0

    WOTABLE_IMB
      SW    KROW   KRW     PCWO
      0.20  1.0    0.0     1.0
      0.250 0.7290 0.0005
      0.350 0.3430 0.0135
      0.425 0.1664 0.0456  0.2
      0.500 0.0640 0.1080
      0.600 0.0080 0.2560
      0.700 0.0000  0.5000 0.0

    HYSTERESIS KRG LINEAR MAXTRAP 0.2 NOMOD
               KRW USER
               KROW KILLOUGH MAXTRAP 0.2 EXP 1.1
               PCWO MAXSW 0.8 ETA 0.15 TRAPSCALE
               PCGO
               WAG LAND 1.1 NOOILHYS
               TOLREV 0.05
               NOCHK_HYS

    STONE1 SOMOPT2 0.05
    STONE2_WAT

    SCALING TWOPOINT
    
    PRSTAB
    SWL SWR SWRO SWU KRO_SWL
    0.100 0.200 0.600 1.0000 0.55
    0.1500 0.250 0.700 0.900 0.65

    VEGO_PC
    VEWO
    DRELPM 0.9

    IFT
    TENTHR 0.005
    XEX 0.3
    TENI 0.005

    FREEZE_PCGO
    FREEZE_PCWO

    DERIVATIVES NUMERICAL

    NONDARCY_GAS
    ENDNONDARCY_GAS

    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'STONE1': '', 'SOMOPT2': 0.05, 'LOW_SAL': '', 'SCALING': 'TWOPOINT', 'VEGO_PC': '', 'STONE2_WAT': '',
          'FREEZE_PCGO': '', 'FREEZE_PCWO': '', 'DERIVATIVES': 'NUMERICAL', 'NONDARCY_GAS': {},
          'VEWO': '', 'DRELPM': 0.9, 'IFT': '', 'TENTHR': 0.005, 'XEX': 0.3, 'TENI': 0.005,
          'WOTABLE': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                   'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                   'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                   'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                   }),
          'GOTABLE': pd.DataFrame({'SG': [0, 0.05, 0.2, 0.4, 0.55, 0.65, 0.8],
                                   'KROG': [1, 0.729, 0.216, 0.008, 0, 0, 0],
                                   'KRG': [0, 0.0039, 0.0625, 0.25, 0.4727, 0.6602, 1],
                                   'PCGO': [0., np.nan, np.nan, 1., np.nan, np.nan, 5.0]
                                   }),
          'WOTABLE_IMB': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                       'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                       'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                       'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                       }),
          'PRSTAB': pd.DataFrame({'SWL': [0.1, 0.15],
                                  'SWR': [0.2, 0.25],
                                  'SWRO': [0.6, 0.7],
                                  'SWU': [1., 0.9],
                                  'KRO_SWL': [0.55, 0.65]
                                  }),
          'HYSTERESIS_PARAMS': {'KRG': {'LINEAR': {'MAXTRAP': 0.2, 'NOMOD': ''}},
                                'KRW': 'USER',
                                'KROW': {'KILLOUGH': {'MAXTRAP': 0.2, 'EXP': 1.1}},
                                'PCWO': {'MAXSW': 0.8, 'ETA': 0.15, 'TRAPSCALE': ''},
                                'PCGO': {},
                                'WAG': {'LAND': 1.1, 'NOOILHYS': ''},
                                'TOLREV': 0.05, 'NOCHK_HYS': ''
                                }
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    GWTABLE
      SG      KRWG   KRG     PCGW
      0.00000 1.0000 0.00000 0.0
      0.05000 0.7290 0.00390
      0.30000 0.0640 0.1406
      0.40000 0.0080 0.2500  1.0
      0.50000 0.00   0.3906
      0.70000 0.00   0.7656
      0.75000 0.00   0.8789  3.0

    JFUNC

    IFT METHOD2
    IRELPM_LOWIFT

    RECONSTRUCT

    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'JFUNC': '', 'IFT': 'METHOD2', 'IRELPM_LOWIFT': '','RECONSTRUCT': {},
          'GWTABLE': pd.DataFrame({'SG': [0, 0.05, 0.3, 0.4, 0.5, 0.7, 0.75],
                                   'KRWG': [1, 0.729, 0.064, 0.008, 0, 0, 0],
                                   'KRG': [0, 0.0039, 0.1406, 0.25, 0.3906, 0.7656, 0.8789],
                                   'PCGW': [0., np.nan, np.nan, 1., np.nan, np.nan, 3.0]
                                   })
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    WOTABLE
      SW    KROW   KRW     PCWO
      0.20  1.0    0.0     1.0
      0.250 0.7290 0.0005
      0.350 0.3430 0.0135
      0.425 0.1664 0.0456  0.2
      0.500 0.0640 0.1080
      0.600 0.0080 0.2560
      0.700 0.0000  0.5000 0.0

    GOTABLE
      SG KROG KRG PCGO
      0.00000 1.0000 0.00000 0.0 ! Inline comment

      ! comment in table, with line breaks

      0.05000 0.7290 0.00390
      0.20000 0.2160 0.06250
      0.40000 0.0080 0.2500 1.0
      0.55000 0.00 0.4727
      0.65000 0.00 0.6602
      0.80000 0.00 1.0000 5.0

    GW3PHASE

    KRWINT

    RECONSTRUCT

    JFUNC KX
       PERMBASIS 100
       PORBASIS 0.2

    SCALING TWOPOINT
    SCALING_PC THREEPOINT
    NOCHK
    VIP_INJ_PERF_KR_SCALING

    NEARCRIT

    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'GW3PHASE': '', 'JFUNC': 'KX', 'PERMBASIS': 100, 'PORBASIS': 0.2, 'NOCHK': '', 'NEARCRIT': '',
          'VIP_INJ_PERF_KR_SCALING': '', 'SCALING': 'TWOPOINT', 'SCALING_PC': 'THREEPOINT', 'RECONSTRUCT': {},
          'KRWINT': '',
          'WOTABLE': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                   'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                   'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                   'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                   }),
          'GOTABLE': pd.DataFrame({'SG': [0, 0.05, 0.2, 0.4, 0.55, 0.65, 0.8],
                                   'KROG': [1, 0.729, 0.216, 0.008, 0, 0, 0],
                                   'KRG': [0, 0.0039, 0.0625, 0.25, 0.4727, 0.6602, 1],
                                   'PCGO': [0., np.nan, np.nan, 1., np.nan, np.nan, 5.0]
                                   })
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    HYSTERESIS KRG LINEAR MAXTRAP 0.30
    GRMTABLE_SGTR
    SGTR SGRM KRGMX
    0.00 0.05 0.96
    0.05 0.10 0.9
    0.10 0.15 0.85
    0.17 0.23 0.81
    0.24 0.30 0.75
    0.33 0.40 0.7
    0.4 0.48 0.6
    0.5 0.6 0.5
    GRMTABLE
    SG KRG
    0.21 0.0
    0.30 0.02
    0.43 0.10
    0.55 0.20
    0.66 0.33
    0.77 0.5
    0.80 0.54
    GRMDSW 0.025

    NEARCRIT HCSCALE
    """, {'DESC': ['This is first line of description', 'and this is second line of description'],
          'GRMDSW': 0.025, 'NEARCRIT': 'HCSCALE',
          'HYSTERESIS_PARAMS': {'KRG': {'LINEAR': {'MAXTRAP': 0.3}}},
          'GRMTABLE_SGTR': pd.DataFrame({'SGTR': [0.0, 0.05, 0.1, 0.17, 0.24, 0.33, 0.4, 0.5],
                                         'SGRM': [0.05, 0.1, 0.15, 0.23, 0.3, 0.4, 0.48, 0.6],
                                         'KRGMX': [0.96, 0.9, 0.85, 0.81, 0.75, 0.7, 0.6, 0.5]
                                         }),
          'GRMTABLE': pd.DataFrame({'SG': [0.21, 0.3, 0.43, 0.55, 0.66, 0.77, 0.8],
                                    'KRG': [0., 0.02, 0.1, 0.2, 0.33, 0.5, 0.54]
                                    })
          }
    ),
    ("""
    DESC This is first line of description
    DESC and this is second line of description

    ! This is a comment
    WOTABLE 
      SW    KROW   KRW     PCWO
      0.20  1.0    0.0     1.0
      0.250 0.7290 0.0005
      0.350 0.3430 0.0135
      0.425 0.1664 0.0456  0.2
      0.500 0.0640 0.1080
      0.600 0.0080 0.2560
      0.700 0.0000  0.5000 0.0

    GOTABLE
      SG KROG KRG PCGO
      0.00000 1.0000 0.00000 0.0
      0.05000 0.7290 0.00390
      0.20000 0.2160 0.06250
      0.40000 0.0080 0.2500 1.0
      0.55000 0.00 0.4727
      0.65000 0.00 0.6602
      0.80000 0.00 1.0000 5.0

    NONDARCY_GAS
      BETA 0.9
      IFT_THRES 0.98
    ENDNONDARCY_GAS

    NONDARCY_OIL
      BETA0 0.001
      BETA1 -0.5
      BETA2 -5
      BETA3 -0.5
      BETA4 -3
      BETA5 4.4
    ENDNONDARCY_OIL

    RECONSTRUCT NSGDIM 101
    NSWDIM 101

    VIP_RELPM

    """, {'DESC': ['This is first line of description', 'and this is second line of description'], 'VIP_RELPM': '',
          'NONDARCY_GAS': {'BETA': 0.9, 'IFT_THRES': 0.98}, 'RECONSTRUCT': {'NSGDIM': 101, 'NSWDIM': 101},
          'NONDARCY_OIL': {'BETA0': 0.001, 'BETA1': -0.5, 'BETA2': -5, 'BETA3': -0.5, 'BETA4': -3, 'BETA5': 4.4},
          'WOTABLE': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                   'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                   'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                   'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                   }),
          'GOTABLE': pd.DataFrame({'SG': [0, 0.05, 0.2, 0.4, 0.55, 0.65, 0.8],
                                   'KROG': [1, 0.729, 0.216, 0.008, 0, 0, 0],
                                   'KRG': [0, 0.0039, 0.0625, 0.25, 0.4727, 0.6602, 1],
                                   'PCGO': [0., np.nan, np.nan, 1., np.nan, np.nan, 5.0]
                                   })
          }
    )
    ], ids=['blackoil_relpm_3ph', 'basic_gaswater', 'gaswater_3ph', 'gas_remob', 'nondarcy']
)
def test_read_relpm_properties_from_file(mocker, file_contents, expected_relpm_properties):
    # Arrange
    rp_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    relpm_obj = NexusRelPermMethod(file=rp_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)

    # mock out open to return our test file contents
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    relpm_obj.read_properties()
    props = relpm_obj.properties
    hyst_params = relpm_obj.hysteresis_params

    # Assert
    for key in expected_relpm_properties:
        if key == 'HYSTERESIS_PARAMS':
            for subkey in expected_relpm_properties['HYSTERESIS_PARAMS']:
                assert hyst_params[subkey] == expected_relpm_properties[key][subkey]
        elif isinstance(expected_relpm_properties[key], pd.DataFrame):
            pd.testing.assert_frame_equal(expected_relpm_properties[key], props[key])
        else:
            assert props[key] == expected_relpm_properties[key]


def test_nexus_relpm_repr():
    # Arrange
    rp_file = NexusFile(location='test/file/relpm.dat')
    relpm_obj = NexusRelPermMethod(file=rp_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    relpm_obj.hysteresis_params = {'KRG': {'LINEAR': {'MAXTRAP': 0.2, 'NOMOD': ''}},
                                   'KRW': 'USER',
                                   'KROW': {'KILLOUGH': {'MAXTRAP': 0.2, 'EXP': 1.1}},
                                   'PCWO': {'MAXSW': 0.8, 'ETA': 0.15, 'TRAPSCALE': ''},
                                   'PCGO': {},
                                   'WAG': {'LAND': 1.1, 'NOOILHYS': ''},
                                   'TOLREV': 0.05, 'NOCHK_HYS': ''
                                   }
    relpm_obj.properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                            'WOTABLE': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                                     'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                                     'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                                     'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                                     }),
                            'GOTABLE': pd.DataFrame({'SG': [0, 0.05, 0.2, 0.4, 0.55, 0.65, 0.8],
                                                     'KROG': [1, 0.729, 0.216, 0.008, 0, 0, 0],
                                                     'KRG': [0, 0.0039, 0.0625, 0.25, 0.4727, 0.6602, 1],
                                                     'PCGO': [0., np.nan, np.nan, 1., np.nan, np.nan, 5.0]
                                                     }),
                            'WOTABLE_IMB': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                                         'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                                         'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                                         'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                                         }),
                            'PRSTAB': pd.DataFrame({'SWL': [0.1, 0.15],
                                                    'SWR': [0.2, 0.25],
                                                    'SWRO': [0.6, 0.7],
                                                    'SWU': [1., 0.9],
                                                    'KRO_SWL': [0.55, 0.65]
                                                     }),
                            'STONE1': '', 'SOMOPT2': 0.05, 'STONE2_WAT': '', 'LOW_SAL': '', 'SCALING': 'TWOPOINT', 'VEGO_PC': '',
                            'VEWO': '', 'DRELPM': 0.9, 'IFT': '', 'TENTHR': 0.005, 'XEX': 0.3, 'TENI': 0.005,
                            'FREEZE_PCGO': '', 'FREEZE_PCWO': '', 'DERIVATIVES': 'NUMERICAL',
                            'NONDARCY_GAS': {},
                            'NONDARCY_OIL': {'BETA0': 0.001, 'BETA1': -0.5, 'BETA2': -5, 'BETA3': -0.5, 'BETA4': -3, 'BETA5': 4.4},
                            'RECONSTRUCT': {'NSGDIM': 101, 'NSWDIM': 101}, 'VIP_RELPM': ''
          }
    expected_output = """
FILE_PATH: test/file/relpm.dat

DESC This is first line of description
DESC and this is second line of description
WOTABLE LOW_SAL
""" + relpm_obj.properties['WOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
GOTABLE
""" + relpm_obj.properties['GOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WOTABLE_IMB
""" + relpm_obj.properties['WOTABLE_IMB'].to_string(na_rep='', index=False) + '\n' + \
"""
PRSTAB
""" + relpm_obj.properties['PRSTAB'].to_string(na_rep='', index=False) + '\n' + \
"""
STONE1 SOMOPT2 0.05
STONE2_WAT
SCALING TWOPOINT
VEGO_PC
VEWO
DRELPM 0.9
IFT
TENTHR 0.005
XEX 0.3
TENI 0.005
FREEZE_PCGO
FREEZE_PCWO
DERIVATIVES NUMERICAL
NONDARCY_GAS
ENDNONDARCY_GAS
NONDARCY_OIL
    BETA0 0.001
    BETA1 -0.5
    BETA2 -5
    BETA3 -0.5
    BETA4 -3
    BETA5 4.4
ENDNONDARCY_OIL
RECONSTRUCT
    NSGDIM 101
    NSWDIM 101
VIP_RELPM
HYSTERESIS KRG LINEAR MAXTRAP 0.2 NOMOD
           KRW USER
           KROW KILLOUGH MAXTRAP 0.2 EXP 1.1
           PCWO MAXSW 0.8 ETA 0.15 TRAPSCALE
           PCGO
           WAG LAND 1.1 NOOILHYS
           TOLREV 0.05
           NOCHK_HYS
"""

    # Act
    result = relpm_obj.__repr__()

    # Assert
    assert result == expected_output


def test_nexus_relperm_methods_repr():
    # Arrange
    relpm_file = NexusFile(location='test/file/relpm.dat')
    hysteresis_params = {'KRG': {'LINEAR': {'MAXTRAP': 0.2, 'NOMOD': ''}},
                         'KRW': 'USER',
                         'KROW': {'KILLOUGH': {'MAXTRAP': 0.2, 'EXP': 1.1}},
                         'PCWO': {'MAXSW': 0.8, 'ETA': 0.15, 'TRAPSCALE': ''},
                         'PCGO': {},
                         'WAG': {'LAND': 1.1, 'NOOILHYS': ''},
                         'TOLREV': 0.05, 'NOCHK_HYS': ''
                         }
    properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                  'WOTABLE': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                           'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                           'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                           'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                           }),
                  'GOTABLE': pd.DataFrame({'SG': [0, 0.05, 0.2, 0.4, 0.55, 0.65, 0.8],
                                           'KROG': [1, 0.729, 0.216, 0.008, 0, 0, 0],
                                           'KRG': [0, 0.0039, 0.0625, 0.25, 0.4727, 0.6602, 1],
                                           'PCGO': [0., np.nan, np.nan, 1., np.nan, np.nan, 5.0]
                                           }),
                  'WOTABLE_IMB': pd.DataFrame({'SW': [0.2, 0.25, 0.35, 0.425, 0.5, 0.6, 0.7],
                                               'KROW': [1.0, 0.729, 0.343, 0.1664, 0.064, 0.008, 0],
                                               'KRW': [0.0, 0.0005, 0.0135, 0.0456, 0.108, 0.256, 0.50],
                                               'PCWO': [1., np.nan, np.nan, 0.2, np.nan, np.nan, 0.0]
                                               }),
                  'PRSTAB': pd.DataFrame({'SWL': [0.1, 0.15],
                                          'SWR': [0.2, 0.25],
                                          'SWRO': [0.6, 0.7],
                                          'SWU': [1., 0.9],
                                          'KRO_SWL': [0.55, 0.65]
                                          }),
                  'STONE1': '', 'SOMOPT2': 0.05, 'STONE2_WAT': '', 'LOW_SAL': '', 'SCALING': 'TWOPOINT', 'VEGO_PC': '',
                  'VEWO': '', 'DRELPM': 0.9, 'IFT': '', 'TENTHR': 0.005, 'XEX': 0.3, 'TENI': 0.005,
                  'FREEZE_PCGO': '', 'FREEZE_PCWO': '', 'DERIVATIVES': 'NUMERICAL',
                  'NONDARCY_GAS': {},
                  'NONDARCY_OIL': {'BETA0': 0.001, 'BETA1': -0.5, 'BETA2': -5, 'BETA3': -0.5, 'BETA4': -3, 'BETA5': 4.4},
                  'RECONSTRUCT': {'NSGDIM': 101, 'NSWDIM': 101}, 'VIP_RELPM': ''
                  }
    relpm_obj = NexusRelPermMethod(file=relpm_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                   properties=properties, hysteresis_params=hysteresis_params)
    relpm_methods_obj = NexusRelPermMethods(model_unit_system=UnitSystem.ENGLISH, inputs={1: relpm_obj,
                                                                                          2: relpm_obj})
    expected_output = """
--------------------------------
RELPM method 1
--------------------------------

FILE_PATH: test/file/relpm.dat

DESC This is first line of description
DESC and this is second line of description
WOTABLE LOW_SAL
""" + properties['WOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
GOTABLE
""" + properties['GOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WOTABLE_IMB
""" + properties['WOTABLE_IMB'].to_string(na_rep='', index=False) + '\n' + \
"""
PRSTAB
""" + properties['PRSTAB'].to_string(na_rep='', index=False) + '\n' + \
"""
STONE1 SOMOPT2 0.05
STONE2_WAT
SCALING TWOPOINT
VEGO_PC
VEWO
DRELPM 0.9
IFT
TENTHR 0.005
XEX 0.3
TENI 0.005
FREEZE_PCGO
FREEZE_PCWO
DERIVATIVES NUMERICAL
NONDARCY_GAS
ENDNONDARCY_GAS
NONDARCY_OIL
    BETA0 0.001
    BETA1 -0.5
    BETA2 -5
    BETA3 -0.5
    BETA4 -3
    BETA5 4.4
ENDNONDARCY_OIL
RECONSTRUCT
    NSGDIM 101
    NSWDIM 101
VIP_RELPM
HYSTERESIS KRG LINEAR MAXTRAP 0.2 NOMOD
           KRW USER
           KROW KILLOUGH MAXTRAP 0.2 EXP 1.1
           PCWO MAXSW 0.8 ETA 0.15 TRAPSCALE
           PCGO
           WAG LAND 1.1 NOOILHYS
           TOLREV 0.05
           NOCHK_HYS


--------------------------------
RELPM method 2
--------------------------------

FILE_PATH: test/file/relpm.dat

DESC This is first line of description
DESC and this is second line of description
WOTABLE LOW_SAL
""" + properties['WOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
GOTABLE
""" + properties['GOTABLE'].to_string(na_rep='', index=False) + '\n' + \
"""
WOTABLE_IMB
""" + properties['WOTABLE_IMB'].to_string(na_rep='', index=False) + '\n' + \
"""
PRSTAB
""" + properties['PRSTAB'].to_string(na_rep='', index=False) + '\n' + \
"""
STONE1 SOMOPT2 0.05
STONE2_WAT
SCALING TWOPOINT
VEGO_PC
VEWO
DRELPM 0.9
IFT
TENTHR 0.005
XEX 0.3
TENI 0.005
FREEZE_PCGO
FREEZE_PCWO
DERIVATIVES NUMERICAL
NONDARCY_GAS
ENDNONDARCY_GAS
NONDARCY_OIL
    BETA0 0.001
    BETA1 -0.5
    BETA2 -5
    BETA3 -0.5
    BETA4 -3
    BETA5 4.4
ENDNONDARCY_OIL
RECONSTRUCT
    NSGDIM 101
    NSWDIM 101
VIP_RELPM
HYSTERESIS KRG LINEAR MAXTRAP 0.2 NOMOD
           KRW USER
           KROW KILLOUGH MAXTRAP 0.2 EXP 1.1
           PCWO MAXSW 0.8 ETA 0.15 TRAPSCALE
           PCGO
           WAG LAND 1.1 NOOILHYS
           TOLREV 0.05
           NOCHK_HYS

"""

    # Act
    result = relpm_methods_obj.__repr__()

    # Assert
    assert result == expected_output
