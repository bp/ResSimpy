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
    def convert_to_iso(cls, date: str, date_format: str, start_date: Optional[str] = None) -> ISODateTime:
        converted_date = None

        if date_format is None:
            raise ValueError('Please provide date format')

        if ISODateTime.isfloat(date) and start_date is None:
            raise ValueError('Please provide start date when date is numeric')
        elif ISODateTime.isfloat(date) and start_date is not None:
            if date_format == DateFormat.DD_MM_YYYY:
                converted_date = ISODateTime.strptime(start_date, '%d/%m/%Y') + timedelta(days=float(date))
            elif date_format == DateFormat.MM_DD_YYYY:
                converted_date = ISODateTime.strptime(start_date, '%m/%d/%Y') + timedelta(days=float(date))

        elif date_format == DateFormat.DD_MM_YYYY:
            converted_date = ISODateTime.strptime(date, '%d/%m/%Y')

        elif date_format == DateFormat.MM_DD_YYYY:
            converted_date = ISODateTime.strptime(date, '%m/%d/%Y')

        if converted_date is None:
            raise ValueError('Invalid date format or missing start_date.')

        return converted_date
