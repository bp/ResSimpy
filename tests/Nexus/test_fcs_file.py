import os
import pathlib
from io import StringIO
from unittest.mock import Mock, MagicMock

import pytest

from ResSimpy import NexusSimulator
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import generic_fcs, get_fake_nexus_simulator


def test_fcs_file(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
RUN_UNITS ENGLISH
DATEFORMAT DD/MM/YYYY
GRID_FILES
	 STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
	 OPTIONS /root_folder/nexus_data/nexus_data/mp2020_ref_options_reg_update.dat'''

    structured_grid_contents = 'structured_grid_contents'
    options_file_contents = 'options_file_contents'

    fcs_path = '/root_folder/test_fcs.fcs'
    root_folder = '/root_folder'
    structured_grid_path = os.path.join(root_folder, 'nexus_data/mp2020_structured_grid_1_reg_update.dat')
    options_file_path = '/root_folder/nexus_data/nexus_data/mp2020_ref_options_reg_update.dat'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/root_folder/test_fcs.fcs': fcs_content,
            structured_grid_path: structured_grid_contents,
            options_file_path: options_file_contents
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)

    expected_includes = [structured_grid_path, options_file_path]
    expected_structured_grid_file = NexusFile(location=structured_grid_path,
                                              origin=fcs_path, include_locations=None,
                                              include_objects=None, file_content_as_list=[structured_grid_contents])
    expected_structured_grid_file._location_in_including_file = 'nexus_data/mp2020_structured_grid_1_reg_update.dat'

    expected_options_file = NexusFile(location=options_file_path,
                                      include_locations=None, origin=fcs_path, include_objects=None,
                                      file_content_as_list=[options_file_contents])

    expected_fcs_file = FcsNexusFile(location=fcs_path, origin=None,
                                     include_objects=[expected_structured_grid_file, expected_options_file],
                                     file_content_as_list=[
                                         'DESC reservoir1\n', 'RUN_UNITS ENGLISH\n', 'DATEFORMAT DD/MM/YYYY\n',
                                         'GRID_FILES\n',
                                         '	 STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat\n',
                                         '	 OPTIONS /root_folder/nexus_data/nexus_data/mp2020_ref_options_reg_update.dat'],
                                     structured_grid_file=expected_structured_grid_file,
                                     options_file=expected_options_file, include_locations=expected_includes)
    expected_fcs_file.files_info = [(fcs_path, None, None),
                                    (structured_grid_path, None, None),
                                    (options_file_path, None, None)]

    expected_fcs_file._location_in_including_file = '/root_folder/test_fcs.fcs'

    # Act
    fcs_file = FcsNexusFile.generate_fcs_structure(fcs_path)

    # Assert
    assert fcs_file.file_content_as_list == expected_fcs_file.file_content_as_list
    assert fcs_file.structured_grid_file == expected_fcs_file.structured_grid_file == expected_structured_grid_file
    assert fcs_file.options_file == expected_fcs_file.options_file == expected_options_file
    assert fcs_file == expected_fcs_file


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
                         'nexus_data/nexus_data/mp2017hm_ref_equil_03.dat']
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

    equil_files = {1: expected_equil_1, 2: expected_equil_2}
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
    assert result.multi_reservoir_files == {}


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
        'nexus_data/nexus_data/mp2017hm_ref_equil_02.dat',
        'nexus_data/mp2020_structured_grid_1_reg_update.dat',
        'nexus_data/nexus_data/mp2020_ref_options_reg_update.dat',
        'wells.dat',
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
    ]

    model = get_fake_nexus_simulator(mocker=mocker, fcs_file_path='test_fcs.fcs', mock_open=False)

    # Act
    from_list, to_list = model.model_files.get_full_network()

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


def test_move_model_files_duplicate_file(mocker):
    # Arrange
    fcs_path = 'test_fcs.fcs'

    fcs_content = '''DESC reservoir1
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            INITIALIZATION_FILES
        	 STRUCTURED_GRID nexus_data/structured_grid.dat
        	  RECURRENT_FILES
            RUNCONTROL nexus_data/nexus_data/runcontrol.dat
        	 '''

    structured_grid_content = '''INCLUDE grid.dat
    some other content
    INCLUDE grid.dat'''

    run_control_content = "START 01/01/2024"

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            'nexus_data/structured_grid.dat': structured_grid_content,
            'nexus_data/nexus_data/runcontrol.dat': run_control_content,
            os.path.join('nexus_data', 'grid.dat'): 'grid_inc content',
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    fcs = FcsNexusFile.generate_fcs_structure(fcs_path)

    new_include_loc = 'nexus_data'
    expected_files = ['structured_grid_grid.dat', 'structured_grid.dat', 'runcontrol.dat']
    expected_files = [os.path.join('/data', new_include_loc, x) for x in expected_files]
    expected_files.append('/data/new_fcs.fcs')

    # Mock out the file exists
    file_calls = []

    def file_exists_side_effect(file_name):
        if file_name in file_calls:
            return True
        else:
            return False

    file_exists_mock = MagicMock(side_effect=file_exists_side_effect)
    mocker.patch('os.path.exists', file_exists_mock)

    def append_file_calls_side_effect(file_name, write_mode):
        if write_mode == 'w':
            file_calls.append(file_name)
        return MagicMock()

    writing_mock_open = MagicMock(side_effect=append_file_calls_side_effect)
    mocker.patch("builtins.open", writing_mock_open)

    # mock out makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)

    # Act
    fcs.move_model_files(new_file_path='/data/new_fcs.fcs', new_include_file_location=new_include_loc)

    # Assert
    list_of_write_names = [call.args[0] for call in writing_mock_open.mock_calls if "'w')" in str(call)]
    # one write call per file
    assert list_of_write_names == expected_files
    assert len(list_of_write_names) == 4


def test_move_model_files_skipped_array(mocker):
    # Arrange
    fcs_path = 'test_fcs.fcs'

    fcs_content = '''DESC reservoir1
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            INITIALIZATION_FILES
        	 STRUCTURED_GRID nexus_data/structured_grid.dat
        	  RECURRENT_FILES
            RUNCONTROL nexus_data/nexus_data/runcontrol.dat
        	 '''

    structured_grid_content = '''some content
    KX VALUE
    INCLUDE arrays.dat'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
            'nexus_data/structured_grid.dat': structured_grid_content,
            os.path.join('nexus_data', 'arrays.dat'): 'array_content',
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    fcs = FcsNexusFile.generate_fcs_structure(fcs_path)

    new_include_loc = 'nexus_data'
    expected_files = ['structured_grid_arrays.dat', 'structured_grid.dat', 'runcontrol.dat']
    expected_files = [os.path.join('/data', new_include_loc, x) for x in expected_files]
    expected_files.append('/data/new_fcs.fcs')

    expected_fcs_content = f'''DESC reservoir1
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            INITIALIZATION_FILES
        	 STRUCTURED_GRID {expected_files[1]}
        	  RECURRENT_FILES
            RUNCONTROL {expected_files[2]}
        	 '''

    expected_grid_content = f'''some content
    KX VALUE
    INCLUDE {expected_files[0]}'''

    # Mock out the file exists
    file_calls = []

    def file_exists_side_effect(file_name):
        if file_name in file_calls:
            return True
        else:
            return False

    file_exists_mock = MagicMock(side_effect=file_exists_side_effect)
    mocker.patch('os.path.exists', file_exists_mock)

    append_writes_files_mocker = mocker.mock_open()

    def append_file_calls_side_effect(file_name, mode):
        if mode == 'w':
            file_calls.append(file_name)
        if mode == 'r' and file_name == os.path.join('nexus_data', 'arrays.dat'):
            return StringIO('array_content')
        return append_writes_files_mocker.return_value

    writing_mock_open = MagicMock(side_effect=append_file_calls_side_effect)
    mocker.patch("builtins.open", writing_mock_open)

    # mock out makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)

    # Act
    fcs.move_model_files(new_file_path='/data/new_fcs.fcs', new_include_file_location=new_include_loc)

    # Assert
    list_of_write_names = [call.args[0] for call in writing_mock_open.mock_calls if "'w')" in str(call)]
    # get the data written to files
    list_of_write_contents = [call.args[0] for call in append_writes_files_mocker.mock_calls if "().write" in str(call)]
    # one write call per file
    assert list_of_write_names == expected_files
    assert list_of_write_contents == ['array_content', expected_grid_content, '', expected_fcs_content]
    assert len(list_of_write_names) == 4


def test_fcs_repr(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY
    INITIALIZATION_FILES
     EQUIL Method 1 nexus_data/nexus_data/mp2017hm_ref_equil_01.dat
     EQUIL NORPT Method 2 nexus_data/nexus_data/mp2017hm_ref_equil_02.dat
    STRUCTURED_GRID nexus_data/mp2020_structured_grid_1_reg_update.dat
     OPTIONS nexus_data/nexus_data/mp2020_ref_options_reg_update.dat
     WELLS SET 1 wells.dat
     HYD NORPT METHOd 3 hyd.dat'''

    fcs_path = 'test_fcs.fcs'

    expected_result = """fcs file location: test_fcs.fcs
\tFCS file contains:
\t\tstructured_grid_file: nexus_data/mp2020_structured_grid_1_reg_update.dat
\t\toptions_file: nexus_data/nexus_data/mp2020_ref_options_reg_update.dat
\t\tequil_files: 2
\t\twell_files: 1
\t\thyd_files: 1
"""

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_path: fcs_content,
            'nexus_data/nexus_data/mp2017hm_ref_equil_01.dat': 'equil content',

        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    mocker.patch("os.path.isfile", lambda x: True)

    fcs = FcsNexusFile.generate_fcs_structure(fcs_file_path=fcs_path)

    # Act
    result = repr(fcs)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize('overwrite_files', [True, False], ids=['overwrite_files', 'no_overwrite_files'])
def test_move_model_files_duplicate(mocker, overwrite_files):
    # Arrange
    fcs_path = 'test_fcs.fcs'

    fcs_content = '''DESC reservoir1
            RUN_UNITS ENGLISH
            DATEFORMAT DD/MM/YYYY
            INITIALIZATION_FILES
        	 EQUIL Method 1 nexus_data/nexus_data/equil.dat
        	 EQUIL Method 2 nexus_data/nexus_data/equil.dat
        	  RECURRENT_FILES
            RUNCONTROL nexus_data/nexus_data/runcontrol.dat
        	 '''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_fcs.fcs': fcs_content,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    fcs_file_exists = Mock(side_effect=lambda x: True)
    mocker.patch('os.path.isfile', fcs_file_exists)

    mocker.patch("os.listdir", return_value=['runcontrol.dat', 'equil.dat', 'equil.dat', 'new_fcs.fcs'])

    model = NexusSimulator(fcs_path)
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    new_include_loc = 'nexus_data'
    expected_files = ['runcontrol.dat', 'equil.dat', 'equil.dat']
    expected_files = [os.path.join('/data', new_include_loc, x) for x in expected_files]
    expected_files.append('/data/new_fcs.fcs')

    files_written = []

    # Mock out the file exists
    def file_exists_side_effect(file_name):
        if file_name in files_written:
            return True
        else:
            files_written.append(file_name)
            return False

    mocker.patch('os.path.exists', file_exists_side_effect)

    # mock out makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)

    # Act
    if overwrite_files:
        model.move_simulator_files(new_file_path='/data/new_fcs.fcs', new_include_file_location=new_include_loc,
                                   overwrite_files=overwrite_files)
    else:
        with pytest.raises(ValueError) as ve:
            model.move_simulator_files(new_file_path='/data/new_fcs.fcs', new_include_file_location=new_include_loc,
                                       overwrite_files=overwrite_files)

    # Assert
    if overwrite_files:
        list_of_write_names = [call.args[0] for call in writing_mock_open.mock_calls if "'w')" in str(call)]
        assert list_of_write_names == expected_files
        assert len(list_of_write_names) == 4
    else:
        assert str(ve.value) == f'File already exists at {expected_files[2]} and overwrite_file set to False'


def test_fcs_file_user(mocker):
    # Arrange
    fcs_content = '''DESC reservoir1
    RUN_UNITS ENGLISH
    DATEFORMAT DD/MM/YYYY'''

    fcs_path = 'test_fcs.fcs'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            fcs_path: fcs_content,

        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    mocker.patch("os.path.isfile", lambda x: True)
    # Mock out pathlib and stat libraries
    owner_mock = mocker.MagicMock(return_value='USER')
    group_mock = mocker.MagicMock(return_value='GROUP')
    mocker.patch.object(pathlib.Path, 'owner', owner_mock)
    mocker.patch.object(pathlib.Path, 'group', group_mock)

    fcs = FcsNexusFile.generate_fcs_structure(fcs_file_path=fcs_path)

    # Act
    result = fcs.linked_user

    # Assert
    assert result == 'USER:GROUP'