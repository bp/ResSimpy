from datetime import datetime

from ResSimpy.FileOperations.File import File
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


def test_get_content_between_dates():
    # Arrange
    file_contents = """
    something
    
TIME 15/01/2025

a
b
c

TIME 16/06/2025
d

TIME 25/07/2026
other text 

    """

    start_date = datetime(2025, 1, 15)
    end_date = datetime(2026, 7, 25)

    expected_result = ['TIME 15/01/2025\n', '\n', 'a\n', 'b\n', 'c\n', '\n', 'TIME 16/06/2025\n', 'd\n', '\n',
                       'TIME 25/07/2026\n']
    file_obj = File(location='', file_content_as_list=file_contents.splitlines(keepends=True))

    # Act
    result = file_obj.get_content_between_dates(start_date=start_date, end_date=end_date,
                                                date_format=DateFormat.DD_MM_YYYY)

    # Assert
    assert result == expected_result

# Dates don't match provided dates exactly
# Other date formats (including decimal)
# Eclipse format for date keyword and date format
# Only start