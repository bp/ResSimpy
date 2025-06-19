import os
from dataclasses import dataclass
import ResSimpy.Nexus.nexus_collect_tables
import ResSimpy.Nexus.nexus_file_operations as nfo
import ResSimpy.FileOperations.file_operations as fo
import pytest
import pandas as pd
import numpy as np

from ResSimpy.FileOperations.simulator_constants import OTHER_SIMULATOR_COMMENT_CHARACTERS
from ResSimpy.Nexus.DataModels.Network.NexusDrill import NexusDrill
from ResSimpy.Nexus.DataModels.Network.NexusWellConnection import NexusWellConnection
from ResSimpy.Nexus.DataModels.Network.NexusWellhead import NexusWellhead
from ResSimpy.Nexus.DataModels.NexusFile import NexusFile
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Enums.UnitsEnum import UnitSystem
from unittest.mock import Mock

from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Nexus.NexusNetwork import NexusNetwork
from ResSimpy.Nexus.NexusSimulator import NexusSimulator
from ResSimpy.Nexus.nexus_add_new_object_to_file import AddObjectOperations
from ResSimpy.Nexus.nexus_remove_object_from_file import RemoveObjectOperations
from tests.multifile_mocker import mock_multiple_files
from tests.utility_for_tests import get_fake_nexus_simulator


@pytest.mark.parametrize("line_string, token, expected_result",
                         [("Line contains TOKEN 124", "ToKEN", True),
                          ("TokeN 323 and other text", "TOKEN", True),
                          ("other text and TokEN", "TOKEN", True),
                          ("No T0k3N here", "TOKEN", False),
                          ("!TOKEN", "TOKEN", False),
                          ("THISTOKEN etc", "TOKEN", False),
                          ("TOKENLONGERWORD etc", "TOKEN", False),
                          ("TOKEN!comment", "TOKEN", True),
                          ("TOKEN  value", "TOKEN", True),
                          ("TOKEN\n", "TOKEN", True),
                          ("T", "T", True),
                          ("Brian", "B", False),
                          ("C TOKEN", "TOKEN", False)
                          ], ids=["standard case", "token at start", "token at end", "no token", "token commented out",
                                  "token only part of longer word 1", "token only part of longer word 2",
                                  "token before comment", "token then tab", "token then newline", "single character",
                                  "token in string", "C Comment"
                                  ])
def test_check_token(line_string, token, expected_result):
    # Act
    result = fo.check_token(token=token, line=line_string)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("line_string, token, expected_result",
                         [("Line contains TOKEN 124", "ToKEN", True),
                          ("TokeN 323 and other text", "TOKEN", True),
                          ("other text and TokEN", "TOKEN", True),
                          ("No T0k3N here", "TOKEN", False),
                          ("--TOKEN", "TOKEN", False),
                          ("THISTOKEN etc", "TOKEN", False),
                          ("TOKENLONGERWORD etc", "TOKEN", False),
                          ("TOKEN--comment", "TOKEN", True),
                          ("TOKEN  value", "TOKEN", True),
                          ("TOKEN\n", "TOKEN", True),
                          ("T", "T", True),
                          ("Brian", "B", False),
                          ("C TOKEN", "TOKEN", True),
                          ("! TOKEN", "TOKEN", True)
                          ], ids=["standard case", "token at start", "token at end", "no token", "token commented out",
                                  "token only part of longer word 1", "token only part of longer word 2",
                                  "token before comment", "token then tab", "token then newline", "single character",
                                  "token in string", "invalid comment character 1", "invalid comment character 2"
                                  ])
def test_check_token_other_comment_characters(line_string, token, expected_result):
    # Act
    result = fo.check_token(token=token, line=line_string, comment_characters=OTHER_SIMULATOR_COMMENT_CHARACTERS)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file_contents, expected_result_contents, strip_str", [
    ('''
SW         KRW        KROW        PCWO !Comments
!comment
''',
     '''SW         KRW        KROW        PCWO ''',
     False,
     ),

    ('''
  Spaces before
0
Mid line ! comment

Tabs  after ! comment ! comment ! comment
Several comment characters !!!!! comment1 !!!!
!single line comment
   !blank space before comment
''',
     '''  Spaces before
0
Mid line 
Tabs  after 
Several comment characters 
   ''',
     False,
     ),
    ('''wrapped in quotations "!" included ! comment''',
     '''wrapped in quotations "!" included ''',
     False,
     ),
    ('''KEYWORD [this should get commented out] keyword''',
     '''KEYWORD  keyword''',
     False,
     ),
    ('''comment
[remove 
remove] keep [remove]
keep [ why does this even
exist] as [functionality]''',
     '''comment
 keep 
keep  as ''',
     False,
     ),
    ('''"[" [ "]" ] [
remove
]
"[" keep "]"
''',
     '''"["  
"[" keep "]"
''',
     False,
     ),
    ('''some string \t! comment
some [comment] \t
[multiline
commment] value
''',
     '''some string
some
value
''',
     True,
     ),
], ids=['basic test', 'several inline/single line comments', 'wrapped in quotations', 'Square bracket',
        'square bracket complicated', 'Square bracket quotation', 'stripstring']
                         )
