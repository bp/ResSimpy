import os
import uuid
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from ResSimpy.Nexus.DataModels import FcsFile
from ResSimpy.Nexus.DataModels.FcsFile import FcsNexusFile
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusWells import NexusWells
from ResSimpy.Nexus.load_wells import load_wells

from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator, uuid_side_effect


def test_generate_file_include_structure_basic(mocker):
    # Arrange
    file_path = 'test_file_path.dat'
    test_file_contents = 'basic_file INCLUDE inc_file1.inc'
    include_file_contents = 'inc file contents'

    expected_includes_list = ['inc_file1.inc']
    expected_location = 'test_file_path.dat'
    expected_origin = None

    nexus_file_include1 = NexusFile(location='inc_file1.inc', include_locations=[], origin=file_path,
                                    include_objects=None, file_content_as_list=[include_file_contents])

    expected_file_content_as_list = ['basic_file INCLUDE inc_file1.inc']

    expected_nexus_file = NexusFile(location=expected_location, include_locations=expected_includes_list,
                                    origin=expected_origin, include_objects=[nexus_file_include1],
                                    file_content_as_list=expected_file_content_as_list)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
        }
                                        ).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)

    # Assert
    assert nexus_file.file_content_as_list == expected_nexus_file.file_content_as_list
    assert nexus_file == expected_nexus_file


def test_generate_file_include_structure_multiple_includes(mocker):
    # Arrange
    file_path = 'test_file_path.dat'
    test_file_contents = (
        '''basic_file INCLUDE inc_file1.inc
second_file INCLUDE inc_file2.inc''')
    include_file_contents = 'inc file contents'
    include_file_contents_2 = 'inc2 file contents'

    expected_includes_list = ['inc_file1.inc', 'inc_file2.inc']
    expected_location = 'test_file_path.dat'
    expected_origin = None

    nexus_file_include1 = NexusFile(location='inc_file1.inc', include_locations=[], origin=file_path,
                                    include_objects=None, file_content_as_list=[include_file_contents])
    nexus_file_include2 = NexusFile(location='inc_file2.inc', include_locations=[], origin=file_path,
                                    include_objects=None, file_content_as_list=[include_file_contents_2])
    expected_file_content_as_list = ['basic_file INCLUDE inc_file1.inc\n', 'second_file INCLUDE inc_file2.inc']

    expected_nexus_file = NexusFile(location=expected_location, include_locations=expected_includes_list,
                                    origin=expected_origin, include_objects=[nexus_file_include1, nexus_file_include2],
                                    file_content_as_list=expected_file_content_as_list)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
            'inc_file2.inc': include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)

    # Assert
    assert nexus_file.file_content_as_list == expected_nexus_file.file_content_as_list
    assert nexus_file == expected_nexus_file


def test_generate_file_include_structure_nested_includes(mocker):
    # Arrange
    file_path = 'test_file_path.dat'
    test_file_contents = 'basic_file INCLUDE inc_file1.inc something after'

    include_file_contents = 'inc file contents INCLUDE inc_file2.inc'
    include_file_contents_2 = 'inc2 file contents'

    expected_includes_list = ['inc_file1.inc']
    expected_location = 'test_file_path.dat'
    expected_origin = None

    nexus_file_include2 = NexusFile(location='inc_file2.inc', include_locations=[], origin='inc_file1.inc',
                                    include_objects=None, file_content_as_list=[include_file_contents_2])
    nexus_file_include1 = NexusFile(location='inc_file1.inc', include_locations=['inc_file2.inc'], origin=file_path,
                                    include_objects=[nexus_file_include2],
                                    file_content_as_list=['inc file contents INCLUDE inc_file2.inc'])

    expected_file_content_as_list = ['basic_file INCLUDE inc_file1.inc something after']

    expected_nexus_file = NexusFile(location=expected_location, include_locations=expected_includes_list,
                                    origin=expected_origin, include_objects=[nexus_file_include1],
                                    file_content_as_list=expected_file_content_as_list)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
            'inc_file2.inc': include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)

    # Assert
    assert nexus_file.file_content_as_list == expected_nexus_file.file_content_as_list
    assert nexus_file == expected_nexus_file


def test_generate_file_include_structure_origin_path(mocker):
    # Arrange
    file_path = '/origin/path/test_file_path.dat'
    test_file_contents = 'basic_file INCLUDE nexus_data/inc_file1.inc'
    include_file_contents = 'inc file contents INCLUDE inc_file2.inc'
    inc2_file_contents = 'second_file'
    include_full_file_path_1 = os.path.join('/origin/path', 'nexus_data/inc_file1.inc')
    include_full_file_path_2 = os.path.join('/origin/path', 'nexus_data', 'inc_file2.inc')
    expected_includes_list = [include_full_file_path_1]
    expected_location = '/origin/path/test_file_path.dat'

    nexus_file_include2 = NexusFile(location=include_full_file_path_2, include_locations=[],
                                    origin=include_full_file_path_1,
                                    include_objects=None, file_content_as_list=['second_file'])
    nexus_file_include2._location_in_including_file = 'inc_file2.inc'

    nexus_file_include1 = NexusFile(location=include_full_file_path_1, include_locations=[include_full_file_path_2],
                                    origin=file_path, include_objects=[nexus_file_include2],
                                    file_content_as_list=['inc file contents INCLUDE inc_file2.inc'])
    nexus_file_include1._location_in_including_file = 'nexus_data/inc_file1.inc'

    expected_nexus_file = NexusFile(location=expected_location, include_locations=expected_includes_list,
                                    origin=None, include_objects=[nexus_file_include1],
                                    file_content_as_list=['basic_file INCLUDE nexus_data/inc_file1.inc'])

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: test_file_contents,
            include_full_file_path_1: include_file_contents,
            include_full_file_path_2: inc2_file_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)

    # Assert
    assert nexus_file.include_objects[0].include_objects[0] == nexus_file_include2
    assert nexus_file.include_objects == [nexus_file_include1]
    assert nexus_file.file_content_as_list == expected_nexus_file.file_content_as_list
    assert nexus_file == expected_nexus_file


def test_iterate_line(mocker):
    # Arrange
    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid1', 'uuid2', 'parent_file'])

    expected_flat_list = ['fcs_file content', 'hello', 'world', 'extra', 'footer', 'second', 'includefile']
    '''
    ['fcs_file content',
    'hello', 'world', 'extra' 1 - 3
     'footer',                  4
     'second', 'includefile'    5 - 6
     ]
    '''
    include_file = NexusFile(location='inc_file1.inc', include_locations=[], origin='test_file.dat',
                             include_objects=None, file_content_as_list=['hello', 'world', 'extra'])
    include_file_2 = NexusFile(location='inc_file2.inc', include_locations=[], origin='test_file.dat',
                               include_objects=None, file_content_as_list=['second', 'includefile'])
    nested_list = ['fcs_file content', 'INCludE \t inc_file1.inc', 'footer', 'include inc_file2.inc']

    nexus_file = NexusFile(location='test_file.dat', include_locations=['inc_file1.inc', 'inc_file2.inc'], origin=None,
                           include_objects=[include_file, include_file_2], file_content_as_list=nested_list)

    expected_line_locations = [(0, 'parent_file'), (1, 'uuid1'), (4, 'parent_file'), (5, 'uuid2'), (7, 'parent_file')]

    # Act
    store_list = []
    for line in nexus_file.iterate_line(file_index=None):
        store_list.append(line)

    # Assert
    assert store_list == expected_flat_list
    assert nexus_file.line_locations == expected_line_locations


