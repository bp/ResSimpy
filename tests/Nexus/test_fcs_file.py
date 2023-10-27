import os
from unittest.mock import Mock, MagicMock

import pytest
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import generic_fcs, check_file_read_write_is_correct


def test_fcs_file(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
RUN_UNITS ENGLISH
DATEFORMAT DD/MM/YYYY
GRID_FILES
	 STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat'''

    fcs_path = '/root_folder/test_fcs.fcs'
    root_folder = '/root_folder'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/root_folder/test_fcs.fcs': fcs_content,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    structured_grid_path = os.path.join(root_folder, 'nexus_data/mp2020_structured_grid_1_reg_update.dat')
    options_file_path = os.path.join(root_folder, 'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat')
    expected_includes = [structured_grid_path, options_file_path]
    expected_structured_grid_file = NexusFile(location=structured_grid_path,
                                              origin=fcs_path, include_locations=None,
                                              include_objects=None, file_content_as_list=None)

    expected_options_file = NexusFile(location=options_file_path,
                                      include_locations=None, origin=fcs_path, include_objects=None,
                                      file_content_as_list=None)
    expected_fcs_file = FcsNexusFile(location=fcs_path, origin=None,
                                     include_objects=[expected_structured_grid_file, expected_options_file],
                                     file_content_as_list=[
                                         'DESC reservoir1\n', 'RUN_UNITS ENGLISH\n', 'DATEFORMAT DD/MM/YYYY\n',
                                         'GRID_FILES\n',
                                         '	 STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat\n',
                                         '	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat', ],
                                     structured_grid_file=expected_structured_grid_file,
                                     options_file=expected_options_file, include_locations=expected_includes)
    expected_fcs_file.files_info = [(fcs_path, None, None),
                                    (structured_grid_path, None, None),
                                    (options_file_path, None, None)]
    # Act
    fcs_file = FcsNexusFile.generate_fcs_structure(fcs_path)
    # Assert
    assert fcs_file.file_content_as_list == expected_fcs_file.file_content_as_list
    assert fcs_file == expected_fcs_file
    assert fcs_file.structured_grid_file == expected_fcs_file.structured_grid_file


def test_fcs_file_multiple_methods(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    INITIALIZATION_FILES
	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat
	 EQUIL Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat
	 EQUIL Method 3 nexus_data/nexus_data/mp2017hm_ref_equil_03.dat'''

    fcs_path = 'test_fcs.fcs'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    expected_includes = ['nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                         'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                         'nexus_data/nexus_data/mp2017hm_ref_equil_03.dat', ]
    expected_equil_1 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_equil_2 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_equil_3 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_03.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_fcs_file = FcsNexusFile(
        location=fcs_path, origin=None,
        include_objects=[expected_equil_1, expected_equil_2, expected_equil_3],
        file_content_as_list=[
            'DESC reservoir1\n', '    RUN_UNITS ENGLISH\n', '    DATEFORMAT DD/MM/YYYY\n',
            '    INITIALIZATION_FILES\n',
            '	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat\n',
            '	 EQUIL Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat\n',
            '	 EQUIL Method 3 nexus_data/nexus_data/mp2017hm_ref_equil_03.dat'],
        equil_files={1: expected_equil_1, 2: expected_equil_2, 3: expected_equil_3},
        include_locations=expected_includes,
    )

    expected_fcs_file.files_info = [(fcs_path, None, None),
                                    ('nexus_data/nexus_data/mp2017hm_ref_equil_01.dat', None, None),
                                    ('nexus_data/nexus_data/mp2017hm_ref_equil_02.dat', None, None),
                                    ('nexus_data/nexus_data/mp2017hm_ref_equil_03.dat', None, None)]
    # Act
    result = FcsNexusFile.generate_fcs_structure(fcs_path)
    # Assert
    assert result == expected_fcs_file


def test_fcs_file_all_methods(mocker):
    # Currently this test doesn't cover ensuring that the include file object gets into the fcs file.
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    INITIALIZATION_FILES
	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat
	 EQUIL NORPT Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat
    STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat
     INCLUDE wells.inc
     HYD NORPT METHOd 3 hyd.dat'''
    include_contents = 'WELLS SET 1 wells.dat'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            'wells.inc': include_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    fcs_path = 'test_fcs.fcs'
    expected_includes = ['nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                         'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                         'nexus_data/mp2020_structured_grid_1_reg_update.dat',
                         'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
                         # 'wells.inc',  # TODO fix this test to ensure the include files get included here
                         'wells.dat',
                         'hyd.dat']
    expected_equil_1 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_equil_2 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                                 origin=fcs_path, include_locations=None,
                                 include_objects=None, file_content_as_list=None)
    expected_structured_grid_file = NexusFile(location='nexus_data/mp2020_structured_grid_1_reg_update.dat',
                                              origin=fcs_path, include_locations=None,
                                              include_objects=None, file_content_as_list=None)
    expected_options_file = NexusFile(location='nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
                                      include_locations=None,
                                      origin=fcs_path, include_objects=None, file_content_as_list=None)
    expected_wells_file = NexusFile(location='wells.dat', origin=fcs_path, include_locations=None, include_objects=None,
                                    file_content_as_list=None)
    expected_hyd_method_file = NexusFile(location='hyd.dat', origin=fcs_path, include_locations=None,
                                         include_objects=None, file_content_as_list=None)

    equil_files = {1: expected_equil_1, 2: expected_equil_2, }
    include_objects = [expected_equil_1, expected_equil_2, expected_structured_grid_file, expected_options_file,
                       expected_wells_file, expected_hyd_method_file]
    expected_fcs_contents_as_list = ['DESC reservoir1\n',
                                     '    RUN_UNITS ENGLISH\n',
                                     '    DATEFORMAT DD/MM/YYYY\n',
                                     '    INITIALIZATION_FILES\n',
                                     '	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat\n',
                                     '	 EQUIL NORPT Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat\n',
                                     '    STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat\n',
                                     '	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat\n',
                                     'WELLS SET 1 wells.dat',
                                     '     HYD NORPT METHOd 3 hyd.dat',
                                     ]
    expected_fcs_file = FcsNexusFile(location=fcs_path, origin=None, include_objects=include_objects,
                                     equil_files=equil_files, structured_grid_file=expected_structured_grid_file,
                                     options_file=expected_options_file, well_files={1: expected_wells_file},
                                     hyd_files={3: expected_hyd_method_file},
                                     file_content_as_list=expected_fcs_contents_as_list,
                                     include_locations=expected_includes)
    expected_fcs_file.files_info = [(fcs_path, None, None),
                                    ('nexus_data/nexus_data/mp2017hm_ref_equil_01.dat', None, None),
                                    ('nexus_data/nexus_data/mp2017hm_ref_equil_02.dat', None, None),
                                    ('nexus_data/mp2020_structured_grid_1_reg_update.dat', None, None),
                                    ('nexus_data/nexus_data/mp2020_ref_options_reg_update.dat', None, None),
                                    ('wells.dat', None, None),
                                    ('hyd.dat', None, None)]

    # Act
    result = FcsNexusFile.generate_fcs_structure(fcs_file_path=fcs_path)

    # Assert
    assert result.file_content_as_list == expected_fcs_file.file_content_as_list
    assert result == expected_fcs_file


def test_get_full_network(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    INITIALIZATION_FILES
	 EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat
	 EQUIL Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat
    STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat
     INCLUDE wells.inc
     HYD METHOd 3 hyd.dat'''
    include_contents = 'WELLS SET 1 wells.dat'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            'wells.inc': include_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)
    fcs_path = 'test_fcs.fcs'

    expected_to_list = [
        'test_fcs.fcs',
        'nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
        'nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
        'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
        'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
        'nexus_data/mp2020_structured_grid_1_reg_update.dat',
        'nexus_data/mp2020_structured_grid_1_reg_update.dat',
        'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
        'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
        'wells.dat',
        'wells.dat',
        'hyd.dat',
        'hyd.dat',
    ]

    expected_from_list = [
        None,
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
        'test_fcs.fcs',
    ]

    equil1 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_01.dat',
                       origin=fcs_path, include_locations=None,
                       include_objects=None, file_content_as_list=None)
    equil_2 = NexusFile(location='nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
                        origin=fcs_path, include_locations=None,
                        include_objects=None, file_content_as_list=None)
    structured_grid_file = NexusFile(location='nexus_data/mp2020_structured_grid_1_reg_update.dat',
                                     origin=fcs_path, include_locations=None,
                                     include_objects=None, file_content_as_list=None)
    options_file = NexusFile(location='nexus_data/nexus_data/mp2020_ref_options_reg_update.dat', include_locations=None,
                             origin=fcs_path, include_objects=None, file_content_as_list=None)
    wells_file = NexusFile(location='wells.dat', origin=fcs_path, include_locations=None, include_objects=None,
                           file_content_as_list=None)
    hyd_method_file = NexusFile(location='hyd.dat', origin=fcs_path, include_locations=None,
                                include_objects=None, file_content_as_list=None)

    equil_files = {1: equil1, 2: equil_2, }
    include_objects = [equil1, equil_2, structured_grid_file, options_file,
                       wells_file, hyd_method_file]
    fcs_contents_as_list = ['DESC reservoir1',
                            '    RUN_UNITS ENGLISH',
                            '    DATEFORMAT DD/MM/YYYY',
                            '    INITIALIZATION_FILES',
                            '	 EQUIL Method 1 ',
                            equil1,
                            '',
                            '	 EQUIL Method 2 ',
                            equil_2,
                            '',
                            '    STRUCTURED_GRID ',
                            structured_grid_file,
                            '',
                            '	 OPTIONS ',
                            options_file,
                            '',
                            '     ',
                            'WELLS SET 1 ',
                            wells_file,
                            '',
                            '',
                            '     HYD METHOd 3 ',
                            hyd_method_file,
                            '',
                            ]
    compiled_fcs_file = FcsNexusFile(location=fcs_path, origin=None, include_objects=include_objects,
                                     equil_files=equil_files, structured_grid_file=structured_grid_file,
                                     options_file=options_file, well_files={1: wells_file},
                                     hyd_files={3: hyd_method_file},
                                     file_content_as_list=fcs_contents_as_list, include_locations=[])

    # Act
    from_list, to_list = compiled_fcs_file.get_full_network()

    # Assert
    assert to_list == expected_to_list
    assert from_list == expected_from_list