def test_strip_file_of_comments(file_contents, expected_result_contents, strip_str):
    # Arrange
    dummy_file_as_list = file_contents.splitlines()
    expected_result = expected_result_contents.splitlines()

    # Act
    result = nfo.strip_file_of_comments(dummy_file_as_list, strip_str=strip_str, square_bracket_comments=True)
    # Assert
    assert result == expected_result


def test_strip_file_of_comments_other_comment_characters():
    # Arrange
    file_contents = '''some string \t# comment
#entire line commented out
value 1 '#value 2
'''

    expected_result_contents = '''some string \t
value 1 '
'''

    dummy_file_as_list = file_contents.splitlines()
    expected_result = expected_result_contents.splitlines()

    # Act
    result = nfo.strip_file_of_comments(dummy_file_as_list, comment_characters=['#'])
    # Assert
    assert result == expected_result


def test_strip_file_of_comments_multiple_comment_characters():
    # Arrange
    file_contents = '''some string \t# comment
#entire line commented out
value 1 '#value 2
value 3 -- different comment style
-- both comment # types
-- Another line missing
! Not a comment for this test.
'''

    expected_result_contents = '''some string \t
value 1 '
value 3 
! Not a comment for this test.
'''

    dummy_file_as_list = file_contents.splitlines()
    expected_result = expected_result_contents.splitlines()

    # Act
    result = nfo.strip_file_of_comments(dummy_file_as_list, comment_characters=['--', '#'])
    # Assert
    assert result == expected_result


def mock_includes(mocker, filename, include_contents0, include_contents1):
    # yes this should just index a tuple
    if "0" in filename:
        file_contents = include_contents0
    elif "1" in filename:
        file_contents = include_contents1
    else:
        raise FileNotFoundError(filename)
    open_mock = mocker.mock_open(read_data=file_contents)
    return open_mock


@pytest.mark.parametrize("file_contents, recursive, include_contents0, include_contents1, expected_result_contents",
                         [
                             # one_include
                             (
                                     '''RUNFILES
INCLUDE data0.inc''',
                                     True,
                                     '''data
KX
CON 5''',
                                     '',
                                     '''RUNFILES
data
KX
CON 5''',
                             ),
                             # complicated
                             (
                                     '''RUNFILES
something before InCLUde data0.inc something after !comment INCLUDE''',
                                     True,
                                     '''data
KX
CON 5''',
                                     '',
                                     '''RUNFILES
something before
data
KX
CON 5
something after''',
                             ),
                             # no_include
                             (
                                     '''no_inc''',
                                     True,
                                     '''data
KX
CON 5''',
                                     '',
                                     '''no_inc''',
                             ),
                             # multiple_includes
                             (
                                     '''Header
INCLUDE data0.inc
INCLUDE data1.inc
footer
''',
                                     True,
                                     '''data
KX
CON 5''',
                                     '''Second file here
second file data
''',
                                     '''Header
data
KX
CON 5
Second file here
second file data
footer''',
                             ),
                             # multiple_includes_recursive_off
                             (
                                     '''Header
INCLUDE data0.inc
INCLUDE data1.inc
footer
''',
                                     False,
                                     '''data
KX
CON 5''',
                                     '''Second file here
second file data
''',
                                     '''Header
data
KX
CON 5
INCLUDE data1.inc
footer''',
                             ),
                             # nested_includes
                             (
                                     '''Header
INCLUDE data0.inc
footer
''',
                                     True,
                                     '''data
INCLUDE data1.inc''',
                                     '''Second file here
second file data
''',
                                     '''Header
data
Second file here
second file data
footer''',
                             ),
                         ], ids=['one_include', 'complicated', 'no_include', 'multiple_includes',
                                 'multiple_includes_recursive_off', 'nested_includes'],
                         )
