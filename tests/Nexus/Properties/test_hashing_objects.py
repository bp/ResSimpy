import numpy as np
import pandas as pd

from ResSimpy.Enums.FluidTypeEnums import PvtType
from ResSimpy.Enums.UnitsEnum import UnitSystem, TemperatureUnits
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusPVTMethod import NexusPVTMethod


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
    # act + assert
    assert method_1 != method_2
    assert method_1.properties == method_2.properties
    assert hash(method_1) == hash(method_2)
    assert hash(method_1) != hash(method_3)