@pytest.mark.parametrize("max_depth, expected_results", [
    (0, ['fcs_file content', 'footer']),
    (1, ['fcs_file content', 'hello', 'world', 'footer']),
    (2, ['fcs_file content', 'hello', 'deeper', 'nesting', 'world', 'footer']),
    (None, ['fcs_file content', 'hello', 'deeper', 'nesting', 'world', 'footer'])
], ids=['0 depth', '1 layer', '2 layers', 'all layers'])
def test_iterate_line_nested(max_depth, expected_results):
    # Arrange
    inc_2 = NexusFile(location='inc2.inc', include_locations=[], origin='inc_file1.inc',
                      include_objects=None, file_content_as_list=['deeper', 'nesting'])
    include_file = NexusFile(location='inc_file1.inc', include_locations=[], origin='test_file.dat',
                             include_objects=[inc_2], file_content_as_list=['hello', 'include inc2.inc', 'world'])

    nested_list = ['fcs_file content', 'include inc_file1.inc', 'footer']
    nexus_file = NexusFile(location='test_file.dat', include_locations=['inc_file1.inc'], origin=None,
                           include_objects=[include_file], file_content_as_list=nested_list)

    # Act
    store_results = []
    for line in nexus_file.iterate_line(max_depth=max_depth):
        store_results.append(line)
    # Assert
    assert store_results == expected_results


@pytest.mark.parametrize("test_file_contents", [
    ('basic_file KH VAlUE Include nexus_data/inc_file1.inc'),
    ('basic_file KH VAlUE\n\n INCLUDE nexus_data/inc_file1.inc'),
    ('basic_file KH VAlUE !comment\n\n INCLUDE nexus_data/inc_file1.inc'),
    ('basic_file KH VAlUE\n\n INCLUDE nexus_data/inc_file1.inc\n\nVALUE 10'),
    ('basic_file KH VAlUE\n\n 10 \n\nKH VALUE INCLUDE\n\n nexus_data/inc_file1.inc'),
    ('basic_file \n\nKH CON 1\n\n \nVMOD 1 10 1 10 2 5 MULT\nINCLUDE nexus_data/inc_file1.inc'),
], ids=['basic_test', 'newline',
        'comment',
        'another_token', 'second_token', 'vmods'])
def test_generate_file_include_structure_skip_array(mocker, test_file_contents):
    # Arrange
    file_path = '/origin/path/test_file_path.dat'
    include_file_contents = 'inc file contents'
    include_full_file_path_1 = os.path.join('/origin/path', 'nexus_data/inc_file1.inc')

    nexus_file_include1 = NexusFile(location=include_full_file_path_1, include_locations=None,
                                    origin=file_path, include_objects=None,
                                    file_content_as_list=None, file_loading_skipped=True)
    nexus_file_include1._input_file_location = 'nexus_data/inc_file1.inc'
    nexus_file_include1._location_in_including_file = 'nexus_data/inc_file1.inc'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: test_file_contents,
            include_full_file_path_1: include_file_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_result = nexus_file_include1

    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path,
                                                           skip_arrays=True)

    # Assert
    assert len(nexus_file.include_objects) == 1
    assert nexus_file.file_loading_skipped is False
    assert nexus_file.include_objects[0].file_loading_skipped is True
    assert nexus_file.include_objects[0] == expected_result


@pytest.mark.parametrize("file_with_nested_grid_array_contents, expected_file_contents", [
    ("""C Corner point grid layout
C
NX     NY     NZ
112    95     233
RIGHTHANDED
C Origin (UTM coords)
C (X,Y)=(0.000000,0.000000)
C
C
ARRAYS
C
C Size of corner point grid (cols,rows,layers)
C 112    95     233
C
KX ZVAR
500 50 200
CORP VALUE
C    
1 2 3 234234 12313""",

     """C Corner point grid layout
C
NX     NY     NZ
112    95     233
RIGHTHANDED
C Origin (UTM coords)
C (X,Y)=(0.000000,0.000000)
C
C
ARRAYS
C
C Size of corner point grid (cols,rows,layers)
C 112    95     233
C
KX ZVAR
500 50 200
CORP VALUE
"""),

    ("""porosity value
12 38923 7439327 7234923723 9274
KX ZVAR
500 50 200
""",
     """porosity value\n""")
], ids=['basic case', 'exclude from start of file'])
def test_generate_file_include_structure_skip_file_with_nested_array(mocker: MockerFixture,
                                                                     file_with_nested_grid_array_contents: str,
                                                                     expected_file_contents: str):
    # Arrange
    file_path = '/origin/path/test_file_path.dat'
    parent_file_contents = 'INCLUDE nexus_data/inc_file1.inc'
    expected_include_file_path = os.path.join('/origin/path', 'nexus_data/inc_file1.inc')
    expected_file_contents_as_list = expected_file_contents.splitlines(keepends=True)

    expected_included_file = NexusFile(location=expected_include_file_path, include_locations=None,
                                       origin=file_path, include_objects=None,
                                       file_content_as_list=expected_file_contents_as_list)
    expected_included_file._location_in_including_file = 'nexus_data/inc_file1.inc'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: parent_file_contents,
            expected_include_file_path: file_with_nested_grid_array_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path,
                                                           skip_arrays=True)

    # Assert
    assert len(nexus_file.include_objects) == 1
    assert nexus_file.include_objects[0].file_content_as_list == expected_included_file.file_content_as_list
    assert nexus_file.include_objects[0] == expected_included_file