def test_expand_include(mocker, file_contents, recursive, include_contents0, include_contents1,
                        expected_result_contents, ):
    # Arrange
    dummy_file_as_list = file_contents.splitlines()
    expected_result = expected_result_contents.splitlines()

    def mock_open_wrapper(filename, operation=None):
        mock_open = mock_includes(mocker, filename, include_contents0, include_contents1).return_value
        return mock_open

    mocker.patch("builtins.open", mock_open_wrapper)

    # Act
    result, _ = nfo.expand_include(dummy_file_as_list, recursive)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file_contents, keep_comments, expected_df_dict",
                         [("""
    NAME IW JW L Radw 
    L1   1  2  3  4.5 
    L2   6  7  8   9.11 
    """, False,
                           {'NAME': ['L1', 'L2'], 'IW': [1, 6], 'JW': [2, 7], 'L': [3, 8], 'RADW': [4.5, 9.11]}),
                          ("""
    NAME IW JW L Radw 
    L1   1  2  3  4.5 
    L2   6  7  8   NA 
    """, False,
                           {'NAME': ['L1', 'L2'], 'IW': [1, 6], 'JW': [2, 7], 'L': [3, 8], 'RADW': [4.5, np.nan]}),
                          ("""
    COMPONENT N2    C1    PS1  C2 
    C1        0.028
    PS1       0.17  0.0
    C2        0.061 0.005 0.0
    PS2       0.17  0.0   0.0  0.0
    """, False,
                           {'COMPONENT': ['C1', 'PS1', 'C2', 'PS2'], 'N2': [0.028, 0.17, 0.061, 0.17],
                            'C1': [None, 0.0, 0.005, 0.0], 'PS1': [None, None, 0.0, 0.0],
                            'C2': [None, None, None, 0.0]}),
                          ("""NAME IW JW L Radw ! Depth
L1   1  2  3  4.5 ! 1000

L2   6  7  8   NA ! 2000 ! 3000
! This is a comment
L3  10  9 10  2.3
""", True,
                           {'NAME': ['L1', 'L2', None, 'L3'], 'IW': [1, 6, None, 10], 'JW': [2, 7, None, 9],
                            'L': [3, 8, None, 10], 'RADW': [4.5, None, None, 2.3],
                            'COMMENT': ['1000', '2000 ! 3000', 'This is a comment', None]})
                          ],
                         ids=["basic case", "na case", "lower triangular case", "comments case"])
def test_read_table_to_df(file_contents, keep_comments, expected_df_dict):
    # Arrange
    if keep_comments:
        df_expected = pd.DataFrame(expected_df_dict).convert_dtypes()
    else:
        df_expected = pd.DataFrame(expected_df_dict)

    # mock out test file contents
    file_as_list = file_contents.splitlines()

    # Act
    df_received = nfo.read_table_to_df(file_as_list, keep_comments)

    # Assert
    # Deep compare expected and received dataframes
    pd.testing.assert_frame_equal(df_expected, df_received)


def test_get_expected_token_value_no_value():
    # Arrange
    token = 'test_token'
    line = 'no token'
    file_list = [line]

    # Act + Assert
    with pytest.raises(ValueError):
        value = float(nfo.get_expected_token_value(token, line, file_list))


def test_get_expected_token_value_value_present():
    # Arrange
    token = 'test_token'
    line = 'test_token 4'
    file_list = [line]

    # Act
    value = float(nfo.get_expected_token_value(token, line, file_list))

    # Assert
    assert value == 4.0


