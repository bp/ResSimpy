import pytest
from pytest_mock import MockerFixture

import ResSimpy.FileOperations.file_operations as fo


@pytest.mark.parametrize("line_contents, file_contents, expected_result, expected_line_index", [
    ("MYTESTTOKEN 3", "MYTESTTOKEN 3\n ANOTHER_TOKEN 8", '3', 0),
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
     '123', 7),
    ("MYTESTTOKEN",
     """GOTABLE 
       SG         KRG        KROG        PCGO
  0.000000     0.000000     1.000000     0.000000
  0.085260     0.011210     0.681265     0.000000
  ! Test comment in the middle of the table    
C Another comment using 'C'        
  0.100598     0.014109     0.625140     0.000000
  ANOTHERTOKEN 6
MYTESTTOKEN 
7
  TOKENCONTAINING_MYTESTTOKEN 8
  FINALTOKEN 90

  """,
     '7', 9),
    ("MYTESTTOKEN",
     '''MYTESTTOKEN
     C Comment line
     token_value''',
     'token_value', 2),
    ("not a comment C MYTESTTOKEN",
     '''not a comment C MYTESTTOKEN
     C Comment line
     C
     Ctoken_value''',
     'Ctoken_value', 3),
    ("MYTESTTOKEN",
     '''MYTESTTOKEN
     C Comment line
     "token value"''',
     'token value', 2),

    ("Values before MYTESTTOKEN",
     '''Values before MYTESTTOKEN
     C Comment line
     ! another comment
     !comment
     "token value"''',
     'token value', 4),

    ("MYTESTTOKEN",
     """MYTESTTOKEN
   'value in quotes'
     
     /""",
    'value in quotes',
     1)
], ids=['basic case', 'multiple lines', 'value on next line', 'Comment character C', 'complex C comment'
    , 'get value in double quotes', 'more values before token', 'value in quotes'])
def test_get_token_value(mocker: MockerFixture, line_contents, file_contents, expected_result, expected_line_index):
    # Arrange
    dummy_file_as_list = [y for y in (x.strip() for x in file_contents.splitlines()) if y]
    open_mock = mocker.mock_open(read_data=file_contents)
    mocker.patch("builtins.open", open_mock)

    # Act
    result = fo.get_token_value(token='MYTESTTOKEN', token_line=line_contents,
                                file_list=dummy_file_as_list, remove_quotation_marks=True)
    with_index_result = fo.get_token_value_with_line_index(token='MYTESTTOKEN', token_line=line_contents,
                                                           file_list=dummy_file_as_list, remove_quotation_marks=True)
    # Assert
    assert result == expected_result
    assert with_index_result == (expected_result, expected_line_index)


