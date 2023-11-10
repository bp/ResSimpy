import datetime

import pytest

from ResSimpy.ISODateTime import ISODateTime
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@pytest.mark.maintain_datetime_behaviour
def test_mmddyyyy_date_format(mocker):
    # Arrange
    completion = NexusCompletion(date='01/14/2022', date_format=DateFormat.MM_DD_YYYY)

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_mmddyyyy_date_no_of_days():
    # Arrange
    completion = NexusCompletion(date='5', date_format=DateFormat.MM_DD_YYYY, start_date='01/14/2022')

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 19, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
# test for date as numeric and start date not provided
def test_mmddyyyy_date_no_of_days_blankStartDate():
    # Arrange
    with pytest.raises(ValueError):
        NexusCompletion(date='5', date_format=DateFormat.MM_DD_YYYY)


@pytest.mark.maintain_datetime_behaviour
def test_ddmmyyyy_date_format():
    # Arrange
    completion = NexusCompletion(date='14/01/2022', date_format=DateFormat.DD_MM_YYYY)

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_ddmmyyyy_date_no_of_days():
    # Arrange
    completion = NexusCompletion(date='5', date_format=DateFormat.DD_MM_YYYY, start_date='14/01/2022')

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime.datetime(2022, 1, 19, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
# test for date as numeric and start date not provided
def test_ddmmyyyy_date_no_of_days_blankStartDate():
    # Arrange
    with pytest.raises(ValueError):
        NexusCompletion(date='5', date_format=DateFormat.DD_MM_YYYY)


@pytest.mark.maintain_datetime_behaviour
def test_start_date_decimal_mmddyyyyFormat():
    # Arrange
    completion = NexusCompletion(date='5.5', date_format=DateFormat.MM_DD_YYYY, start_date='01/14/2022')
    expected_iso_date = datetime.datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_date_decimal_ddmmyyyyFormat():
    # Arrange
    completion = NexusCompletion(date='5.5', date_format=DateFormat.DD_MM_YYYY, start_date='14/01/2022')
    expected_iso_date = datetime.datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_dd_MMM_yyyy_date_format():
    # Arrange
    completion = NexusCompletion(date='14 JAN 2022', date_format=DateFormat.DD_MMM_YYYY)

    expected_iso_date_str = '2022-01-14T00:00:00'
    expected_iso_date = datetime.datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date
    assert str(completion.iso_date) == expected_iso_date_str


@pytest.mark.maintain_datetime_behaviour
def test_invalid_date_format_raises_error():
    # Arrange

    # Act
    with pytest.raises(ValueError) as e:
        _ = NexusCompletion(date='1234', date_format=DateFormat.DD_MMM_YYYY, start_date='01/01/2023')

    # Assert
    assert str(e.value) == 'Invalid date format or missing start_date.'


@pytest.mark.maintain_datetime_behaviour
def test_datetime_to_iso():
    # Arrange
    date_to_convert = datetime.datetime(2022, 1, 19)
    expected_iso_date = ISODateTime(2022, 1, 19)

    # Act
    result = ISODateTime.datetime_to_iso(date_to_convert, '%Y-%m-%d %H:%M:%S')

    # Assert
    assert result == expected_iso_date