def test_generate_file_include_structure_not_skipping_file(mocker: MockerFixture):
    # Arrange
    file_contents = """POROSITY CON 0.31012
CORP VALUE INCLUDE nested/include/file/path.dat

KX ZVAR
500 50 200

KY MULT
1.1 KX

KZ CON 1
"""
    file_path = '/origin/path/test_file_path.dat'
    parent_file_contents = 'INCLUDE nexus_data/inc_file1.inc'
    expected_include_file_path = os.path.join('/origin/path', 'nexus_data/inc_file1.inc')
    nested_include_file_contents = 'another file'
    nested_include_file_location = 'nested/include/file/path.dat'
    expected_nested_include_file_path = os.path.join('/origin/path', 'nexus_data', nested_include_file_location)
    expected_nested_included_file = NexusFile(location=nested_include_file_location, include_locations=None,
                                              origin=expected_include_file_path, include_objects=None,
                                              file_content_as_list=['another file'])

    expected_included_file = NexusFile(location=expected_include_file_path,
                                       include_locations=[expected_nested_include_file_path],
                                       origin=file_path, include_objects=[expected_nested_included_file],
                                       file_content_as_list=file_contents.splitlines(keepends=True))
    expected_included_file._location_in_including_file = 'nexus_data/inc_file1.inc'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: parent_file_contents,
            expected_include_file_path: file_contents,
            expected_nested_include_file_path: nested_include_file_contents
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path,
                                                           skip_arrays=False)

    # Assert
    assert len(nexus_file.include_objects) == 1
    assert nexus_file.include_objects[0].file_content_as_list == expected_included_file.file_content_as_list
    assert nexus_file.include_objects[0].include_objects[0] == expected_nested_included_file
    assert nexus_file.include_objects[0] == expected_included_file


@pytest.mark.parametrize("test_file_contents, expected_results",
                         [('''       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5
       6 7 8   9.11''',
                           {'uuid1': [2],
                            'uuid2': [3]}),
                          ],
                         ids=['basic_test']
                         )
def test_file_object_locations(mocker, test_file_contents, expected_results):
    # Arrange
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_wells = NexusWells(model=dummy_model)

    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4',
                 side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5',
                              'uuid6', 'uuid7'])  # Mocking the object IDs

    mocker.patch.object(uuid, 'uuid4', side_effect=['file_uuid'])  # Mocking the file IDs

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'wells.dat': test_file_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    wells_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path='wells.dat',
                                                           skip_arrays=True, )

    # Act
    load_wells(wells_file, start_date='01/01/2012', default_units=UnitSystem.ENGLISH,
               model_date_format=DateFormat.DD_MM_YYYY, parent_wells_instance=dummy_wells)
    result = wells_file.object_locations

    # Assert
    assert result == expected_results


def test_line_locations_complex(mocker):
    # Arrange
    # We need 2 lots of the mocked out uuid one for init of the expected files and one set for the try statement
    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid_inc1', 'uuid_inc2', 'parent_file',
                                                    'uuid_inc1', 'uuid_inc2', 'parent_file'])

    file_path = 'test_file_path.dat'
    test_file_contents = (
        '''basic_file INCLUDE inc_file1.inc
some random words ! comment
second_file INCLUDE inc_file2.inc continuation''')
    include_file_contents = 'inc file contents\nsecond line in incfile'
    include_file_contents_2 = 'inc2 file contents\nmore content'

    expected_includes_list = ['inc_file1.inc', 'inc_file2.inc']
    expected_location = 'test_file_path.dat'
    expected_origin = None

    nexus_file_include1 = NexusFile(location='inc_file1.inc', include_locations=[], origin=file_path,
                                    include_objects=None,
                                    file_content_as_list=['inc file contents\n', 'second line in incfile'])
    nexus_file_include2 = NexusFile(location='inc_file2.inc', include_locations=[], origin=file_path,
                                    include_objects=None, file_content_as_list=['inc2 file contents\n', 'more content'])
    expected_file_content_as_list = ['basic_file INCLUDE inc_file1.inc\n', 'some random words ! comment\n',
                                     'second_file INCLUDE inc_file2.inc continuation', ]

    expected_line_locations = [(0, 'parent_file'), (1, 'uuid_inc1'), (3, 'parent_file'), (5, 'uuid_inc2'),
                               (7, 'parent_file')]

    expected_nexus_file = NexusFile(location=expected_location, include_locations=expected_includes_list,
                                    origin=expected_origin, include_objects=[nexus_file_include1, nexus_file_include2],
                                    file_content_as_list=expected_file_content_as_list)
    expected_nexus_file.__setattr__('line_locations', expected_line_locations)

    expected_flat_file_as_list = [
        'basic_file ',  # 0: parent
        'inc file contents\n',  # 1: include
        'second line in incfile',
        'some random words ! comment\n',  # 3: parent
        'second_file ',
        'inc2 file contents\n',  # 5: 2nd include
        'more content',
        ' continuation']  # 7: parent

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
            'inc_file2.inc': include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    flat_file = nexus_file.get_flat_list_str_file
    # Assert
    assert flat_file == expected_flat_file_as_list
    assert nexus_file == expected_nexus_file
    assert nexus_file.line_locations == expected_nexus_file.line_locations


def test_line_locations_nested(mocker):
    # Arrange
    # We need 2 lots of the mocked out uuid one for init of the expected files and one set for the try statement

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid_inc2', 'uuid_inc1', 'parent_file',
                                                    'uuid_inc2', 'uuid_inc1', 'parent_file'])

    file_path = 'test_file_path.dat'
    test_file_contents = (
        '''basic_file INCLUDE inc_file1.inc
some random words ! comment
continuation''')
    include_file_contents = 'inc file contents\nsecond line in incfile \n include inc_file2.inc end of line \n abc'
    include_file_contents_2 = 'inc2 file contents\nmore content'
    expected_location = 'test_file_path.dat'
    expected_origin = None
    expected_flat_file = ['basic_file ', 'inc file contents\n', 'second line in incfile \n',
                          'inc2 file contents\n', 'more content', ' end of line \n', ' abc',
                          'some random words ! comment\n', 'continuation']
    nexus_file_include2 = NexusFile(location='inc_file2.inc', include_locations=[], origin='inc_file1.inc',
                                    include_objects=None, file_content_as_list=['inc2 file contents\n', 'more content'])

    inc1_file_content_as_list = ['inc file contents\n', 'second line in incfile \n',
                                 ' include inc_file2.inc end of line \n', ' abc']

    nexus_file_include1 = NexusFile(location='inc_file1.inc', include_locations=['inc_file2.inc'], origin=file_path,
                                    include_objects=[nexus_file_include2],
                                    file_content_as_list=inc1_file_content_as_list)

    expected_file_content_as_list = ['basic_file INCLUDE inc_file1.inc\n', 'some random words ! comment\n',
                                     'continuation']

    expected_line_locations = [(0, 'parent_file'), (1, 'uuid_inc1'), (3, 'uuid_inc2'), (5, 'uuid_inc1'),
                               (7, 'parent_file')]

    expected_nexus_file = NexusFile(location=expected_location, include_locations=['inc_file1.inc'],
                                    origin=expected_origin, include_objects=[nexus_file_include1],
                                    file_content_as_list=expected_file_content_as_list)
    expected_nexus_file.__setattr__('line_locations', expected_line_locations)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
            'inc_file2.inc': include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    # do the generation of the flat file a few times to catch the issue of continually appending duplicate line locations
    nexus_file.get_flat_list_str_file
    nexus_file.get_flat_list_str_file
    flat_file = nexus_file.get_flat_list_str_file

    # Assert
    assert flat_file == expected_flat_file
    assert nexus_file == expected_nexus_file
    assert nexus_file.line_locations == expected_nexus_file.line_locations


