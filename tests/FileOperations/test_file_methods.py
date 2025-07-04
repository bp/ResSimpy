from datetime import datetime

import pytest

from ResSimpy.FileOperations.File import File
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@pytest.mark.parametrize( 'file_contents, start_date, end_date, date_format, expected_result',
    [
    # Basic Case
    ("""
    something
    
TIME 15/01/2025

a
b
c

TIME 16/06/2025
d

TIME 25/07/2026
other text 

    """,
    datetime(2025, 1, 15),
    datetime(2026, 7, 25),
    DateFormat.DD_MM_YYYY,
['TIME 15/01/2025\n', '\n', 'a\n', 'b\n', 'c\n', '\n', 'TIME 16/06/2025\n', 'd\n', '\n',
                       'TIME 25/07/2026\n']
      ),

     # No exact matches
     ("""
    something

TIME 14/01/2025

a
b
c

TIME 16/06/2025
d

TIME 26/07/2026
other text 

    """,
      datetime(2025, 1, 15),
      datetime(2026, 7, 25),
      DateFormat.DD_MM_YYYY,
      ['TIME 16/06/2025\n', 'd\n', '\n', 'TIME 26/07/2026\n']
      ),

    # MM/DD/YYY date format
    ("""
    something

TIME 01/15/2025

a
b
c

TIME 06/16/2025
d

TIME 07/25/2026
other text 

    """,
         datetime(2025, 1, 15),
         datetime(2026, 7, 25),
         DateFormat.MM_DD_YYYY,
         ['TIME 01/15/2025\n', '\n', 'a\n', 'b\n', 'c\n', '\n', 'TIME 06/16/2025\n', 'd\n', '\n',
          'TIME 07/25/2026\n']),

    # Decimal date format
    ("""
    something

TIME 1

a
b
c

TIME 16.5
d

TIME 4566
other text 

    """,
         datetime(2025, 1, 15),
         datetime(2026, 7, 25),
         DateFormat.DD_MM_YYYY,
         ['TIME 16.5\n', 'd\n', '\n', 'TIME 4566\n']
         ),

        # Only one time card
        ("""
    something

TIME 15/01/2025

a
b
c
""",
         datetime(2025, 1, 15),
         datetime(2026, 7, 25),
         DateFormat.DD_MM_YYYY,
         ['TIME 15/01/2025\n', '\n', 'a\n', 'b\n', 'c\n']
         ),

        # Different time card format
        ("""
    something

DATES
 15 JAN 2025 /
/

a
b
c

DATES
 16 JUN 2025 /
/
d

DATES
 25 JUL 2026 /
/
other text 

    """,
         datetime(2025, 1, 15),
         datetime(2026, 7, 25),
         DateFormat.DD_MMM_YYYY,
         ['DATES\n', ' 15 JAN 2025 /\n', '/\n',  '\n', 'a\n', 'b\n', 'c\n', '\n', 'DATES\n',
          ' 16 JUN 2025 /\n', '/\n', 'd\n', '\n', 'DATES\n']
         ),
], ids=['Basic Case', 'No exact matches', 'mmddyyyy format', 'decimal date format', 'only one time card',
        'Different time card format']
)
def test_get_content_between_dates(file_contents, start_date, end_date, date_format, expected_result):
    # Arrange
    file_obj = File(location='', file_content_as_list=file_contents.splitlines(keepends=True))

    # Act
    result = file_obj.get_content_between_dates(start_date=start_date, end_date=end_date,
                                                date_format=date_format, model_start_date='01/01/2025')

    # Assert
    assert result == expected_result

@pytest.mark.parametrize('include_objects, filename, expected_result',
[  # Basic case
   ([File(location='/path/to/file_1.dat', file_content_as_list=[]),
     File(location='/path/to/file_2.dat', file_content_as_list=[])],
    'file_1.dat',
    [File(location='/path/to/file_1.dat', file_content_as_list=[])]
   ),

   # No matches
   ([File(location='/path/to/file_1.dat', file_content_as_list=[]),
     File(location='/path/to/file_2.dat', file_content_as_list=[])],
    'file_3.dat',
    []
   ),

   # Multiple matches
   ([File(location='/path/to/file_1.dat', file_content_as_list=[]),
     File(location='/path/to/file_2.dat', file_content_as_list=[]),
     File(location='/path/to/other/file_1.dat', file_content_as_list=[])],
    'file_1.dat',
    [File(location='/path/to/file_1.dat', file_content_as_list=[]),
     File(location='/path/to/other/file_1.dat', file_content_as_list=[])]
   ),

   # Match multiple levels down
   ([File(location='/path/to/file_1.dat', file_content_as_list=[],
          include_objects=[File(location='/path/to/embedded/file_3.dat', file_content_as_list=[])]),
     File(location='/path/to/file_2.dat', file_content_as_list=[])],
    'file_3.dat',
    [File(location='/path/to/embedded/file_3.dat', file_content_as_list=[])]
   ),

], ids=['Basic Case', 'No matches', 'Multiple matches', 'Match further down the tree'])
def test_get_include_file_from_filename(include_objects, filename, expected_result):
    # Arrange
    base_file = File(location='', file_content_as_list=[], include_objects=include_objects)

    # Act
    result = base_file.get_include_file_from_filename(filename=filename)

    # Assert
    assert result == expected_result
