import datetime

from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


def test_usa_date_format():
    # Arrange
    completion = NexusCompletion(date='01/14/2022',
                                 date_format=DateFormat.MM_DD_YYYY)

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.date_ISO

    # Assert
    assert result_date == expected_iso_date


def test_european_date_format():
    # Arrange
    completion = NexusCompletion(date='14/01/2022',
                                 date_format=DateFormat.DD_MM_YYYY)
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.date_ISO

    # Assert
    assert result_date == expected_iso_date


def test_no_of_days_format_usaformat():
    # Arrange
    completion = NexusCompletion(date='01/14/2022', no_of_days='5',
                                 date_format=DateFormat.MM_DD_YYYY)
    expected_iso_date = datetime.datetime(2022, 1, 19, 0, 0, 0)

    # Act
    result_date = completion.date_ISO

    # Assert
    assert result_date == expected_iso_date


def test_no_of_days_format_europeanformat():
    # Arrange
    completion = NexusCompletion(date='14/01/2022', no_of_days='5',
                                 date_format=DateFormat.DD_MM_YYYY)
    expected_iso_date = datetime.datetime(2022, 1, 19, 0, 0, 0)

    # Act
    result_date = completion.date_ISO

    # Assert
    assert result_date == expected_iso_date


def test_no_of_days_decimal_usaformat():
    # Arrange
    completion = NexusCompletion(date='01/14/2022', no_of_days='5.5',
                                 date_format=DateFormat.MM_DD_YYYY)
    expected_iso_date = datetime.datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.date_ISO

    # Assert
    assert result_date == expected_iso_date


def test_no_of_days_decimal_europeanformat():
    # Arrange
    completion = NexusCompletion(date='14/01/2022', no_of_days='5.5',
                                 date_format=DateFormat.DD_MM_YYYY)
    expected_iso_date = datetime.datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.date_ISO

    # Assert
    assert result_date == expected_iso_date