def test_line_locations_with_additional_lines(mocker):
    # Arrange
    # We need 2 lots of the mocked out uuid one for init of the expected files and one set for the try statement

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid_inc2', 'uuid_inc1', 'parent_file',
                                                    'uuid_inc2', 'uuid_inc1', 'parent_file'])

    file_path = 'test_file_path.dat'
    test_file_contents = (
        '''basic_file 
INCLUDE inc_file1.inc
some random words ! comment
continuation''')
    include_file_contents = 'inc file contents\nsecond line in incfile \n include inc_file2.inc end of line \n '
    include_file_contents_2 = 'inc2 file contents\nmore content'
    expected_location = 'test_file_path.dat'
    expected_origin = None

    nexus_file_include2 = NexusFile(location='inc_file2.inc', include_locations=[], origin='inc_file1.inc',
                                    include_objects=None, file_content_as_list=['inc2 file contents\n', 'more content'])

    inc1_file_content_as_list = ['inc file contents\n', 'new line in include_file\n', 'second line in incfile \n',
                                 ' include inc_file2.inc end of line \n', ' ']

    nexus_file_include1 = NexusFile(location='inc_file1.inc', include_locations=['inc_file2.inc'], origin=file_path,
                                    include_objects=[nexus_file_include2],
                                    file_content_as_list=inc1_file_content_as_list)

    expected_file_content_as_list = ['basic_file \n', 'New line in here\n', 'INCLUDE inc_file1.inc\n',
                                     'some random words ! comment\n', 'continuation']

    expected_line_locations = [(0, 'parent_file'), (2, 'uuid_inc1'), (5, 'uuid_inc2'), (7, 'uuid_inc1'),
                               (9, 'parent_file')]

    expected_nexus_file = NexusFile(location=expected_location, include_locations=['inc_file1.inc'],
                                    origin=expected_origin, include_objects=[nexus_file_include1],
                                    file_content_as_list=expected_file_content_as_list)
    expected_nexus_file.__setattr__('line_locations', expected_line_locations)

    expected_flat_file = ['basic_file \n', 'New line in here\n', 'inc file contents\n', 'new line in include_file\n',
                          'second line in incfile \n',
                          'inc2 file contents\n', 'more content', ' end of line \n', ' ',
                          'some random words ! comment\n', 'continuation']

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
            'inc_file2.inc': include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    # do the generation of the flat file a few times to catch the issue of continually appending duplicate line locations
    # nexus_file.get_flat_list_str_file
    nexus_file.file_content_as_list.insert(1, 'New line in here\n')
    nexus_file.include_objects[0].file_content_as_list.insert(1, 'new line in include_file\n')
    flat_file = nexus_file.get_flat_list_str_file

    # Assert
    assert flat_file == expected_flat_file
    assert nexus_file.file_content_as_list == expected_nexus_file.file_content_as_list
    assert nexus_file == expected_nexus_file
    assert nexus_file.line_locations == expected_nexus_file.line_locations


@pytest.mark.parametrize('index, expected_file_number, expected_index_in_file', [
    (0, 0, 0),
    (4, 2, 1),
    (1, 1, 0),
    (6, 1, 3),
    (7, 0, 1),
    (8, 0, 2),
    (3, 2, 0),
    (5, 1, 2),
    (2, 1, 1),
])
def test_find_which_include_file(mocker, index, expected_file_number, expected_index_in_file):
    # Arrange
    # We need 2 lots of the mocked out uuid one for init of the expected files and one set for the try statement

    mocker.patch.object(uuid, 'uuid4', side_effect=['uuid_inc2', 'uuid_inc1', 'parent_file',
                                                    'uuid_inc2', 'uuid_inc1', 'parent_file'])

    file_path = 'test_file_path.dat'
    test_file_contents = (
        '''basic_file INCLUDE inc_file1.inc
some random words ! comment
continuation''')
    include_file_contents = 'inc file contents\nsecond line in incfile \n include inc_file2.inc end of line \n '
    include_file_contents_2 = 'inc2 file contents\nmore content'
    expected_location = 'test_file_path.dat'
    expected_origin = None

    nexus_file_include2 = NexusFile(location='inc_file2.inc', include_locations=[], origin='inc_file1.inc',
                                    include_objects=None, file_content_as_list=['inc2 file contents\n', 'more content'])

    inc1_file_content_as_list = ['inc file contents\n', 'second line in incfile \n',
                                 ' include inc_file2.inc end of line \n',
                                 ' ']

    nexus_file_include1 = NexusFile(location='inc_file1.inc', include_locations=['inc_file2.inc'], origin=file_path,
                                    include_objects=[nexus_file_include2],
                                    file_content_as_list=inc1_file_content_as_list)

    expected_file_content_as_list = ['basic_file INCLUDE inc_file1.inc\n', 'some random words ! comment\n',
                                     'continuation']

    expected_flat_list_str = ['basic_file ', 'inc file contents\n', 'second line in incfile \n',
                              'inc2 file contents\n', 'more content',
                              ' end of line \n',
                              ' ',
                              'some random words ! comment\n',
                              'continuation']

    expected_line_locations = [(0, 'parent_file'), (1, 'uuid_inc1'), (3, 'uuid_inc2'), (5, 'uuid_inc1'),
                               (7, 'parent_file')]

    expected_nexus_file = NexusFile(location=expected_location, include_locations=['inc_file1.inc'],
                                    origin=expected_origin, include_objects=[nexus_file_include1],
                                    file_content_as_list=expected_file_content_as_list)
    expected_nexus_file.__setattr__('line_locations', expected_line_locations)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
            'inc_file2.inc': include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    expected_return_file = [expected_nexus_file, nexus_file_include1, nexus_file_include2][expected_file_number]

    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    flat_file = nexus_file.get_flat_list_str_file
    nexus_file_result, index_in_file = nexus_file.find_which_include_file(flattened_index=index)

    # Assert
    assert flat_file == expected_flat_list_str
    assert nexus_file.file_content_as_list == expected_file_content_as_list
    assert nexus_file == expected_nexus_file
    assert nexus_file_result == expected_return_file
    assert index_in_file == expected_index_in_file

    # raises
    nexus_file.include_objects.pop(0)
    with pytest.raises(ValueError) as ve:
        nexus_file.find_which_include_file(flattened_index=1)
    assert str(ve.value) == "No file with uuid_index='uuid_inc1' found within include objects"


