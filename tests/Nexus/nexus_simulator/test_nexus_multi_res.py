import os.path

from ResSimpy import NexusSimulator
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from tests.multifile_mocker import mock_multiple_files


def test_multi_reservoir_handling(mocker, recwarn):
    # Arrange
    # Current development stage expects to throw a warning describing partial handling of multires models
    # We should also expect the reservoir files to be added to the model's reservoir list.
    
    test_fcs_file = """! Multireservoir network connection
    
    RUN_UNITS METBAR
    
    DEFAULT_UNITS METBAR
    
    DATEFORMAT DD/MM/YYYY
    
    RESERVOIR  RUM  rumaila.fcs
    
    RESERVOIR GAW  ghawar.fcs
    
    RESERVOIR BURG  burgan.fcs

    SURFACE Method 1 surface.dat
    
    RUNCONTROL runcontrol.dat
    """
    
    fcs_path = '/this/is/a/test/path/test.fcs'
    base_dir = os.path.dirname(fcs_path)
    field_1_path = os.path.join(base_dir, 'rumaila.fcs')
    field_2_path = os.path.join(base_dir, 'ghawar.fcs')
    field_3_path = os.path.join(base_dir, 'burgan.fcs')
    
    field_1_content = """! Field 1 content
    RUN_UNITS METBAR
    DEFAULT_UNITS METBAR
    
    DATEFORMAT DD/MM/YYYY
    GRID_FILES
    STRUCTURED_GRID nexus_data/rum_grid.dat

    PVT_FILES
    PVT Method 1 nexus_data/rum_pvt.dat
    
    RECURRENT_FILES
    WELLS SET 1   rum_wells.dat
    
    """
    field_2_content = field_1_content.replace('rum', 'gaw')
    field_3_content = field_1_content.replace('rum', 'burg')
    
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_path: test_fcs_file,
            field_1_path: field_1_content,
            field_2_path: field_2_content,
            field_3_path: field_3_content,
            os.path.join(base_dir, 'nexus_data/rum_grid.dat'): 'NX NY NZ\n 10 10 10\n',
            
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    
    # patch uuid to avoid generating new UUIDs during the test
    uuid_mock_number = '12345678-1234-5678-1234-567812345678'
    mocker.patch('ResSimpy.FileOperations.File.uuid.uuid4', return_value=uuid_mock_number)
    
    field_1_expected_model = NexusSimulator(field_1_path)
    field_2_expected_model = NexusSimulator(field_2_path)
    field_3_expected_model = NexusSimulator(field_3_path)

    expected_reservoirs_dict = {
        'RUM': field_1_expected_model,
        'GAW': field_2_expected_model,
        'BURG': field_3_expected_model,
    }
    expected_warning_message = "Multi-reservoir models are partially supported. " \
                                       "Some features may not work as expected."
    
    expected_multires_surface_file = NexusFile(
        location=os.path.join(base_dir, 'surface.dat'),
        file_content_as_list=[],
        include_locations=[],
        origin=fcs_path,
        include_objects=[]
    )
    expected_multires_surface_file._location_in_including_file = 'surface.dat'
    
    expected_multires_runcontrol_file = NexusFile(
        location=os.path.join(base_dir, 'runcontrol.dat'),
        file_content_as_list=[],
        include_locations=[],
        origin=fcs_path,
        include_objects=[]
    )
    expected_multires_runcontrol_file._location_in_including_file = 'runcontrol.dat'
    expected_multires_runcontrol_file.get_flat_list_str_file

    expected_multires_files = FcsNexusFile(location=fcs_path,
                                           include_locations=[expected_multires_surface_file.location,
                                                              expected_multires_runcontrol_file.location],
                                           include_objects=[expected_multires_surface_file,
                                                            expected_multires_runcontrol_file],
                                           file_content_as_list=test_fcs_file.splitlines(keepends=True),
                                           origin=None,
                                           multi_reservoir_files={'RUM': field_1_expected_model.model_files,
                                                                  'GAW': field_2_expected_model.model_files,
                                                                  'BURG': field_3_expected_model.model_files,
                                                                  },
                                           runcontrol_file=expected_multires_runcontrol_file,
                                           surface_files={1: expected_multires_surface_file},

                                           )
    expected_multires_files.files_info = [(fcs_path, None, None),
                (expected_multires_surface_file.location, None, None),
                (expected_multires_runcontrol_file.location, None, None)]

    # Act
    result = NexusSimulator(fcs_path)

    # Assert
    assert result.is_multi_reservoir is True
    assert result.reservoir_paths == {'RUM': field_1_path, 'GAW': field_2_path, 'BURG': field_3_path}
    assert result.multi_reservoirs['RUM'].model_files == expected_reservoirs_dict['RUM'].model_files
    assert result.multi_reservoirs['GAW'].model_files == expected_reservoirs_dict['GAW'].model_files
    assert result.multi_reservoirs['BURG'].model_files == expected_reservoirs_dict['BURG'].model_files
    
    # calls to get_flat_list_str_file to ensure file line locations are loaded correctly
    result.model_files.multi_reservoir_files['RUM'].structured_grid_file.get_flat_list_str_file
    result.model_files.multi_reservoir_files['GAW'].structured_grid_file.get_flat_list_str_file
    result.model_files.multi_reservoir_files['BURG'].structured_grid_file.get_flat_list_str_file
    assert (result.model_files.multi_reservoir_files['RUM'] == 
            expected_multires_files.multi_reservoir_files['RUM'])
    assert (result.model_files.multi_reservoir_files['GAW'] == 
            expected_multires_files.multi_reservoir_files['GAW'])
    assert (result.model_files.multi_reservoir_files['BURG'] == 
            expected_multires_files.multi_reservoir_files['BURG'])

    result.model_files.runcontrol_file.get_flat_list_str_file
    assert result.model_files.runcontrol_file == expected_multires_files.runcontrol_file
    
    assert result.model_files.files_info == expected_multires_files.files_info
    
    assert result.model_files.surface_files[1] == expected_multires_files.surface_files[1]

    assert result.model_files == expected_multires_files

    matching_warnings = [x for x in recwarn if expected_warning_message in str(x.message)]
    assert len(matching_warnings) == 1
