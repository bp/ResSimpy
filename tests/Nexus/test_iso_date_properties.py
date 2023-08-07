import datetime

import pytest

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


def test_mmddyyyy_date_format():
    # Arrange
    completion = NexusCompletion(date='01/14/2022',
                                 date_format=DateFormat.MM_DD_YYYY)

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


def test_mmddyyyy_date_no_of_days():
    # Arrange
    completion = NexusCompletion(date='5',
                                 date_format=DateFormat.MM_DD_YYYY,
                                 start_date='01/14/2022')

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 19, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date

# test for date as numeric and start date not provided
def test_mmddyyyy_date_no_of_days_blankStartDate():
    # Arrange
    with pytest.raises(ValueError):
        NexusCompletion(date='5', date_format=DateFormat.MM_DD_YYYY)


def test_ddmmyyyy_date_format():
    # Arrange
    completion = NexusCompletion(date='14/01/2022',
                                 date_format=DateFormat.DD_MM_YYYY)

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


def test_ddmmyyyy_date_no_of_days():
    # Arrange
    completion = NexusCompletion(date='5',
                                 date_format=DateFormat.DD_MM_YYYY,
                                 start_date='14/01/2022')

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 19, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date

# test for date as numeric and start date not provided
def test_ddmmyyyy_date_no_of_days_blankStartDate():
    # Arrange
    with pytest.raises(ValueError):
        NexusCompletion(date='5', date_format=DateFormat.DD_MM_YYYY)

def test_start_date_decimal_mmddyyyyFormat():
    # Arrange
    completion = NexusCompletion(date='5.5', start_date='01/14/2022',
                                 date_format=DateFormat.MM_DD_YYYY)
    expected_iso_date = datetime.datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


def test_date_decimal_ddmmyyyyFormat():
    # Arrange
    completion = NexusCompletion(date='5.5', start_date='14/01/2022',
                                 date_format=DateFormat.DD_MM_YYYY)
    expected_iso_date = datetime.datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date