@pytest.mark.parametrize("test_file_contents, expected_results",
                         [('''       WELLSPEC DEV1
       IW JW L RADW
       1  2  3  4.5     ! 2
       6 7 8   9.11     ! 3
       
       4 5 6 7.5        ! 5
       2 4 5 11         ! 6
                       
       !comment           
       3 4 5 6.5        ! 9 
       ''',
                           {'uuid1': [2],
                            'uuid2': [3],
                            'uuid3': [7],
                            'uuid4': [8],
                            'uuid5': [11],
                            }),
                          ],
                         ids=['basic_test']
                         )
def test_update_object_locations(mocker, test_file_contents, expected_results):
    # Arrange
    dummy_model = get_fake_nexus_simulator(mocker)
    dummy_wells = NexusWells(model=dummy_model)

    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4',
                 side_effect=['uuid1', 'uuid2', 'uuid3', 'uuid4', 'uuid5',
                              'uuid6', 'uuid7'])  # Mocking the object IDs

    mocker.patch.object(uuid, 'uuid4', side_effect=['file_uuid'])  # Mocking the file IDs

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'wells.dat': test_file_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    wells_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path='wells.dat',
                                                           skip_arrays=True)
    # load the uuids
    load_wells(wells_file, start_date='01/01/2012', default_units=UnitSystem.ENGLISH,
               model_date_format=DateFormat.DD_MM_YYYY, parent_wells_instance=dummy_wells)

    # Act
    # effectively add 2 lines at location 5
    wells_file._NexusFile__update_object_locations(line_number=5, number_additional_lines=2)
    result = wells_file.object_locations

    # Assert
    assert result == expected_results


def test_add_to_file_as_list(mocker):
    # Arrange
    mocker.patch.object(uuid, 'uuid4', side_effect=['additional_obj_uuid', 'file_uuid', 'file_uuid', ])

    additional_content = ['new', 'lines', 'of\n !the', 'file']
    additional_obj = {uuid.uuid4(): [3]}
    nexus_file = NexusFile(location='somefile.dat', origin=None, file_content_as_list=
    ['original', 'file', 'with \n', 'some filler', 'content', 'and object', 'must', 'be', 'more lines !ajf'],
                           )
    nexus_file.line_locations = [(0, 'file_uuid')]
    nexus_file.object_locations = {'uuid_obj': [2], 'another_uuid': [3], 'final_uuid': [7]}

    expected_line_locations = [(0, 'file_uuid')]
    expected_object_locations = {'uuid_obj': [2], 'another_uuid': [7], 'final_uuid': [11], 'additional_obj_uuid': [3]}
    expected_file_as_list = ['original', 'file', 'with \n', 'new', 'lines', 'of\n !the', 'file', 'some filler',
                             'content', 'and object', 'must', 'be', 'more lines !ajf']
    expected_result = NexusFile(location='somefile.dat', origin=None, file_content_as_list=expected_file_as_list)

    expected_result.line_locations = expected_line_locations
    expected_result.object_locations = expected_object_locations
    expected_result._file_modified_set(True)

    # mock out the write method to ensure it isn't making new files.
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)
    # Act
    nexus_file.add_to_file_as_list(additional_content=additional_content, index=3, additional_objects=additional_obj)
    result = nexus_file

    # Assert
    assert result == expected_result
    assert result.file_modified


def test_remove_from_file_as_list(mocker):
    # Arrange
    mocker.patch.object(uuid, 'uuid4', side_effect=['remove_obj_uuid', 'file_uuid', 'file_uuid', ])

    remove_obj = {uuid.uuid4(): 3}
    nexus_file = NexusFile(location='somefile.dat', origin=None, file_content_as_list=
    ['original', 'file', 'with \n', 'some filler', 'content', 'and object', 'must', 'be', 'more lines !ajf'],
                           )
    nexus_file.line_locations = [(0, 'file_uuid')]
    nexus_file.object_locations = {'uuid1': [2], 'remove_obj_uuid': [3], 'final_uuid': [7]}

    expected_object_locations = {'uuid1': [2], 'final_uuid': [6]}
    expected_file_as_list = ['original', 'file', 'with \n', 'content', ' object', 'must', 'be', 'more lines !ajf']
    expected_result = NexusFile(location='somefile.dat', origin=None, file_content_as_list=expected_file_as_list)

    expected_result.line_locations = [(0, 'file_uuid')]
    expected_result.object_locations = expected_object_locations
    expected_result._file_modified_set(True)

    # mock out the write method to ensure it isn't making new files.
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)
    # Act
    nexus_file.remove_from_file_as_list(index=3, objects_to_remove=list(remove_obj.keys()))
    nexus_file.remove_from_file_as_list(index=4, string_to_remove='and')

    # Assert
    assert nexus_file.file_content_as_list == expected_result.file_content_as_list
    assert nexus_file == expected_result
    assert nexus_file.file_modified


@pytest.mark.parametrize('file_content, expected_file_content', [
    (
            'test_file_content\nInCluDE oRigINAl_Include.inc\nend of the file\n',
            'test_file_content\nInCluDE New_FiLe_Path.inc\nend of the file\n',
    ),
    (
            'test_file_content\nInCluDE\noRigINAl_Include.inc\nend of the file\n',
            'test_file_content\nInCluDE\nNew_FiLe_Path.inc\nend of the file\n',
    ),
    (
            'test_file_content\nInCluDE /abs_path/oRigINAl_Include.inc\nend of the file\n',
            'test_file_content\nInCluDE New_FiLe_Path.inc\nend of the file\n',
    )
], ids=['basic', 'on another line', 'next line'])
def test_update_include_location_in_file_as_list(mocker, file_content, expected_file_content):
    # Arrange
    file_path = '/root/file.dat'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_content,
            '/root/oRigINAl_Include.inc': 'inc file contents',
            '/abs_path/oRigINAl_Include.inc': 'inc file contents',
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)

    new_file_path = 'New_FiLe_Path.inc'
    include_file = nexus_file.include_objects[0]
    expected_path = os.path.join('/root', 'New_FiLe_Path.inc')
    # Act
    nexus_file.update_include_location_in_file_as_list(new_file_path, include_file)
    # Assert
    assert nexus_file.file_content_as_list == expected_file_content.splitlines(keepends=True)
    assert nexus_file.include_locations == [expected_path]
    assert include_file.location == expected_path
    assert include_file.location_in_including_file == 'New_FiLe_Path.inc'
    assert nexus_file.file_modified


def test_write_to_file(mocker):
    # Arrange
    file_content = '''test_file_content\nInCluDE original_include.inc\nINCLUDE
                    /abs_path/another_file.inc\nend of the file\n'''
    file_path = '/root/file.dat'
    new_file_path = os.path.join('\\new_location', 'new_file_path.dat')
    expected_include_path_1 = os.path.join('\\new_location', 'new_file_path_original_include.inc')
    expected_include_path_2 = os.path.join('\\new_location', 'new_file_path_another_file.inc')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_content,
            os.path.join('/root', 'original_include.inc'): 'inc file contents',
            '/abs_path/another_file.inc': 'inc file contents',
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)

    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)

    # Mock out the file exists
    file_exists_mock = MagicMock(side_effect=lambda x: False)
    mocker.patch('os.path.exists', file_exists_mock)

    # mock out makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)
    # Act
    nexus_file.write_to_file(new_file_path, write_includes=True, write_out_all_files=True)
    # Assert
    list_of_write_names = [call.args[0] for call in writing_mock_open.mock_calls if "'w')" in str(call)]
    assert list_of_write_names == [expected_include_path_1, expected_include_path_2, new_file_path]
    # assert the file_modified has been removed
    assert not nexus_file.file_modified


