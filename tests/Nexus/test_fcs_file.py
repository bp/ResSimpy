import pytest
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from tests.multifile_mocker import mock_multiple_files


def test_fcs_file(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
RUN_UNITS ENGLISH
DATEFORMAT DD/MM/YYYY
GRID_FILES
	 STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat'''


    fcs_path = 'test_fcs.fcs'
    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            }).return_value
        return mock_open
    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    expected_structured_grid_file = NexusFile(location='nexus_data/mp2020_structured_grid_1_reg_update.dat',
                                              origin=fcs_path, includes=None,
                                              includes_objects=None, file_content_as_list=None)
    expected_options_file = NexusFile(location='nexus_data/nexus_data/mp2020_ref_options_reg_update.dat', includes=None,
                                      origin=fcs_path, includes_objects=None, file_content_as_list=None)
    expected_fcs_file = FcsNexusFile(location=fcs_path, origin=None,
                                     includes_objects=[expected_structured_grid_file, expected_options_file],
                                     file_content_as_list=[
                                         'DESC reservoir1', 'RUN_UNITS ENGLISH', 'DATEFORMAT DD/MM/YYYY',
                                         'GRID_FILES', '	 STRUCTURED_GRID ', expected_structured_grid_file, '',
                                         '	 OPTIONS ', expected_options_file, '', ],
                                     structured_grid_file=expected_structured_grid_file,
                                     options_file=expected_options_file,
                                     )

    # Act
    fcs_file = FcsNexusFile.generate_fcs_structure(fcs_path)
    # Assert
    assert fcs_file == expected_fcs_file
    assert fcs_file.structured_grid_file == expected_fcs_file.structured_grid_file


@pytest.mark.parametrize("input_line, expected_result", [
    ('STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat\n',
     ['STRUCTURED_GRID ', 'NEXUSFILE', '']),
    ('STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat !comment',
     ['STRUCTURED_GRID ', 'NEXUSFILE', ' !comment']),
    ('STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat !nexus_data/mp2020_structured_grid_1_reg_update.dat',
     ['STRUCTURED_GRID ', 'NEXUSFILE', ' !nexus_data/mp2020_structured_grid_1_reg_update.dat']),
    ('\t    STRUCTURED_GRID \t  nexus_data/mp2020_structured_grid_1_reg_update.dat',
     ['\t    STRUCTURED_GRID \t  ', 'NEXUSFILE', '']),
    ], ids=['basic', 'with_comment', 'with filename in comment', 'weird tabbing'])
def test_line_as_nexus_list(input_line, expected_result):
    # Arrange
    path = "nexus_data/mp2020_structured_grid_1_reg_update.dat"
    structured_grid_file = NexusFile(location=path, origin=None, includes=None,
                                     includes_objects=None, file_content_as_list=None)
    expected_result = [x if x != 'NEXUSFILE' else structured_grid_file for x in expected_result]
    # Act
    result = FcsNexusFile.line_as_nexus_list(input_line, path, structured_grid_file)

    # Assert
    assert result == expected_result
