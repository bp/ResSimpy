import numpy as np
import pandas as pd
import pytest

from ResSimpy import NexusSimulator
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod
from ResSimpy.Nexus.DataModels.NexusRelPermMethod import NexusRelPermMethod


def test_add_hydraulics_method():
    # Arrange
    model = NexusSimulator(origin='new_model.fcs', assume_loaded=True, start_date='01/01/2020', )

    hydraulic_method = NexusHydraulicsMethod(input_number=10, properties={'ALQ': 1000},
                                             file=None, model_unit_system=model.run_units,
                                             )

    expected_generated_nexus_file = NexusFile(location='new_method.dat',
                                              file_content_as_list=['ALQ 1000\n', '\n'])
    expected_generated_nexus_file._file_modified_set(True)

    # Act
    model.hydraulics.add_method(hydraulic_method, new_file_name='new_method.dat', create_new_file=False)

    # Assert
    assert model.hydraulics.inputs[10] == hydraulic_method
    assert model.hydraulics.inputs[10].properties['ALQ'] == 1000
    assert model.hydraulics.inputs[10].input_number == 10
    assert model.hydraulics.inputs[10].file == expected_generated_nexus_file
    assert model.model_files is not None
    assert model.model_files.hyd_files is not None
    assert model.model_files.hyd_files[10] == expected_generated_nexus_file


def test_add_relpm_method():
    # Arrange
    model = NexusSimulator(origin='new_model.fcs', assume_loaded=True, start_date='01/01/2020', )

    relpm_props = {'DESC': ['This is first line of description', 'and this is second line of description'],
                   'GWTABLE': pd.DataFrame({'SG': [0, 0.05, 0.3, 0.4, 0.5, 0.7, 0.75],
                                            'KRWG': [1, 0.729, 0.064, 0.008, 0, 0, 0],
                                            'KRG': [0, 0.0039, 0.1406, 0.25, 0.3906, 0.7656, 0.8789],
                                            'PCGW': [0., np.nan, np.nan, 1., np.nan, np.nan, 3.0]
                                            }),
                   'SCALING': 'TWOPOINT',
                   }
    expected_file_as_list = """DESC This is first line of description
DESC and this is second line of description
GWTABLE
  SG  KRWG    KRG  PCGW
0.00 1.000 0.0000   0.0
0.05 0.729 0.0039      
0.30 0.064 0.1406      
0.40 0.008 0.2500   1.0
0.50 0.000 0.3906      
0.70 0.000 0.7656      
0.75 0.000 0.8789   3.0

SCALING TWOPOINT
""".splitlines(keepends=True)
    
    relpm_method = NexusRelPermMethod(input_number=10, properties=relpm_props,
                                         file=None, model_unit_system=model.run_units,
                                         )

    expected_generated_nexus_file = NexusFile(location='new_method.dat',
                                              file_content_as_list=expected_file_as_list)
    expected_generated_nexus_file._file_modified_set(True)

    # Act
    model.relperm.add_method(relpm_method, new_file_name='new_method.dat', create_new_file=False)

    # Assert
    assert model.relperm.inputs[10] == relpm_method
    assert model.relperm.inputs[10].properties['SCALING'] == 'TWOPOINT'
    assert model.relperm.inputs[10].input_number == 10
    assert model.relperm.inputs[10].file == expected_generated_nexus_file
    assert model.model_files is not None
    assert model.model_files.relperm_files is not None
    assert model.model_files.relperm_files[10] == expected_generated_nexus_file

def test_add_wrong_type_of_dynamic_method():
    # Arrange
    model = NexusSimulator(origin='new_model.fcs', assume_loaded=True, start_date='01/01/2020', )

    hydraulic_method = NexusHydraulicsMethod(input_number=10, properties={'ALQ': 1000},
                                             file=None, model_unit_system=model.run_units,
                                             )

    # Act + Assert
    with pytest.raises(Exception) as e_info:
        model.relperm.add_method(hydraulic_method, new_file_name='new_method.dat', create_new_file=False)
    assert str(e_info.value) == "Expected method of type NexusRelPermMethod, but got NexusHydraulicsMethod."