def test_write_to_file_only_modified(mocker):
    # Arrange
    file_content = '''test_file_content\nInCluDE original_include.inc\nINCLUDE
                    /abs_path/another_file.inc\nend of the file\n'''

    file_path = '/root/file.dat'
    new_file_path = os.path.join('\\new_location', 'new_file_path.dat')
    expected_include_path_1 = os.path.join('\\new_location', 'new_file_path_original_include.inc')

    expected_file_content = f'''test_file_content\nInCluDE {expected_include_path_1}\nINCLUDE
                    /abs_path/another_file.inc\nend of the file\n'''

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_content,
            '/root/original_include.inc': 'inc file contents',
            '/abs_path/another_file.inc': 'inc file contents',
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    nexus_file._file_modified_set(True)
    nexus_file.include_objects[0]._file_modified_set(True)
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)
    # mock out makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)
    # Mock out the file exists
    file_exists_mock = MagicMock(side_effect=lambda x: False)
    mocker.patch('os.path.exists', file_exists_mock)

    # mock out makedirs
    makedirs_mock = MagicMock()
    mocker.patch('os.makedirs', makedirs_mock)

    # Act
    nexus_file.write_to_file(new_file_path, write_includes=True, write_out_all_files=False)
    # Assert
    list_of_write_names = [call.args[0] for call in writing_mock_open.mock_calls if "'w')" in str(call)]
    assert list_of_write_names == [expected_include_path_1, new_file_path]

    list_of_writes = [call for call in writing_mock_open.mock_calls if 'call().write' in str(call)]
    assert list_of_writes[-1].args[0] == expected_file_content


@pytest.mark.parametrize('location, file_as_list, overwrite_file, expected_error', [
    ('path/file.dat', None, True, 'No file data to write out, instead found None'),
    (None, ['file_content'], False, 'No file path to write to, and overwrite_file set to False'),
], ids=['no file as list', 'no overwrite'])
def test_write_to_file_exit_points(mocker, location, file_as_list, overwrite_file,
                                   expected_error):
    # Arrange
    empty_file = NexusFile(location=location, file_content_as_list=file_as_list)
    if file_as_list is None:
        empty_file.file_content_as_list = None
    # Act Assert
    with pytest.raises(ValueError) as ve:
        empty_file.write_to_file(overwrite_file=overwrite_file)
    assert str(ve.value) == expected_error


@pytest.mark.parametrize('location, file_as_list, include_locations, error', [
    ('location.dat', ['file_content'], None, 'No include locations found'),
    ('location.dat', None, ['include_loc.dat'], 'No file content found within file'),
], ids=['No includes locs', 'No file content'])
def test_update_include_location_in_file_as_list_exit_points(mocker,
                                                             location, file_as_list, include_locations, error):
    # Arrange
    empty_file = NexusFile(location=location, file_content_as_list=file_as_list, include_locations=include_locations)
    include_file = NexusFile(location='include_loc.dat')
    # Act Assert
    with pytest.raises(ValueError) as ve:
        empty_file.update_include_location_in_file_as_list(new_path='New_path.dat', include_file=include_file)
    assert error in str(ve.value)


def test_write_to_file_failure(mocker):
    # Arrange
    file_content = '''test_file_content'''
    file = NexusFile(location='somefile.dat', origin=None, file_content_as_list=[file_content])
    writing_mock_open = mocker.mock_open()
    mocker.patch("builtins.open", writing_mock_open)
    mocker.patch('os.path.exists', MagicMock(return_value=True))
    # Act
    with pytest.raises(ValueError) as ve:
        file.write_to_file(new_file_path='new_somefile.dat', write_includes=True, write_out_all_files=True,
                           overwrite_file=False)
    assert str(ve.value) == 'File already exists at new_somefile.dat and overwrite_file set to False'


# TODO: Convert this test to run independently of the other tests.
def test_missing_file(mocker):
    # Arrange
    file_content = '''test_file_content\nInCluDE original_include.inc\nINCLUDE'''
    file_path = '/root/file.dat'
    expected_missing_file = os.path.join('/root', 'original_include.inc')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_content,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    path_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path', path_mock)
    path_mock.return_value.owner.return_value = "mock_User"
    path_mock.return_value.group.side_effect = FileNotFoundError("File not found")
    # Act Assert
    with pytest.warns(UserWarning, match=r'No file found for:') as warn_msg:
        nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    mocker.stopall()
    result_include_file = nexus_file.include_objects[0]
    assert result_include_file.file_content_as_list == []
    assert result_include_file.location == expected_missing_file
    assert result_include_file.origin == file_path
    assert result_include_file.include_objects == []
    assert result_include_file.include_locations == []
    assert result_include_file.linked_user is None
    assert result_include_file.last_modified is None
    assert warn_msg[0].message.args[0] == 'FileNotFoundError when trying to access file at /root/file.dat'
    assert warn_msg[1].message.args[
               0] == f"No file found for: {os.path.join('/root', 'original_include.inc')} while loading /root/file.dat"


def test_group_not_found(mocker):
    # Arrange
    file_content = '''test_file_content\nInCluDE original_include.inc\nINCLUDE'''
    file_path = '/root/file.dat'
    expected_missing_file = os.path.join('/root', 'original_include.inc')

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_content,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    path_mock = mocker.MagicMock()
    mocker.patch('pathlib.Path', path_mock)
    path_mock.return_value.owner.return_value = "mock_User"
    path_mock.return_value.group.side_effect = KeyError(f"Unable to find the group for the file at {file_path}")
    # Act Assert
    with pytest.warns(UserWarning, match=r'Unable to find the group for the file at') as warn_msg:
        nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    mocker.stopall()
    result_include_file = nexus_file.include_objects[0]
    assert result_include_file.file_content_as_list == []
    assert result_include_file.location == expected_missing_file
    assert result_include_file.origin == file_path
    assert result_include_file.include_objects == []
    assert result_include_file.include_locations == []
    assert result_include_file.linked_user is None
    assert result_include_file.last_modified is None
    assert warn_msg[0].message.args[0] == 'Unable to find the group for the file at /root/file.dat'