@pytest.mark.parametrize("line, expected_result", [
    ('\t 1', '1'),
    ('\t 1 ', '1'),
    (' ', None),
    ("   IW   ", 'IW'),
    ("\t ", None),
    ("   \t   ", None),
    ("", None),
    ("\t   a", 'a'),
    ("a", 'a'),
    ("\"a a\"", 'a a'),
    ("\"ABCD   \"", 'ABCD   '),
    ('"ABCD"', "ABCD"),
])
def test_get_next_value_single_line(line, expected_result):
    # Act
    result = nfo.get_next_value(0, [line])
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file, expected_result", [
    (['\t ', '1'], '1'),
    (['\t ', '\n', '\n', '\n', '\n', '1'], '1'),
    (['!Comment Line 1', '\n', '\n', '\t', ' !Comment Line 2 ', '\n', ' ABCDEFG '], 'ABCDEFG'),
    (['!"First Value"', '"Second Value"'], 'Second Value'),
    (['C comment line', '1'], '1'),
    (['"1 2"'], '1 2'),  # Checks that quoted values are returned in their entirety
    (["! commented line", "  '3 4'\n"], '3 4'),
])
def test_get_next_value_multiple_lines(file, expected_result):
    # Act
    result = nfo.get_next_value(0, file)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file, expected_result", [
    (['\t #comment', '1'], '1'),
    (['#comment', '1'], '1'),
    (['1\t #comment', '!another comment', '1'], '1'),
    (['C comment line', '1'], '1'),
])
def test_get_next_value_different_comment_char(file, expected_result):
    # Act
    result = nfo.get_next_value(0, file, comment_characters=['#', '!'])
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file, single_c_acts_as_comment, expected_result", [
    (['C Comment line ', '1'], True, '1'),
    (['C Comment line ', '1'], False, 'C'),
    (['COMMENT line ', '1'], True, 'COMMENT'),
    (['COMMENT line', '1', ], False, 'COMMENT'),
])
def test_get_next_value_single_c_acts_as_comment(file, single_c_acts_as_comment, expected_result):
    # Act
    result = nfo.get_next_value(0, file, single_c_acts_as_comment=single_c_acts_as_comment)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("line, ignore, expected_result", [
    ('test 1', [], 'test'),
    ('test 1', ['test'], '1'),
    ('test 1', None, 'test'),
    ('test 1', ['TEST'], '1'),
    ('test 1', ['something_else'], 'test'),
    ('test', ['test'], None),
    ('exclude end', ['exclude', 'end'], None),
    ('Include /path/to/include/folder/file.dat another', ['INCLUDE'], '/path/to/include/folder/file.dat'),
    ('KX Include /path/to/include/folder/file.dat another', ['kx', 'INCLUDE'], '/path/to/include/folder/file.dat'),
    ('KX include includes/folder/file.dat another', ['kx', 'include'], 'includes/folder/file.dat'),
    ('exclude excludepartoflongertext 1', ['exclude'], 'excludepartoflongertext'),
    ('exclude ! comment', ['exclude'], None),
])
def test_get_next_value_ignore(line: str, ignore: list[str], expected_result: str):
    # Act
    result = nfo.get_next_value(0, [line], ignore_values=ignore)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("line, expected_result", [
    ('\t 1', '1'),
    ('\t 1 ', '1'),
    (' ', None),
    ("   IW   ", 'IW'),
    ("\t ", None),
    ("   \t   ", None),
    ("", None),
    ("\t   a", 'a'),
    ("a", 'a')
])
def test_get_previous_value_single_line(line, expected_result):
    # Act
    result = fo.get_previous_value([line])
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("line, search_before, expected_result", [
    ('\t 2 1', '1', '2'),
    ('\t 21 1', '1', '21'),
    ('KX INCLUDE', 'INCLUDE', 'KX'),
    ('  \t INCLUDE', 'INCLUDE', None),
    ('  \t test INCLUDE !INCLUDE', 'INCLUDE', 'test'),
])
def test_get_previous_value_single_line_specify_search_before(line, search_before, expected_result):
    # Act
    result = fo.get_previous_value([line], search_before=search_before)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file, search_before, expected_result", [
    (['\t ', '1', '       INCLUDE'], 'INCLUDE', '1'),
    (['\t ', '\n', '     \n', '\n', '\n', '1'], '1', None),
    (['\t ', '1\n', '     \n', '\n', '12 \n', '1'], '1', '12'),
    (['\t ', '3\n', '     \n', '\n', '12 1', '1'], '1', '1'),
    ([' ABCDEFG ', '!Comment Line 1', '\n', '\n', '\t', ' !Comment Line 2 ', '\n' 'START_TEXT'], 'START_TEXT',
     'ABCDEFG'),
    ([' ABCDEFG ', '!Comment Line 1', '\n', '\n', '\t', ' !Comment Line 2 ', '\n', '12_3 START_TEXT'], 'START_TEXT',
     '12_3'),
    (['1', '2 ', ' 3', '!4', ' START_TEXT 5'], 'START_TEXT', '3'),
    (['1', '2 ', ' 3', '!4', '1 START_TEXT 5'], 'START_TEXT', '1'),
    ([' Token INCLUDE /path VALUE HIJK', '\n' 'INCLUDE /file_name'], 'INCLUDE', 'HIJK'),
])
def test_get_previous_value_multiple_lines_specify_search_before(file, search_before, expected_result):
    # Act
    result = fo.get_previous_value(file_as_list=file, search_before=search_before)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file_contents, expected_header_index, expected_header_result", [
    ('KH \t NAME \t COLUMN1 \t   COLUMN2 \n\n SOMETHING ELSe',
     0, ['KH', 'NAME', 'COLUMN1', 'COLUMN2']),
    ('KH \t NAME \t COLUMN1 \t   COLUMN2 COLUMN3 \n\n SOMETHING ELSe',
     0, ['KH', 'NAME', 'COLUMN1', 'COLUMN2', 'COLUMN3']),
    ('! comment first \n KH \t NAME \t COLUMN1 \t   COLUMN2 ! comment \n 10 well1 10 item',
     1, ['KH', 'NAME', 'COLUMN1', 'COLUMN2']),
    ('well1\n jw  iw   l    RADB \n\n 1  2   3   1.5',
     1, ['JW', 'IW', 'L', 'RADB']),
    ('extra values first \n KH \t NAME \t COLUMN1 \t   COLUMN2 ! comment \n 10 well1 10 item',
     1, ['KH', 'NAME', 'COLUMN1', 'COLUMN2']),
], ids=['basic', 'additional column', 'comments', 'well headers', 'extra starting line'])
def test_get_table_header(file_contents, expected_header_index, expected_header_result):
    # Arrange
    header_values = {
        'KH': 'kh',
        'NAME': 'Name',
        'COLUMN1': 'Column',
        'COLUMN2': 'Column',
        'IW': 'iw',
        'JW': 'jw',
        'L': 'l',
        'RADB': 'RADB',
    }
    file_as_list = file_contents.splitlines()
    # Act
    result_header_index, result_headers = nfo.get_table_header(file_as_list, header_values)

    # Assert
    assert result_header_index == expected_header_index
    assert result_headers == expected_header_result


