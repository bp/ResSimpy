from datetime import datetime

import pytest

from ResSimpy import NexusSimulator
from ResSimpy.Time.ISODateTime import ISODateTime
from ResSimpy.Nexus.DataModels.Network.NexusNode import NexusNode
from ResSimpy.Nexus.DataModels.NexusCompletion import NexusCompletion
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from tests.utility_for_tests import get_fake_nexus_simulator


@pytest.mark.maintain_datetime_behaviour
def test_mmddyyyy_date_format(mocker):
    # Arrange
    completion = NexusCompletion(date='01/14/2022', date_format=DateFormat.MM_DD_YYYY)

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_mmddyyyy_date_no_of_days():
    # Arrange
    completion = NexusCompletion(date='5', date_format=DateFormat.MM_DD_YYYY, start_date='01/14/2022')

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime(2022, 1, 19, 0, 0, 0)

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
    expected_iso_date = datetime(2022, 1, 14, 0, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_ddmmyyyy_date_no_of_days():
    # Arrange
    completion = NexusCompletion(date='5', date_format=DateFormat.DD_MM_YYYY, start_date='14/01/2022')

    # expected_iso_date_str = 2022-01-14T00:00:00
    expected_iso_date = datetime(2022, 1, 19, 0, 0, 0)

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
    expected_iso_date = datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_date_decimal_ddmmyyyyFormat_Completion():
    # Arrange
    completion = NexusCompletion(date='5.5', date_format=DateFormat.DD_MM_YYYY, start_date='14/01/2022')
    expected_iso_date = datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_date_decimal_ddmmyyyyFormat_Node():
    # Arrange
    completion = NexusNode(date='5.5', date_format=DateFormat.DD_MM_YYYY, start_date='14/01/2022', properties_dict={})
    expected_iso_date = datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_date_decimal_ddmmyyyyFormat_Node_all_in_properties():
    # Arrange
    completion = NexusNode(
        properties_dict={'date': '5.5', 'date_format': DateFormat.DD_MM_YYYY, 'start_date': '12/01/2022'})
    expected_iso_date = datetime(2022, 1, 17, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_date_decimal_ddmmyyyyFormat_more_classes():
    # Arrange
    completion = NexusNode(date='5.5', date_format=DateFormat.DD_MM_YYYY, start_date='14/01/2022', properties_dict={})
    expected_iso_date = datetime(2022, 1, 19, 12, 0, 0)

    # Act
    result_date = completion.iso_date

    # Assert
    assert result_date == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
def test_dd_MMM_yyyy_date_format():
    # Arrange
    completion = NexusCompletion(date='14 JAN 2022', date_format=DateFormat.DD_MMM_YYYY)

    expected_iso_date_str = '2022-01-14T00:00:00'
    expected_iso_date = datetime(2022, 1, 14, 0, 0, 0)

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
    date_to_convert = datetime(2022, 1, 19)
    expected_iso_date = ISODateTime(2022, 1, 19)

    # Act
    result = ISODateTime.datetime_to_iso(date_to_convert, '%Y-%m-%d %H:%M:%S')

    # Assert
    assert result == expected_iso_date


@pytest.mark.maintain_datetime_behaviour
@pytest.mark.parametrize('iso_date, expected_str, dateformat', [
    (ISODateTime(2022, 1, 19), '19 JAN 2022', DateFormat.DD_MMM_YYYY),
    (ISODateTime(2022, 1, 19, 12, 0, 0), '19 JAN 2022 12:00:00', DateFormat.DD_MMM_YYYY),
    (ISODateTime(2022, 1, 19), '19/01/2022', DateFormat.DD_MM_YYYY),
    (ISODateTime(2022, 1, 19, 12, 0, 0), '19/01/2022(12:00:00)', DateFormat.DD_MM_YYYY),
    (ISODateTime(2022, 1, 19), '01/19/2022', DateFormat.MM_DD_YYYY),
    (ISODateTime(2022, 1, 19, 12, 0, 0), '01/19/2022(12:00:00)', DateFormat.MM_DD_YYYY),
])
def test_datetime_to_iso(iso_date, expected_str, dateformat):
    # Arrange
    # Act
    result = iso_date.strftime_dateformat(dateformat)

    # Assert
    assert result == expected_str


@pytest.mark.maintain_datetime_behaviour
@pytest.mark.parametrize('initial_date_str, date_format, expected_date_object, datetime_format', [
    ('14/01/2025', DateFormat.DD_MM_YYYY, datetime(2025, 1, 14), '%Y-%m-%d %H:%M:%S'),
    ('01/14/2025', DateFormat.MM_DD_YYYY, datetime(2025, 1, 14), '%Y-%m-%d %H:%M:%S'),
    ('14/01/2025(23:11:01)', DateFormat.DD_MM_YYYY, datetime(2025, 1, 14, 23, 11, 1), '%Y-%m-%d %H:%M:%S'),
    ('01/14/2025(23:11:01)', DateFormat.MM_DD_YYYY, datetime(2025, 1, 14, 23, 11, 1), '%Y-%m-%d %H:%M:%S'),
    ('14 JAN 2025', DateFormat.DD_MMM_YYYY, datetime(2025, 1, 14), '%Y-%m-%d %H:%M:%S'),
    ('14 JAN 2025 23:11:01', DateFormat.DD_MMM_YYYY, datetime(2025, 1, 14, 23, 11, 1), '%Y-%m-%d %H:%M:%S'),
    ('14 JAN 2025 23:11:01.1234', DateFormat.DD_MMM_YYYY, datetime(2025, 1, 14, 23, 11, 1, 123400),
     '%Y-%m-%d %H:%M:%S.%f'),
    ('1 NOV 2024 23:11:01', DateFormat.DD_MMM_YYYY, datetime(2024, 11, 1, 23, 11, 1), '%Y-%m-%d %H:%M:%S'),
], ids=['dd/mm/yyyy', 'mm/dd/yyyy', 'dd/mm/yyyy(time)', 'mm/dd/yyyy(time)', '3 letter month',
        '3 letter month with time', '3 letter month with time + decimal seconds', 'single digit day'])
def test_convert_to_iso(initial_date_str, date_format, expected_date_object, datetime_format):
    # Arrange
    expected_iso_date_object = ISODateTime.datetime_to_iso(date=expected_date_object,
                                                           datetime_format=datetime_format)

    # Act
    result = ISODateTime.convert_to_iso(date=initial_date_str, date_format=date_format)

    # Assert
    assert result == expected_iso_date_object


@pytest.mark.maintain_datetime_behaviour
def test_nexus_simulator_start_iso_date(mocker):
    # Arrange
    start_date = '01/14/2022'
    model = get_fake_nexus_simulator(mocker, start_date=start_date)
    expected_date = ISODateTime(year=2022, month=1, day=14)

    # Act + Assert
    assert model.start_date == start_date
    assert model.start_iso_date == expected_date