def test_update_fcs_file(mocker):
    # Arrange
    fcs_file_class = generic_fcs(mocker)
    # flag one of the files as modified and give them some content
    setattr(fcs_file_class.equil_files[2], '_File__file_modified', True)
    fcs_file_class.equil_files[2].file_content_as_list = ['some\n', 'new\n', 'data\n']
    setattr(fcs_file_class.structured_grid_file, '_File__file_modified', True)
    fcs_file_class.structured_grid_file.file_content_as_list = ['structured grid new data']
    expected_equil_contents = 'some\nnew\ndata\n'
    expected_grid_contents = 'structured grid new data'

    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Act
    fcs_file_class.update_model_files()

    # Assert
    # need to update this to check multiple files writes
    # Get all the calls to write() and check that the contents are what we expect
    list_of_writes = [call.args[0] for call in writing_mock_open.mock_calls if 'call().write' in str(call)]

    assert list_of_writes == [expected_grid_contents, expected_equil_contents]

    # Get all the calls to write() with a write 'w' as the last arg and check that the file name writes are correct
    list_of_write_names = [call.args[0] for call in writing_mock_open.mock_calls if "'w')" in str(call)]
    assert list_of_write_names == [fcs_file_class.structured_grid_file.location, fcs_file_class.equil_files[2].location]