@pytest.mark.parametrize("headers, line, expected_dictionary, expected_valid_line", [
    (['KH', 'NAME', 'COLUMN1', 'COLUMN2'], '10 well1 value1 0.2',
     {'KH': '10', 'NAME': 'well1', 'COLUMN1': 'value1', 'COLUMN2': '0.2'}, True),
    (['KH', 'NAME', 'COLUMN1', 'COLUMN2'], '10 well1 ',
     {'KH': '10', 'NAME': 'well1', 'COLUMN1': None, 'COLUMN2': None}, False),
    (['KH', 'NAME', ], '10 well1',
     {'KH': '10', 'NAME': 'well1', 'COLUMN1': None, 'COLUMN2': None}, True),
    (['KH', 'NAME', ], '10 well1 !comment',
     {'KH': '10', 'NAME': 'well1', 'COLUMN1': None, 'COLUMN2': None}, True),
    (['KH', 'NAME', 'NOTINDICT'], '10 well1 value !comment',
     {'KH': '10', 'NAME': 'well1', 'COLUMN1': None, 'COLUMN2': None, 'NOTINDICT': 'value'}, True),
], ids=['basic', 'invalid_line (too short)', 'fewer_columns_than_dict', 'comments', 'value not in dict'])
def test_table_line_reader(headers, line, expected_dictionary, expected_valid_line):
    # Arrange
    dict_to_populate = {'KH': None, 'NAME': None, 'COLUMN1': None, 'COLUMN2': None}

    # Act
    result_valid_line, result_dict = nfo.table_line_reader(dict_to_populate, headers, line)

    # Assert
    assert result_dict == expected_dictionary
    assert result_valid_line == expected_valid_line


@pytest.mark.parametrize("value, dtype, na_to_none, expected_result", [
    ('string', str, True, 'string'),
    ('10', int, True, 10),
    ('10', float, True, 10.0),
    ('1.9101', float, True, 1.9101),
    ('#', int, True, None),
    ('NA', int, True, None),
    ('NA', str, False, 'NA'),
    (None, str, False, None),
    (10.0, str, False, '10.0'),
    ('None', str, False, None),
])
def test_correct_datatypes(value, dtype, na_to_none, expected_result):
    # Act
    result = nfo.correct_datatypes(value, dtype, na_to_none)
    # Assert
    assert result == expected_result