@pytest.mark.parametrize("line, number_tokens, expected_result, comment_chars", [
    ('EQUIL METHOD 1 /path/equil.dat', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat'], None),
    ('EQUIL METHOD 1 /path/equil.dat ! comment', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat'], None),
    ('EQUIL NorPT METHOD 1 /path/equil.dat TOKEN TOKEN', 6,
     ['EQUIL', 'METHOD', '1', '/path/equil.dat', 'TOKEN', 'TOKEN'], None),
    ('EQUIL METHOD 1 \n /path/equil.dat', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat'], None),
    ('EQUIL METHOD !comment\n \t 1 ', 3, ['EQUIL', 'METHOD', '1'], None),
    ('EQUIL\n NORPT METHOD\n1\n/path/equil.dat', 4, ['EQUIL', 'METHOD', '1', '/path/equil.dat'], None),
    ('EQUIL METHOD 1 /path/equil.dat', 2, ['EQUIL', 'METHOD'], None),
    ('\n \n \n EQUIL --comment\n METHOD 1 /path/equil.dat', 2, ['EQUIL', 'METHOD'], ['--']),
], ids=["basic", "more tokens", "get more tokens", "new line", "newline comment", "lots of newlines",
        "more text than declared tokens", "starting with new lines"])
def test_get_multiple_sequential_values(line, number_tokens, expected_result, comment_chars):
    # Arrange
    list_of_strings = line.splitlines()
    # Act
    result = fo.get_multiple_expected_sequential_values(list_of_strings, number_tokens, ['NORPT'],
                                                        comment_characters=comment_chars)
    # Assert
    assert result == expected_result



def test_get_multiple_sequential_values_fail_case():
    # Arrange
    line = 'EQUIL METHOD \n \n \n'
    number_tokens = 3
    expected_error_str = ('Too many values requested from the list of strings passed, instead found: 2 values, '
                          'out of the requested 3')
    # Act + Assert
    with pytest.raises(ValueError) as ve:
        value = fo.get_multiple_expected_sequential_values(line.splitlines(), number_tokens, [])
    result_error_msg = str(ve.value)
    assert result_error_msg == expected_error_str


@pytest.mark.parametrize("list_of_strings, value_number_to_get, expected_result", [
    (["a"], 1, 'a'),
    ([" 1 2 \t 3 4"], 3, '3'),
    ([" 1 2 \t 3 4"], 1, '1'),
    ([" A 2 \t C 4"], 3, 'C'),
    ([" 1 2 \t 3"], 4, None),
    ([" 1 ", "2 \t 3 ", "4"], 3, '3'),
    ([" 1 ", "2 \t 3 ", "4"], 4, '4'),
    ([" Value1 ", "Value2 \t", "   ", " Value3 ", "Value4"], 3, 'Value3'),
    ([], 1, None),
])
def test_get_nth_value(list_of_strings, value_number_to_get, expected_result):
    # Act
    result = fo.get_nth_value(list_of_strings=list_of_strings, value_number=value_number_to_get, ignore_values=[])

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("long_string, expected_result, max_length", [
    ('This is a long string that needs to be split into multiple lines based on a certain length.\n',
     'This is a long string that needs to be split into multiple lines\nbased on a certain length.\n', 68),
    ('This is a long string that needs to be split into multiple lines based on a certain length.\n',
     'This is a long string that needs to be split into multiple lines based on a certain length.\n', 100),
    ('This is a long string that needs to be split into multiple lines based on a certain length.\n',
     'This is a long\nstring that needs to\nbe split into\nmultiple lines based\non a certain length.\n', 20), ])
def test_split_lines_for_long_string(long_string, expected_result, max_length):
    # Arrange
    # Act
    result = fo.split_lines_for_long_string(long_string, max_length=max_length)

    # Assert
    assert result == expected_result


def test_split_list_of_strings_by_length():
    # Arrange
    list_of_strings = ['This is a long string that\n', 'needs to be split into multiple lines\n']
    expected_result = [
        'This is a long\nstring that\n',
        'needs to be split\ninto multiple lines\n'
    ]
    max_length = 20

    # Act
    result = fo.split_list_of_strings_by_length(list_of_strings, max_length)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("date_str, start_index", [
    ("""DATES
    25 JUL 2026 /
    /
    """, 0),

    ("""DATES
    15 JAN 2025 /
/
    
DATES
    25 JUL         2026 /
/
    """, 4),

    ("""DATES
    15 JAN 2025 /
/
   
   
    
DATES


    25 JUL         2026 /
/
    """, 6)
], ids=['simple case', 'multiple occurrences of token', 'Multiple blank lines + whitespace'])
def test_load_three_part_date(date_str: str, start_index: int):
    # Arrange

    # Act
    result = fo.load_in_three_part_date(initial_token='DATES', token_line='DATES\n',
                                        file_as_list=date_str.splitlines(keepends=True), start_index=start_index)

    # Assert
    assert result == "25 JUL 2026"


def test_load_three_part_date_no_token():
    # Arrange
    token_line = """   25 JUL  2026"""

    # Act
    result = fo.load_in_three_part_date(initial_token=None, token_line=token_line,
                                        file_as_list=[token_line], start_index=0)

    # Assert
    assert result == "25 JUL 2026"