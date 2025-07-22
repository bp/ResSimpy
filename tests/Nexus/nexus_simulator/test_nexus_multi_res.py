import os.path

from ResSimpy import NexusSimulator
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.NexusWell import NexusWell
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusWells import NexusWells
from tests.multifile_mocker import mock_multiple_files


def test_multi_reservoir_handling(mocker, recwarn):
    # Arrange
    # Current development stage expects to throw a warning describing partial handling of multires models
    # We should also expect the reservoir files to be added to the model's reservoir list.

    test_fcs_file = """! Multireservoir network connection
    
    RUN_UNITS METBAR
    
    DEFAULT_UNITS METBAR
    
    DATEFORMAT DD/MM/YYYY
    
    RESERVOIR  res_1  reservoir_1.fcs
    
    RESERVOIR res_2  reservoir_2.fcs
    
    RESERVOIR res_3  reservoir_3.fcs

    SURFACE Method 1 surface.dat
    
    RUNCONTROL runcontrol.dat
    """

    fcs_path = '/this/is/a/test/path/test.fcs'
    base_dir = os.path.dirname(fcs_path)
    field_1_path = os.path.join(base_dir, 'reservoir_1.fcs')
    field_2_path = os.path.join(base_dir, 'reservoir_2.fcs')
    field_3_path = os.path.join(base_dir, 'reservoir_3.fcs')

    field_1_content = """! Field 1 content
    RUN_UNITS METBAR
    DEFAULT_UNITS METBAR
    
    DATEFORMAT DD/MM/YYYY
    GRID_FILES
    STRUCTURED_GRID nexus_data/res_1_grid.dat

    PVT_FILES
    PVT Method 1 nexus_data/res_1_pvt.dat
    
    RECURRENT_FILES
    WELLS SET 1   res_1_wells.dat
    SURFACE Network 1 res_1_surface.dat

    """
    field_2_content = field_1_content.replace('res_1', 'res_2')
    field_3_content = field_1_content.replace('res_1', 'res_3')

    submodel_wells_file = os.path.join(base_dir, 'res_1_wells.dat')
    submodel_wells_content = """
    TIME 01/01/2020
    WELLSPEC WELL1
    IW JW L RADW
    1  2  3  4.5
    6 7 8   9.11
    """
    submodel_surface_file = os.path.join(base_dir, 'res_1_surface.dat')
    submodel_surface_content = """
    TIME 01/01/2020
    WELLS 
    NAME STREAM
    WELL1 PRODUCER
    ENDWELLS
    """
    
    expected_submodel_wells = [NexusWell(well_name='WELL1',
                                         completions=[
                                             NexusCompletion(date='01/01/2020', i=1, j=2, k=3, well_radius=4.5,
                                                             date_format=DateFormat.DD_MM_YYYY,
                                                             unit_system=UnitSystem.METBAR, start_date=''),
                                             NexusCompletion(date='01/01/2020', i=6, j=7, k=8, well_radius=9.11,
                                                             date_format=DateFormat.DD_MM_YYYY,
                                                             unit_system=UnitSystem.METBAR, start_date='')],
                                         unit_system=UnitSystem.METBAR, parent_wells_instance=None,
    )]

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_path: test_fcs_file,
            field_1_path: field_1_content,
            field_2_path: field_2_content,
            field_3_path: field_3_content,
            os.path.join(base_dir, 'nexus_data/res_1_grid.dat'): 'NX NY NZ\n 10 10 10\n',
            submodel_wells_file: submodel_wells_content,
            submodel_surface_file: submodel_surface_content,
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
        'res_1': field_1_expected_model,
        'res_2': field_2_expected_model,
        'res_3': field_3_expected_model,
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
                                           multi_reservoir_files={'res_1': field_1_expected_model.model_files,
                                                                  'res_2': field_2_expected_model.model_files,
                                                                  'res_3': field_3_expected_model.model_files,
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
    assert result.reservoir_paths == {'res_1': field_1_path, 'res_2': field_2_path, 'res_3': field_3_path}
    assert result.multi_reservoirs['res_1'].model_files == expected_reservoirs_dict['res_1'].model_files
    assert result.multi_reservoirs['res_2'].model_files == expected_reservoirs_dict['res_2'].model_files
    assert result.multi_reservoirs['res_3'].model_files == expected_reservoirs_dict['res_3'].model_files

    # calls to get_flat_list_str_file to ensure file line locations are loaded correctly
    result.model_files.multi_reservoir_files['res_1'].structured_grid_file.get_flat_list_str_file
    result.model_files.multi_reservoir_files['res_2'].structured_grid_file.get_flat_list_str_file
    result.model_files.multi_reservoir_files['res_3'].structured_grid_file.get_flat_list_str_file
    assert (result.model_files.multi_reservoir_files['res_1'] ==
            expected_multires_files.multi_reservoir_files['res_1'])
    assert (result.model_files.multi_reservoir_files['res_2'] ==
            expected_multires_files.multi_reservoir_files['res_2'])
    assert (result.model_files.multi_reservoir_files['res_3'] ==
            expected_multires_files.multi_reservoir_files['res_3'])

    result.model_files.runcontrol_file.get_flat_list_str_file
    assert result.model_files.runcontrol_file == expected_multires_files.runcontrol_file

    assert result.model_files.files_info == expected_multires_files.files_info

    assert result.model_files.surface_files[1] == expected_multires_files.surface_files[1]

    assert result.model_files == expected_multires_files

    # test one of the subreservoir models for correct loading of grid.
    assert result.multi_reservoirs['res_1'].grid.range_x == 10
    assert result.multi_reservoirs['res_1'].grid.range_y == 10
    assert result.multi_reservoirs['res_1'].grid.range_z == 10

    matching_warnings = [x for x in recwarn if expected_warning_message in str(x.message)]
    assert len(matching_warnings) == 1

    # ensure the submodels don't have multires set
    assert result.model_files.multi_reservoir_files['res_1'].multi_reservoir_files == {}
    assert result.multi_reservoirs['res_1'].is_multi_reservoir is False

    assert (result.multi_reservoirs['res_1'].model_files.well_files[1].location ==
            os.path.join(base_dir, 'res_1_wells.dat'))
    assert result.multi_reservoirs['res_1'].wells.get_all() == expected_submodel_wells