def test_load_table_to_objects_basic():
    # Arrange
    property_map = {'NAME': ('name', str), 'KH': ('kh', int), 'L': ('k', float)}

    @dataclass
    class TestClass:
        name: str
        kh: int
        k: float

        def __init__(self, properties_dict, date: str | None = None, date_format: DateFormat | None = None,
                     unit_system: UnitSystem | None = None, start_date: str | None = None):
            for key, prop in properties_dict.items():
                self.__setattr__(key, prop)

    file_contents = '''NAME     KH  L \n\n well1        10   13.5 \n\n well2 20 7.501'''
    file_as_list = file_contents.splitlines()
    expected_dict_1 = {'name': 'well1', 'kh': 10, 'k': 13.5}
    expected_dict_2 = {'name': 'well2', 'kh': 20, 'k': 7.501}
    expected_obj_1 = TestClass(expected_dict_1)
    expected_obj_2 = TestClass(expected_dict_2)
    expected_result = [(expected_obj_1, 2), (expected_obj_2, 4)]

    # Act
    result = nfo.load_table_to_objects(file_as_list, TestClass, property_map, date_format=DateFormat.DD_MM_YYYY)

    # Assert
    assert result == expected_result


def test_load_table_to_objects_date_units():
    # Arrange
    property_map = {'NAME': ('name', str), 'KH': ('kh', int), 'L': ('k', float)}
    date = '20/12/2023'
    units = UnitSystem.ENGLISH

    # the date and units should not be added to this class
    @dataclass
    class TestClass:
        name: str
        kh: int
        k: float

        def __init__(self, properties_dict, date: str | None = None, date_format: DateFormat | None = None,
                     unit_system: UnitSystem | None = None, start_date: str | None = None):
            for key, prop in properties_dict.items():
                self.__setattr__(key, prop)

    # but should be added to this class:
    @dataclass
    class TestClassUnitDates:
        name: str
        kh: int
        k: float

        def __init__(self, properties_dict, date: str | None = None, date_format: DateFormat | None = None,
                     unit_system: UnitSystem | None = None, start_date: str | None = None):
            for key, prop in properties_dict.items():
                self.__setattr__(key, prop)

    file_contents = '''NAME     KH  L \n\n well1        10   13.5 \n\n well2 20 7.501'''
    file_as_list = file_contents.splitlines()
    expected_dict_1 = {'name': 'well1', 'kh': 10, 'k': 13.5}
    expected_dict_2 = {'name': 'well2', 'kh': 20, 'k': 7.501}
    # create expected testclass examples where they shouldn't get the name, date attribute
    expected_obj_1 = TestClass(expected_dict_1)
    expected_obj_2 = TestClass(expected_dict_2)
    expected_result = [(expected_obj_1, 2), (expected_obj_2, 4)]

    # add in the date and unit systems to the kwargs dict
    unit_date_dict = {'date': date, 'unit_system': units}
    expected_dict_1.update(unit_date_dict)
    expected_dict_2.update(unit_date_dict)
    # create a new set of objects that should get the date and unit system
    expected_result_unit_date = [(TestClassUnitDates(expected_dict_1), 2), (TestClassUnitDates(expected_dict_2), 4)]
    # Act
    result = nfo.load_table_to_objects(file_as_list, TestClass, property_map, date, units)
    result_unit_date = nfo.load_table_to_objects(file_as_list, TestClassUnitDates, property_map, date, units)
    # Assert
    assert result == expected_result
    assert result_unit_date == expected_result_unit_date


