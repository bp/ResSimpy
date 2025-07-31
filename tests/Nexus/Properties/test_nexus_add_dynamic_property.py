from ResSimpy import NexusSimulator
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusHydraulicsMethod import NexusHydraulicsMethod


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