@pytest.mark.parametrize('token, method_number, edited_line, new_line_content',
                         [
                             (  # basic test
                                     'ROCK', 1, 10,
                                     '	        ROCK Method 1 new_file.dat\n'
                             ),

                             (  # different methods
                                     'HYD', 3, 13,
                                     '         HYD METHOd 3 new_file.dat\n'
                             ),
                             (  # no method number
                                     'RUNCONTROL', None, 16,
                                     '            RUNCONTROL new_file.dat\n'
                             ),
                         ],
                         ids=['basic', 'different methods', 'no method_number'])
def test_update_file_path(mocker, token, method_number, edited_line, new_line_content):
    # Arrange
    fcs_file_class = generic_fcs(mocker)
    expected_fcs_content = fcs_file_class.file_content_as_list.copy()
    expected_fcs_content[edited_line] = new_line_content
    # Act
    fcs_file_class.change_file_path('new_file.dat', token, method_number)

    # Assert
    assert fcs_file_class.file_content_as_list == expected_fcs_content


def test_update_file_path_no_content(mocker):
    # Arrange
    fcs_file_class = generic_fcs(mocker)
    fcs_file_class.file_content_as_list = None
    # Act
    with pytest.raises(ValueError) as ve:
        fcs_file_class.change_file_path('new_file.dat', 'ROCK', 1)
    assert str(ve.value) == 'No file content to change file path on.'


def test_move_model_files(mocker):
    # Arrange
    fcs_path = 'test_fcs.fcs'

    fcs_content = '''DESC reservoir1
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            INITIALIZATION_FILES
        	 EQUIL Method 1 nexus_data/nexus_data/equil_01.dat
        	 EQUIL Method 2 nexus_data/nexus_data/equil_02.dat
        	  RECURRENT_FILES
            RUNCONTROL nexus_data/nexus_data/runcontrol.dat
            WELLS Set 1 nexus_data/nexus_data/wells.dat
            SURFACE Network 1 nexus_data/nexus_data/surface.dat
        	 '''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    fcs = FcsNexusFile.generate_fcs_structure(fcs_path)
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    new_include_loc = 'nexus_data'
    expected_files = ['runcontrol.dat', 'equil_01.dat', 'equil_02.dat', 'surface.dat', 'wells.dat']
    expected_files = [os.path.join('/data', new_include_loc, x) for x in expected_files]
    expected_files.append('/data/new_fcs.fcs')

    # Mock out the file exists
    file_exists_mock = MagicMock(side_effect=lambda x: False)
    mocker.patch('os.path.exists', file_exists_mock)

    # mock out makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)

    # Act
    fcs.move_model_files(new_file_path='/data/new_fcs.fcs', new_include_file_location=new_include_loc)

    # Assert
    list_of_write_names = [call.args[0] for call in writing_mock_open.mock_calls if "'w')" in str(call)]
    # one write call per file
    assert list_of_write_names == expected_files
    assert len(list_of_write_names) == 6