def test_nexusfile_repr(mocker):
    # Arrange
    file_content = '''test_file_content\nInCluDE original_include.inc\nINCLUDE'''
    file_path = '/root/file.dat'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: file_content,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    expected_result = f"""FILE PATH: /root/file.dat

Include files: {[os.path.join(os.path.dirname(file_path), 'original_include.inc')]}

FILE CONTENTS:

test_file_content
InCluDE original_include.inc
INCLUDE"""
    # Act
    result = repr(nexus_file)
    # Assert
    assert result == expected_result


def test_get_full_network_nexus_file(mocker):
    # Arrange
    file_path = '/origin/path/test_file_path.dat'
    include_full_file_path_1 = os.path.join('/origin/path', 'nexus_data/inc_file1.inc')
    include_full_file_path_2 = os.path.join('/origin/path', 'nexus_data', 'inc_file2.inc')
    include_full_file_path_3 = os.path.join('/origin/path', 'nexus_data/inc_file3.inc')
    expected_includes_list = [include_full_file_path_1]
    expected_location = '/origin/path/test_file_path.dat'

    nexus_file_include2 = NexusFile(location=include_full_file_path_2, include_locations=[],
                                    origin=include_full_file_path_1,
                                    include_objects=None, file_content_as_list=['second_file'])
    nexus_file_include2._location_in_including_file = 'inc_file2.inc'

    nexus_file_include1 = NexusFile(location=include_full_file_path_1, include_locations=[include_full_file_path_2],
                                    origin=file_path, include_objects=[nexus_file_include2],
                                    file_content_as_list=['inc file contents INCLUDE inc_file2.inc'])
    nexus_file_include1._location_in_including_file = 'nexus_data/inc_file1.inc'

    nexus_file_include3 = NexusFile(location='nexus_data/inc_file3.inc', include_locations=[],
                                    origin=file_path, include_objects=None,
                                    file_content_as_list=['third_file'])

    nexus_file = NexusFile(location=expected_location, include_locations=expected_includes_list,
                           origin=None, include_objects=[nexus_file_include1, nexus_file_include3],
                           file_content_as_list=['basic_file INCLUDE nexus_data/inc_file1.inc'])

    expected_from_list = [None, file_path, include_full_file_path_1, file_path]
    expected_to_list = [file_path, include_full_file_path_1, include_full_file_path_2, include_full_file_path_3]

    expected_shallow_from_list = [None, file_path, file_path]
    expected_shallow_to_list = [file_path, include_full_file_path_1, include_full_file_path_3]
    # Act
    from_list, to_list = nexus_file.get_full_network()

    shallow_from_list, shallow_to_list = nexus_file.get_full_network(max_depth=1)

    # Assert
    assert from_list == expected_from_list
    assert to_list == expected_to_list

    assert shallow_from_list == expected_shallow_from_list
    assert shallow_to_list == expected_shallow_to_list


@pytest.mark.parametrize('callable, expected_result', [
    ('get_flat_list_str_with_file_ids', [('basic_file ', 'uuid0'),
                                         ('first inc file contents\n', 'uuid0'),
                                         ('second line in incfile', 'uuid0'),
                                         ('line 1 parent\n', 'uuid1'),
                                         ('line 2 parent\n', 'uuid1'),
                                         ]),
    ('get_flat_list_str_with_file_ids_with_includes', [('basic_file INCLUDE inc_file1.inc\n', 'uuid1'),
                                                       ('basic_file ', 'uuid0'),
                                                       ('first inc file contents\n', 'uuid0'),
                                                       ('second line in incfile', 'uuid0'),
                                                       ('line 1 parent\n', 'uuid1'),
                                                       ('line 2 parent\n', 'uuid1'),
                                                       ]),
    ('get_flat_list_str_file', ['basic_file ', 'first inc file contents\n', 'second line in incfile',
                                'line 1 parent\n', 'line 2 parent\n']),
], ids=['file_ids', 'file_ids_with_includes', 'no_file_ids'])
def test_iterate_line_with_file_origins(mocker, callable, expected_result):
    # Arrange
    # mock out the uuids
    mocker.patch.object(uuid, 'uuid4', side_effect=uuid_side_effect())
    file_path = 'test_file_path.dat'
    test_file_contents = (
        '''basic_file INCLUDE inc_file1.inc
line 1 parent
line 2 parent
'''
    )
    include_file_contents = 'first inc file contents\nsecond line in incfile'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            'test_file_path.dat': test_file_contents,
            'inc_file1.inc': include_file_contents,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path)
    # Act
    result = getattr(nexus_file, callable)

    # Assert
    assert result == expected_result


def test_generate_file_include_structure_skip_multiple_includes(mocker):
    # Arrange
    file_path = '/origin/path/test_file_path.dat'
    include_file_contents = '1 2.2 3\n 2.3\n 4.1231235 -24.43 +2303 \n +2013\n'
    include_full_file_path_1 = os.path.join('/origin/path', 'nexus_data/inc_file1.inc')
    test_file_contents = 'KX VALUE\nINCLUDE nexus_data/inc_file1.inc\nINCLUDE nexus_data/inc_file2.inc\n'
    expected_include_file_1 = NexusFile(location=include_full_file_path_1, include_locations=None,
                                        origin=file_path, include_objects=None,
                                        file_content_as_list=None, file_loading_skipped=True)
    expected_include_file_1._input_file_location = 'nexus_data/inc_file1.inc'
    expected_include_file_1._location_in_including_file = 'nexus_data/inc_file1.inc'

    include_file_contents_2 = '1 2.2 3\n 2.3\n 4.1231235 -24.43 +2303 \n +2013\n'

    include_full_file_path_2 = os.path.join('/origin/path', 'nexus_data/inc_file2.inc')
    expected_include_file_2 = NexusFile(location='nexus_data/inc_file2.inc', include_locations=None,
                                        origin=file_path, include_objects=None,
                                        file_content_as_list=None, file_loading_skipped=True)
    expected_include_file_2._input_file_location = 'nexus_data/inc_file2.inc'
    expected_include_file_2._location_in_including_file = 'nexus_data/inc_file2.inc'

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            file_path: test_file_contents,
            include_full_file_path_1: include_file_contents,
            include_full_file_path_2: include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    nexus_file = NexusFile.generate_file_include_structure(simulator_type=NexusFile, file_path=file_path,
                                                           skip_arrays=True)

    # Assert
    assert len(nexus_file.include_objects) == 2
    assert nexus_file.file_loading_skipped is False
    assert nexus_file.include_objects[0].file_loading_skipped is True
    assert nexus_file.include_objects[0] == expected_include_file_1
    assert nexus_file.include_objects[1].file_loading_skipped is True
    assert nexus_file.include_objects[1] == expected_include_file_2