@pytest.mark.parametrize('file_contents, node1_props, node2_props', [
    ('''NODES
  NAME                           TYPE       DEPTH   TEMP
 ! Riser Nodes
  node1                         NA            NA      #
  node_2        WELLHEAD     1167.3 # 
  ENDNODES
''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     ),

    ('''NODES
  NAME       TYPE       DEPTH   TemP    X     Y       NUMBER  StatiON
 ! Riser Nodes
  node1         NA        NA    60.5    100.5 300.5   1     station
  node_2        WELLHEAD     1167.3 #  10.21085 3524.23 2   station2 ! COMMENT 
  ENDNODES
  content outside of the node statement
  node1         NA        NA    60.5    10.5 3.5   1     station_null
  ''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': 60.5, 'x_pos': 100.5, 'y_pos': 300.5, 'number': 1,
      'station': 'station', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': 10.21085, 'y_pos': 3524.23,
      'number': 2,
      'station': 'station2', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     ),

    ('''NODES
  NAME                           TYPE       DEPTH   TEMP
 ! Riser Nodes
  node1                         NA            NA      #
  ENDNODES
  TIME 01/02/2023
  NODES
    NAME                           TYPE       DEPTH   TEMP

  node_2        WELLHEAD     1167.3 # 
  ENDNODES
''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/02/2023',
      'unit_system': UnitSystem.ENGLISH},
     ),
    ('''NODES
  NAME                           TYPE       DEPTH   TEMP
 ! Riser Nodes
  node1                         NA            NA      #
  ENDNODES
  METRIC
  TIME 01/02/2023
  NODES
    NAME                           TYPE       DEPTH   TEMP

  node_2        WELLHEAD     1167.3 # 
  ENDNODES
''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/02/2023',
      'unit_system': UnitSystem.METRIC},
     ),

    ('''NODES
  NAME       TYPE       DEPTH   TemP    X     Y       NUMBER  StatiON
 ! Riser Nodes
  node1         NA        NA    60.5    100.5 300.5   1     station
  ENDNODES
  NODES
    NAME       TYPE       DEPTH   TemP       NUMBER  StatiON    
node_2        WELLHEAD     1167.3 #  2   station2 
ENDNODES
  content outside of the node statement
  node1         NA        NA    60.5    10.5 3.5   1     station_null
  ''',
     {'name': 'node1', 'type': None, 'depth': None, 'temp': 60.5, 'x_pos': 100.5, 'y_pos': 300.5, 'number': 1,
      'station': 'station', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'x_pos': None, 'y_pos': None, 'number': 2,
      'station': 'station2', 'date': '01/01/2023', 'unit_system': UnitSystem.ENGLISH},
     ),
    ("""  NODES
    NAME TYPE DEPTH TEMP
  node_1 WELLHEAD 1167.3 # 
  ENDNODES
  TIME 1.5
  NODES
  NAME TYPE DEPTH TEMP
  node_2 WELLHEAD 1005.3 10.5
  ENDNODES """,
     {'name': 'node_1', 'type': 'WELLHEAD', 'depth': 1167.3, 'temp': None, 'date': '01/01/2023',
      'unit_system': UnitSystem.ENGLISH},
     {'name': 'node_2', 'type': 'WELLHEAD', 'depth': 1005.3, 'temp': 10.5,
      'date': '1.5', 'unit_system': UnitSystem.ENGLISH}
     )
], ids=['basic', 'all columns', 'times', 'units', 'two tables', 'decimal date'])
def test_collect_all_tables_to_objects(mocker, file_contents, node1_props, node2_props):
    # Arrange
    # mock out a surface file:
    start_date = '01/01/2023'
    mocker.patch('ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4', return_value='uuid1')
    surface_file = NexusFile(location='surface.dat', file_content_as_list=file_contents.splitlines())

    node_1 = NexusNode(node1_props, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)
    node_2 = NexusNode(node2_props, date_format=DateFormat.MM_DD_YYYY, start_date=start_date)

    # line locs for this part of the code refers to line loc relative to the table
    expected_result = [node_1, node_2]

    # Act

    result_dict, _ = ResSimpy.Nexus.nexus_collect_tables.collect_all_tables_to_objects(
        nexus_file=surface_file,
        table_object_map={'NODES': NexusNode,
                          'WELLS': NexusWellConnection, 'GASWELLS': NexusWellConnection}, start_date=start_date,
        default_units=UnitSystem.ENGLISH,
        date_format=DateFormat.MM_DD_YYYY,
    )
    result = result_dict.get('NODES')
    if result_dict.get('WELLS') is not None:
        result.extend(result_dict.get('WELLS'))
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('file_as_list', [
    ("""WELLHEAD
WELL NAME DEPTH X Y\t IPVT\t IWAT
testwell testwell_wellhead 1000 102 302 2 3
ENDWELLHEAD
        """.splitlines()),

    ("""DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL
        """.splitlines())
])
def test_collect_all_tables_to_objects_correct_line_numbers(mocker, file_as_list):
    # Arrange
    mocker.patch(
        "ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4", return_value="uuid_1"
    )

    nexus_file = NexusFile(location="", file_content_as_list=file_as_list)

    expected_object_locations = {'uuid_1': [2]}

    # Act
    nexus_obj_dict, _ = ResSimpy.Nexus.nexus_collect_tables.collect_all_tables_to_objects(
        nexus_file=nexus_file,
        table_object_map={
            "DRILL": NexusDrill,
            "WELLHEAD": NexusWellhead,
        },
        start_date="01/01/2019",
        default_units=UnitSystem.ENGLISH,
        date_format=DateFormat.DD_MM_YYYY,
    )

    # Assert
    # Check that the line numbers are correct
    assert nexus_file.object_locations == expected_object_locations


