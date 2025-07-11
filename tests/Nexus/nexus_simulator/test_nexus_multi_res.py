import os.path

from ResSimpy import NexusSimulator
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
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

    include_file_contents_1 = field_1_content.splitlines(keepends=True)
    include_file_contents_2 = field_2_content.splitlines(keepends=True)
    include_file_contents_3 = field_3_content.splitlines(keepends=True)
    
    expected_field_1_file = FcsNexusFile(
        location=field_1_path,
        file_content_as_list=include_file_contents_1,
        include_locations=[],
        origin=None,
        include_objects=None
    )
    expected_field_2_file = FcsNexusFile(
        location=field_2_path,
        file_content_as_list=include_file_contents_2,
        include_locations=[],
        origin=None,
        include_objects=None
    )
    expected_field_3_file = FcsNexusFile(
        location=field_3_path,
        file_content_as_list=include_file_contents_3,
        include_locations=[],
        origin=None,
        include_objects=None
    )

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_path: test_fcs_file,
            field_1_path: field_1_content,
            field_2_path: field_2_content,
            field_3_path: field_3_content,
            
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    field_1_expected_model = NexusSimulator(field_1_path)
    field_2_expected_model = NexusSimulator(field_2_path)
    field_3_expected_model = NexusSimulator(field_3_path)

    expected_reservoirs_dict = {
        'RUM': field_1_expected_model,
        'GAW': field_2_expected_model,
        'BURG': field_3_expected_model,
    }

    # Act
    result = NexusSimulator(fcs_path)
    
    # Assert
    assert result.is_multi_reservoir is True
    assert result.reservoir_paths == {'RUM': field_1_path, 'GAW': field_2_path, 'BURG': field_3_path}
    assert result.multi_reservoirs['RUM'] == expected_reservoirs_dict['RUM']
    assert result.multi_reservoirs == expected_reservoirs_dict
    assert len(recwarn) == 1
    assert recwarn[0].category == UserWarning
    assert str(recwarn[0].message) == "Multi-reservoir models are partially supported. " \
                                       "Some features may not work as expected."
