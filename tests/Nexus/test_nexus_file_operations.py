import ResSimpy.Nexus.nexus_file_operations as nfo
import pytest
import pandas as pd
import numpy as np


@pytest.mark.parametrize("line_contents, file_contents, expected_result", [
    ("MYTESTTOKEN 3", "MYTESTTOKEN 3\n ANOTHER_TOKEN 8", '3'),
    ("MYTESTTOKEN 123",
     """GOTABLE 
               SG         KRG        KROG        PCGO
          0.000000     0.000000     1.000000     0.000000
          0.085260     0.011210     0.681265     0.000000
          ! Test comment in the middle of the table          
          0.100598     0.014109     0.625140     0.000000
          ANOTHERTOKEN 6
        MYTESTTOKEN 123
          TOKENCONTAINING_MYTESTTOKEN 8
          FINALTOKEN 90

          """,
     '123'),
    ("MYTESTTOKEN",
     """GOTABLE 
       SG         KRG        KROG        PCGO
  0.000000     0.000000     1.000000     0.000000
  0.085260     0.011210     0.681265     0.000000
  ! Test comment in the middle of the table          
  0.100598     0.014109     0.625140     0.000000
  ANOTHERTOKEN 6
MYTESTTOKEN 
7
  TOKENCONTAINING_MYTESTTOKEN 8
  FINALTOKEN 90

  """,
     '7'),
], ids=['basic case', 'multiple lines', 'value on next line'])
def test_get_token_value(mocker, line_contents, file_contents, expected_result):
    # Arrange
    dummy_file_as_list = [y for y in (x.strip() for x in file_contents.splitlines()) if y]
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    result = nfo.get_token_value(token='MYTESTTOKEN', token_line=line_contents,
                                 file_list=dummy_file_as_list)

    # Assert
    assert result == expected_result


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
                          ], ids=["standard case", "token at start", "token at end", "no token", "token commented out",
                                  "token only part of longer word 1", "token only part of longer word 2",
                                  "token before comment", "token then tab", "token then newline", "single character"])
def test_check_token(line_string, token, expected_result):
    # Act
    result = nfo.check_token(token=token, line=line_string)

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
def test_strip_file_of_comments(file_contents, strip_str, expected_result_contents):
    # Arrange
    dummy_file_as_list = file_contents.splitlines()
    expected_result = expected_result_contents.splitlines()

    # Act
    result = nfo.strip_file_of_comments(dummy_file_as_list, strip_str=strip_str)
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


@pytest.mark.parametrize("line, number_tokens, expected_result", [
  ('EQUIL METHOD 1 /path/equil.dat', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat']),
  ('EQUIL METHOD 1 /path/equil.dat ! comment', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat']),
  ('EQUIL METHOD 1 /path/equil.dat TOKEN TOKEN', 6, ['EQUIL', 'METHOD', '1', '/path/equil.dat','TOKEN', 'TOKEN']),
  ('EQUIL METHOD 1 \n /path/equil.dat', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat']),
  ('EQUIL METHOD !comment\n \t 1 ', 3, ['EQUIL', 'METHOD', '1']),
  ('EQUIL\n METHOD\n1\n/path/equil.dat', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat'])
  ], ids=["basic", "more tokens", "get more tokens", "new line", "newline comment", "lots of newlines"])
def test_get_multiple_sequential_tokens(line, number_tokens, expected_result):
    # Arrange
    list_of_strings = line.splitlines()
    # Act
    result = nfo.get_multiple_sequential_tokens(list_of_strings, number_tokens)
    # Assert
    assert result == expected_result


def test_get_multiple_sequential_tokens_fail_case():
    # Arrange
    line = 'EQUIL METHOD'
    number_tokens = 3
    # Act + Assert
    with pytest.raises(ValueError):
        value = nfo.get_multiple_sequential_tokens([line], number_tokens)


@pytest.mark.parametrize("line, expected_result",[
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
def test_get_next_value_single_line(line, expected_result):
    # Act
    result = nfo.get_next_value(0, [line])
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file, expected_result",[
    (['\t ', '1'], '1'),
    (['\t ', '\n', '\n', '\n', '\n', '1'], '1'),
    (['!Comment Line 1','\n', '\n', '\t', ' !Comment Line 2 ', '\n', ' ABCDEFG '], 'ABCDEFG')
])
def test_get_next_value_multiple_lines(file, expected_result):
    # Act
    result = nfo.get_next_value(0, file)
    # Assert
    assert result == expected_result


@pytest.mark.parametrize("file_contents, expected_header_index, expected_header_result",[
    ('KH \t NAME \t COLUMN1 \t   COLUMN2 \n\n SOMETHING ELSe',
        0, ['KH', 'NAME', 'COLUMN1', 'COLUMN2']),
    ('KH \t NAME \t COLUMN1 \t   COLUMN2 COLUMN3 \n\n SOMETHING ELSe',
        0, ['KH', 'NAME', 'COLUMN1', 'COLUMN2', 'COLUMN3']),
    ('! comment first \n KH \t NAME \t COLUMN1 \t   COLUMN2 ! comment \n 10 well1 10 item',
        1, ['KH', 'NAME', 'COLUMN1', 'COLUMN2'])
], ids=['basic', 'additional column', 'comments'])
def test_get_table_header(file_contents, expected_header_index, expected_header_result):
    # Arrange
    header_values = {
        'KH': 'kh',
        'NAME': 'Name',
        'COLUMN1': 'Column',
        'COLUMN2': 'Column',
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
    (['KH', 'NAME',], '10 well1',
    {'KH': '10', 'NAME': 'well1', 'COLUMN1': None, 'COLUMN2': None}, True),
    (['KH', 'NAME',], '10 well1 !comment',
    {'KH': '10', 'NAME': 'well1', 'COLUMN1': None, 'COLUMN2': None}, True),
    (['KH', 'NAME','NOTINDICT'], '10 well1 value !comment',
    {'KH': '10', 'NAME': 'well1', 'COLUMN1': None, 'COLUMN2': None,'NOTINDICT': 'value'}, True),
], ids=['basic', 'invalid_line (too short)', 'fewer_columns_than_dict', 'comments', 'value not in dict'])
def test_table_line_reader(headers, line, expected_dictionary, expected_valid_line):
    # Arrange
    dict_to_populate = {'KH': None, 'NAME': None, 'COLUMN1': None, 'COLUMN2': None}

    # Act
    result_valid_line, result_dict = nfo.table_line_reader(dict_to_populate, headers, line)

    # Assert
    assert result_dict == expected_dictionary
    assert result_valid_line == expected_valid_line


@pytest.mark.parametrize("value, dtype, na_to_none, expected_result",[
    ('string', str, True, 'string'),
    ('10', int, True, 10),
    ('10', float, True, 10.0),
    ('1.9101', float, True, 1.9101),
    ('#', int, True, None),
    ('NA', int, True, None),
    ('NA', str, False, 'NA'),
    (None, str, False, None),
    (10.0, str, False, '10.0'),
])
def test_correct_datatypes(value, dtype, na_to_none, expected_result):
    # Act
    result = nfo.correct_datatypes(value, dtype, na_to_none)
    # Assert
    assert result == expected_result
