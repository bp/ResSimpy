from __future__ import annotations
from typing import Optional
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from datetime import datetime, timedelta


class ISODateTime(datetime):
    """A class representing an extension of datetime class,  returns back date in ISO datetime format."""

    def __repr__(self) -> str:
        """Return the object representation, but formatted in ISO format."""
        basic_string = super().__repr__()
        iso_string = basic_string.replace(' ', 'T')
        return iso_string

    def __str__(self) -> str:
        """Return the string representation, but formatted in ISO format."""
        basic_string = super().__str__()
        iso_string = basic_string.replace(' ', 'T')
        return iso_string

    @staticmethod
    def isfloat(no_of_days: str) -> bool:
        if no_of_days is not None:
            try:
                float(no_of_days)
                return True
            except ValueError:
                return False
        else:
            return False

    @classmethod
    def convert_to_iso(cls, date: str, date_format: DateFormat, start_date: Optional[str] = None) -> ISODateTime:
        """Converts an ordinary date to an ISODate format.

        Args:
            date (str): The date as it is written in the model file.
            date_format (DateFormat): The date format to use to convert the date.
            start_date (Optional[str]): The start date of the model (required if the date is a number of days from the
                start).

        Raises:
            ValueError: if the provided parameters cannot produce a valid date.

        Returns:
        ISODateTime: an initialised ISODateTime class instance for the date provided.
        """
        converted_date = None

        if date_format is None:
            raise ValueError('Please provide a date format')

        if ISODateTime.isfloat(date) and start_date is None:
            raise ValueError('Please provide start date when date is numeric')
        elif ISODateTime.isfloat(date) and start_date is not None:
            if date_format == DateFormat.DD_MM_YYYY:
                converted_date = ISODateTime.strptime(start_date, '%d/%m/%Y') + timedelta(days=float(date))
            elif date_format == DateFormat.MM_DD_YYYY:
                converted_date = ISODateTime.strptime(start_date, '%m/%d/%Y') + timedelta(days=float(date))

        elif date_format == DateFormat.DD_MM_YYYY:
            try:
                converted_date = ISODateTime.strptime(date, '%d/%m/%Y')
            except ValueError:  # Handling the case where a time has been added
                converted_date = ISODateTime.strptime(date, '%d/%m/%Y(%H:%M:%S)')

        elif date_format == DateFormat.MM_DD_YYYY:
            try:
                converted_date = ISODateTime.strptime(date, '%m/%d/%Y')
            except ValueError:  # Handling the case where a time has been added
                converted_date = ISODateTime.strptime(date, '%m/%d/%Y(%H:%M:%S)')

        elif date_format == DateFormat.DD_MMM_YYYY:
            converted_date = ISODateTime.strptime(date, '%d %b %Y')

        elif date_format == DateFormat.DD_MM_YYYY_h_m_s:
            converted_date = ISODateTime.strptime(date, '%d/%m/%Y(%H:%M:%S)')

        elif date_format == DateFormat.MM_DD_YYYY_h_m_s:
            converted_date = ISODateTime.strptime(date, '%m/%d/%Y(%H:%M:%S)')

        if converted_date is None:
            raise ValueError('Invalid date format or missing start_date.')

        return converted_date

    @classmethod
    def datetime_to_iso(cls, date: datetime, datetime_format: str = '%Y-%m-%d') -> ISODateTime:
        """Converts datetime object to ISODateTime object."""
        return ISODateTime.strptime(str(date), datetime_format)