@pytest.mark.parametrize('filename, expected_result', [
    ('file_in_restart_include.dat',
     [NexusFile(location='file_in_restart_include.dat', include_objects=[])]),
    ('structured_grid_file.dat',
     [NexusFile(location='structured_grid_file.dat', include_objects=[])]),
    ('options_file.dat',
     [NexusFile(location='options_file.dat', include_objects=[])]),
    ('runcontrol_file.dat',
     [NexusFile(location='runcontrol_file.dat', include_objects=[])]),
    ('override_file.dat',
     [NexusFile(location='override_file.dat', include_objects=[])]),
    ('eos_default_file.dat',
     [NexusFile(location='eos_default_file.dat', include_objects=[])]),
    ('well_file.dat',
     [NexusFile(location='well_file.dat', include_objects=[])]),
    ('surface_file.dat',
     [NexusFile(location='surface_file.dat', include_objects=[])]),
    ('rock_file.dat',
     [NexusFile(location='rock_file.dat', include_objects=[])]),
    ('relperm_file.dat',
     [NexusFile(location='relperm_file.dat', include_objects=[])]),
    ('pvt_file.dat',
     [NexusFile(location='pvt_file.dat', include_objects=[])]),
    ('file_in_water_include.dat',
     [NexusFile(location='file_in_water_include.dat', include_objects=[])]),
    ('equil_file2.dat',
     [NexusFile(location='equil_file2.dat', include_objects=[])]),
    ('tracer_init_file.dat',
     [NexusFile(location='tracer_init_file.dat', include_objects=[])]),
    ('aquifer_file.dat',
     [NexusFile(location='aquifer_file.dat', include_objects=[])]),
    ('hyd_file.dat',
     [NexusFile(location='hyd_file.dat', include_objects=[])]),
    ('valve_file.dat',
     [NexusFile(location='valve_file.dat', include_objects=[])]),
    ('separator_file.dat',
     [NexusFile(location='separator_file.dat', include_objects=[])]),
    ('ipr_file.dat',
     [NexusFile(location='ipr_file.dat', include_objects=[])]),
    ('gas_lift_file.dat',
     [NexusFile(location='gas_lift_file.dat', include_objects=[])]),
    ('pump_file.dat',
     [NexusFile(location='pump_file.dat', include_objects=[])]),
    ('compressor_file.dat',
     [NexusFile(location='compressor_file.dat', include_objects=[])]),
    ('choke_file.dat',
     [NexusFile(location='choke_file.dat', include_objects=[])]),
    ('icd_file.dat',
     [NexusFile(location='icd_file.dat', include_objects=[])]),
    ('esp_file.dat',
     [NexusFile(location='esp_file.dat', include_objects=[])]),
    ('polymer_file.dat',
     [NexusFile(location='polymer_file.dat', include_objects=[])]),
    ('adsorption_file.dat',
     [NexusFile(location='adsorption_file.dat', include_objects=[])]),
    ('flux_in_file.dat',
     [NexusFile(location='flux_in_file.dat', include_objects=[])])
])
def test_get_model_files_by_filename(filename, expected_result):
    # Arrange
    restart_file = NexusFile(location='restart_file.dat',
                             include_objects=[NexusFile(location='file_in_restart_include.dat')])
    structured_grid_file = NexusFile(location='structured_grid_file.dat', include_objects=[])
    options_file = NexusFile(location='options_file.dat', include_objects=[])
    runcontrol_file = NexusFile(location='runcontrol_file.dat', include_objects=[])
    override_file = NexusFile(location='override_file.dat', include_objects=[])
    eos_default_file = NexusFile(location='eos_default_file.dat', include_objects=[])
    well_files = {1: NexusFile(location='well_file.dat', include_objects=[])}
    surface_files = {1: NexusFile(location='surface_file.dat', include_objects=[])}
    rock_files = {1: NexusFile(location='rock_file.dat', include_objects=[])}
    relperm_files = {1: NexusFile(location='relperm_file.dat', include_objects=[])}
    pvt_files = {1: NexusFile(location='pvt_file.dat', include_objects=[])}
    water_files = {
        1: NexusFile(location='water_file.dat', include_objects=[NexusFile(location='file_in_water_include.dat')])}
    equil_files = {1: NexusFile(location='equil_file1.dat', include_objects=[]),
                   2: NexusFile(location='equil_file2.dat', include_objects=[])}
    tracer_init_files = {1: NexusFile(location='tracer_init_file.dat', include_objects=[])}
    aquifer_files = {1: NexusFile(location='aquifer_file.dat', include_objects=[])}
    hyd_files = {1: NexusFile(location='hyd_file.dat', include_objects=[])}
    valve_files = {1: NexusFile(location='valve_file.dat', include_objects=[])}
    separator_files = {1: NexusFile(location='separator_file.dat', include_objects=[])}
    ipr_files = {1: NexusFile(location='ipr_file.dat', include_objects=[])}
    gas_lift_files = {1: NexusFile(location='gas_lift_file.dat', include_objects=[])}
    pump_files = {1: NexusFile(location='pump_file.dat', include_objects=[])}
    compressor_files = {1: NexusFile(location='compressor_file.dat', include_objects=[])}
    choke_files = {1: NexusFile(location='choke_file.dat', include_objects=[])}
    icd_files = {1: NexusFile(location='icd_file.dat', include_objects=[])}
    esp_files = {1: NexusFile(location='esp_file.dat', include_objects=[])}
    polymer_files = {1: NexusFile(location='polymer_file.dat', include_objects=[])}
    adsorption_files = {1: NexusFile(location='adsorption_file.dat', include_objects=[])}
    flux_in_files = {1: NexusFile(location='flux_in_file.dat', include_objects=[])}

    fcs_file = FcsNexusFile(location='model.fcs', restart_file=restart_file, structured_grid_file=structured_grid_file,
                            options_file=options_file, runcontrol_file=runcontrol_file, override_file=override_file,
                            eos_default_file=eos_default_file, well_files=well_files, surface_files=surface_files,
                            rock_files=rock_files, relperm_files=relperm_files, pvt_files=pvt_files,
                            water_files=water_files, equil_files=equil_files, tracer_init_files=tracer_init_files,
                            aquifer_files=aquifer_files, hyd_files=hyd_files, valve_files=valve_files,
                            separator_files=separator_files, ipr_files=ipr_files, gas_lift_files=gas_lift_files,
                            pump_files=pump_files, compressor_files=compressor_files, choke_files=choke_files,
                            icd_files=icd_files, esp_files=esp_files, polymer_files=polymer_files,
                            adsorption_files=adsorption_files, flux_in_files=flux_in_files)

    # Act
    result = fcs_file.get_model_files_by_filename(filename=filename)

    # Assert
    assert result == expected_result


def test_get_model_files_by_filename_file_not_found():
    # Arrange
    restart_file = NexusFile(location='restart_file.dat',
                             include_objects=[NexusFile(location='file_in_restart_include.dat')])

    fcs_file = FcsNexusFile(location='model.fcs', restart_file=restart_file)

    # Act
    result = fcs_file.get_model_files_by_filename(filename='missing_file.dat')

    # Assert
    assert result == []
