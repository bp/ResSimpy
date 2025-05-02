import numpy as np
import pandas as pd

from ResSimpy.Enums.FluidTypeEnums import PvtType
from ResSimpy.Enums.UnitsEnum import UnitSystem, TemperatureUnits, SUnits
from ResSimpy.Nexus.DataModels.NexusAquiferMethod import NexusAquiferMethod
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Nexus.DataModels.NexusPVTMethod import NexusPVTMethod
from ResSimpy.Nexus.DataModels.NexusWaterMethod import NexusWaterMethod


def test_pvt_method_hash():
    # Arrange
    pvt_file = NexusFile(location='test/file/pvt.dat')
    pvt_type = PvtType.EOS
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
                                        'C1': [0.0, 0.0, 0.0, 0.05, 0.05],
                                        'C3': [np.nan, 0.0, 0.0, 0.005, 0.005],
                                        'C6': [np.nan, np.nan, 0.0, 0.0, 0.0],
                                        'C10': [np.nan, np.nan, np.nan, 0.0, 0.0],
                                        'C15': [np.nan, np.nan, np.nan, np.nan, 0.0]
                                        }),
                  'PEDTUNE': pd.DataFrame({'INDEX': [1, 2, 3, 4, 5, 6],
                                           'COEFF': [1, 1, 1.847, 0.5173, 0.007378, 0.031]
                                           })
                  }
    properties_3 = {'DESC': ['This is a', 'different PVT case']
                    }
    method_1 = NexusPVTMethod(file=pvt_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                              pvt_type=pvt_type, eos_nhc=eos_nhc, eos_components=eos_components, eos_temp=eos_temp,
                              eos_options=eos_options, properties=properties
                              )

    # Change input number to ensure the hash is the same
    method_2 = NexusPVTMethod(file=pvt_file, input_number=10, model_unit_system=UnitSystem.ENGLISH,
                              pvt_type=pvt_type, eos_nhc=eos_nhc, eos_components=eos_components, eos_temp=eos_temp,
                              eos_options=eos_options, properties=properties
                              )
    method_3 = NexusPVTMethod(file=pvt_file, input_number=10, model_unit_system=UnitSystem.ENGLISH,
                              pvt_type=pvt_type, eos_nhc=eos_nhc, eos_components=eos_components, eos_temp=eos_temp,
                              eos_options=eos_options, properties=properties_3
                              )
    # Act + Assert
    assert method_1 == method_2
    assert method_1.properties == method_2.properties
    assert hash(method_1) == hash(method_2)
    assert hash(method_1) != hash(method_3)


