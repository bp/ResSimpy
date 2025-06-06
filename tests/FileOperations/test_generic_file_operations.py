import os
import sys

from pytest_mock import MockerFixture

from ResSimpy.FileOperations.File import File
from tests.multifile_mocker import mock_multiple_files


def test_generate_file_include_structure_nested_includes_non_nexus(mocker: MockerFixture, recwarn):
    # Arrange
    file_path = '/path/of/test_file_path.dat'

    test_file_contents = """basic_file 
INCLUDE 
    inc_file1.inc 
/

-- Test comment
-- INCLUDE
-- incfile_3.inc
-- /

something after"""

    include_file_contents = f"""inc file contents 
INCLUDE 

-- test comment before file
  '/path/to/inc_file_2.inc'

/
"""

    include_file_contents_2 = 'inc2 file contents'
    inc_file_1_full_path = os.path.join('/path/of', 'inc_file1.inc')
    expected_includes_list = [os.path.join('/path/of', 'inc_file1.inc')]
    expected_location = '/path/of/test_file_path.dat'
    expected_origin = None

    nexus_file_include2 = File(location='/path/to/inc_file_2.inc', include_locations=[], origin=inc_file_1_full_path,
                               include_objects=None, file_content_as_list=[include_file_contents_2])
    nexus_file_include1 = File(location='inc_file1.inc', include_locations=['/path/to/inc_file_2.inc'],
                               origin=file_path, include_objects=[nexus_file_include2],
                               file_content_as_list=include_file_contents.splitlines(keepends=True))

    expected_file_content_as_list = test_file_contents.splitlines(keepends=True)

    expected_nexus_file = File(location=expected_location, include_locations=expected_includes_list,
                               origin=expected_origin, include_objects=[nexus_file_include1],
                               file_content_as_list=expected_file_content_as_list)

    def mock_open_wrapper(filename, mode):
        mock_open = mock_multiple_files(mocker, filename, potential_file_dict={
            '/path/of/test_file_path.dat': test_file_contents,
            inc_file_1_full_path: include_file_contents,
            '/path/to/inc_file_2.inc': include_file_contents_2,
        }).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    file_with_includes = File.generate_file_include_structure(simulator_type=File, file_path=file_path)

    # Assert
    assert len(recwarn) == 0
    assert file_with_includes.file_content_as_list == expected_nexus_file.file_content_as_list
    assert file_with_includes == expected_nexus_file