def test_load_file_as_list_unicode_error(mocker, ):
    # Arrange
    file_contents = 'file\ncontents'
    expected_file_as_list = ['file\n', 'contents']
    file_path = 'file_path.dat'

    def side_effect(filename, mode, errors=None):
        if errors is None:
            raise UnicodeDecodeError('test_error', b'', 0, 0, '')
        else:
            open_mock = mocker.mock_open(read_data=file_contents)
            return open_mock.return_value

    mock_open = Mock(side_effect=side_effect)
    mocker.patch("builtins.open", mock_open)

    # Act
    result = nfo.load_file_as_list(file_path)
    # Assert
    assert result == expected_file_as_list


@pytest.mark.parametrize('line, expected_result', [
    ('some kind of token line', ['some', 'kind', 'of', 'token', 'line']),
    ('some !comment finshes the line', ['some']),
    ('!only comment', []),
    ('', [])
])
def test_split_line(line, expected_result):
    # Act
    result = fo.split_line(line, upper=False)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('line, expected_result', [
    ('some kind of token line', ['SOME', 'KIND', 'OF', 'TOKEN', 'LINE']),
    ('some !comment finshes the line', ['SOME']),
    ('!only comment', []),
    ('', [])
])
def test_split_line(line, expected_result):
    # Act
    result = fo.split_line(line, upper=True)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize('file_as_list, table_header, table_footer', [
    ("""WELLHEAD
WELL NAME DEPTH X Y\t IPVT\t IWAT
testwell testwell_wellhead 1000 102 302 2 3
ENDWELLHEAD
        """.splitlines(), 'WELLHEAD', 'ENDWELLHEAD'),

    # Table keyword repeated in header
    ("""DRILL
WELL    DRILLSITE   DRILLTIME   
well_1  site_1   654.1
ENDDRILL
        """.splitlines(), 'DRILL', 'ENDDRILL')
], ids=['WELLHEAD', 'DRILL'])
def test_check_for_empty_table_returns_correct_indices(mocker, file_as_list, table_header, table_footer):
    # Arrange
    mocker.patch(
        "ResSimpy.DataModelBaseClasses.DataObjectMixin.uuid4", return_value="uuid_1"
    )

    nexus_file = NexusFile(location="", file_content_as_list=file_as_list)

    obj = RemoveObjectOperations(network=None, table_header=table_header, table_footer=table_footer)
    expected_indices_to_remove = [0, 1, 2, 3]

    # Act
    indices_to_remove = obj.check_for_empty_table(file=nexus_file, line_numbers_in_file_to_remove=[2], obj_id='uuid_1')

    # Assert
    assert indices_to_remove == expected_indices_to_remove


def test_add_network_obj(mocker):
    # Arrange

    file_contents = """
TIME 15/01/2025
    
DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

TIME 25/07/2026

TIME 26/07/2026
"""

    expected_file_contents = """
TIME 15/01/2025
    
DRILLSITE
NAME    MAXRIGS
site_1  5
site_2  1
ENDDRILLSITE

TIME 25/07/2026

DRILL
WELL DRILLSITE DRILLTIME
well_1 site_1 30.3
ENDDRILL

TIME 26/07/2026
"""

    table_header = 'DRILL'
    table_footer = 'ENDDRILL'

    nexus_file = NexusFile(location="", file_content_as_list=file_contents.splitlines(keepends=True))

    model = get_fake_nexus_simulator(mocker=mocker)
    model.date_format = DateFormat.DD_MM_YYYY
    model._sim_controls.date_format_string = "%d/%m/%Y"
    model._model_files.surface_files = {1: nexus_file}
    model._start_date = '15/01/2025'

    network_obj = NexusNetwork(model=model, assume_loaded=True)

    obj = AddObjectOperations(table_header=table_header, table_footer=table_footer, model=model, obj_type=NexusDrill)

    # Act
    expected_object = obj.add_network_obj(node_to_add={'drill_site': 'site_1', 'drill_time': 30.3, 'date': '25/07/2026',
                                                       'date_format': DateFormat.DD_MM_YYYY, 'name': 'well_1'},
                                          obj_type=NexusDrill, network=network_obj)

    # Assert
    assert nexus_file.get_flat_list_str_file == expected_file_contents.splitlines(keepends=True)
    assert expected_object == NexusDrill(drillsite='site_1', drill_time=30.3, date_format=DateFormat.DD_MM_YYYY,
                                         date='25/07/2026', name='well_1')