def test_hyd_method_hash():
    # Arrange
    hyd_file = NexusFile(location='test/file/hyd.dat')
    hydraulic_props = {'DESC': ['Hydraulics Data'],
                       'UNIT_SYSTEM': UnitSystem.ENGLISH,
                       'QOIL': np.array([1.0, 1000., 3000.]),
                       'GOR': np.array([0.0, 0.5]),
                       'WCUT': np.array([0.0]),
                       'THP': np.array([100., 500.]),
                       'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 2, 2, 2],
                                                  'IWCUT': [1, 1, 1, 1, 1, 1],
                                                  'IQOIL': [1, 2, 3, 1, 2, 3],
                                                  'BHP0': [2470., 2478., 2493., 1860., 1881., 1947.],
                                                  'BHP1': [2545., 2548., 2569., 1990., 2002., 2039.0]
                                                  })
                       }
    hydraulic_props_3 = {'DESC': ['Hydraulics Data'],
                         'UNIT_SYSTEM': UnitSystem.ENGLISH,
                         'QOIL': np.array([1.0, 1000., 3000.]),
                         'GOR': np.array([0.0, 0.5]),
                         'WCUT': np.array([0.0]),
                         'ALQ': np.array([0.0, 50.0]),
                         'ALQ_PARAM': 'GASRATE',
                         'THP': np.array([100., 500., 900., 1400., 2000.]),
                         'HYD_TABLE': pd.DataFrame({'IGOR': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                                                    'IWCUT': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                                    'IALQ': [1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2],
                                                    'IQOIL': [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
                                                    'BHP0': [2470., 2478., 2493., 2535., 2541., 2555.,
                                                             1860., 1881., 1947., 1990., 2004., 2033.],
                                                    'BHP1': [2545., 2548., 2569., 2600., 2608., 2631.,
                                                             1990., 2002., 2039., 2100., 2109., 2130.],
                                                    'BHP2': [2600., 2613., 2638., 2650., 2673., 2703.,
                                                             2090., 2101., 2131., 2190., 2206., 2224.],
                                                    'BHP3': [2820., 2824., 2870., 2852., 2884., 2931.,
                                                             2435., 2438., 2448., 2530., 2537., 2548.],
                                                    'BHP4': [3070., 3081., 3138., 3130., 3141., 3197.,
                                                             2830., 2836., 2848., 2916., 2926., 2946.]
                                                    }),
                         'DATGRAD': 'GRAD',
                         'DEPTH': 10000.0,
                         'WATINJ': {'GRAD': 0.433, 'VISC': 0.7, 'LENGTH': 9000,
                                    'ROUGHNESS': 1e-5, 'DZ': 8000, 'DIAM': 7},
                         'NOCHK': ''}

    hyd_obj = NexusHydraulicsMethod(file=hyd_file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                    properties=hydraulic_props)
    hyd_obj_2 = NexusHydraulicsMethod(file=hyd_file, input_number=2, model_unit_system=UnitSystem.ENGLISH,
                                      properties=hydraulic_props)
    hyd_obj_3 = NexusHydraulicsMethod(file=hyd_file, input_number=2, model_unit_system=UnitSystem.ENGLISH,
                                      properties=hydraulic_props_3)
    # Act + Assert
    assert hash(hyd_obj) == hash(hyd_obj_2)
    assert hash(hyd_obj_3) != hash(hyd_obj_2)


def test_method_with_inbuilt_hashable():
    """Tests the DynamicProperty __hash__ method for a method with only properties dict to distinguish the hash."""
    # Arrange
    # add dummy file
    file = NexusFile(location='test/file/test.dat')
    properties = {'DESC': ['This is first line of description', 'and this is second line of description'],
                  'CARTER_TRACY': '', 'CT': 1e-6, 'H': 50, 'RO': 5000, 'S': 0.3333, 'TC': 400,
                  'TDPD': pd.DataFrame({'TD': [0., 0.01, 0.1, 0.2],
                                        'PD': [0., 0.115, 0.35, 0.472]
                                        })
                  }
    properties_3 = {'DESC': ['This is first line of description', 'and this is second line of description'],
                    'UNIT_SYSTEM': UnitSystem.ENGLISH, 'SUNITS': SUnits.PPM, 'IWATER': 2, 'SALINITY': 300000,
                    'LINFAC': 2.5,
                    'FETKOVICH': '', 'LABEL': 'FETTY_V', 'RADIAL': '', 'VISC': 1.1, 'CT': 1e-6, 'H': 50, 'RO': 5000,
                    'S': 0.3333, 'RE': 10000, 'NOFLOW': '', 'WAQI': 5e8, 'PAQI': 4800, 'DAQI': 9600,
                    'TRACER': pd.DataFrame({'NAME': ['c1', 'c2'],
                                            'CONCENTRATION': [0.2, 0.05]
                                            })
                    }

    method_1 = NexusAquiferMethod(file=file, input_number=1, model_unit_system=UnitSystem.ENGLISH,
                                  properties=properties
                                  )
    method_2 = NexusAquiferMethod(file=file, input_number=2, model_unit_system=UnitSystem.ENGLISH,
                                  properties=properties
                                  )
    method_3 = NexusAquiferMethod(file=file, input_number=3, model_unit_system=UnitSystem.ENGLISH,
                                  properties=properties_3
                                  )

    # Act + Assert
    assert hash(method_1) == hash(method_2)
    assert hash(method_1) != hash(method_3)


def test_watermethod_hash():
    file_contents = """
    DESC This is first line of description
    DESC and this is second line of description

    SUNITS PPM
    KELVIN

    ! This is a comment
    TEMP 394.3
        SALINITY 100000
            DENW 62.4 CW 3.4
            VISW 0.7 BW 1.04
            PREF 3600

        SALINITY 200000
            DENW 65.4 CW 4.4
            VISW 0.8 BW 1.05

    TEMP 399.8
        SALINITY 100000
            DENW 62.4 CW 3.5
            VISW 0.8 BW 1.05
            PREF 3600

        SALINITY 200000
            DENW 65.4 CW 4.5
            VISW 0.9 BW 1.06
    """

    file_contents_3 = """
    DESC This is first line of description
    DESC and this is second line of description

    FAHR

    ! This is a comment
    TEMP 250
        DENW 62.4 CW 3.4
        VISW 0.7 BW 1.04
        PREF 3600

    TEMP 260
        DENW 62.4 CW 4.4
        VISW 0.8 BW 1.05

    TEMP 270
        DENW 62.4 CW 5.4
        VISW 0.9 BW 1.06
    """

    wat_file = NexusFile(location='', file_content_as_list=file_contents.splitlines())
    wat_file_3 = NexusFile(location='', file_content_as_list=file_contents_3.splitlines())
    wat_obj = NexusWaterMethod(file=wat_file, input_number=1, model_unit_system=UnitSystem.ENGLISH)
    wat_obj_2 = NexusWaterMethod(file=wat_file, input_number=2, model_unit_system=UnitSystem.ENGLISH)
    wat_obj_3 = NexusWaterMethod(file=wat_file_3, input_number=3, model_unit_system=UnitSystem.ENGLISH)

    # Act
    wat_obj.read_properties()
    wat_obj_2.read_properties()
    wat_obj_3.read_properties()

    # Assert 
    assert hash(wat_obj) == hash(wat_obj_2)
    assert hash(wat_obj) != hash(wat_obj_3)
