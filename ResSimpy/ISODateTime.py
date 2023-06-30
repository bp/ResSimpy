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

    def convert_to_iso(self):

        date_format = self.date_format
        start_date = self.date
        no_of_days = self.no_of_days

        if ISODateTime.isfloat(no_of_days):
            if date_format == DateFormat.DD_MM_YYYY:
                converted_date = ISODateTime.strptime(start_date, '%d/%m/%Y') + timedelta(days=float(no_of_days))
            elif date_format == DateFormat.MM_DD_YYYY:
                converted_date = ISODateTime.strptime(start_date, '%m/%d/%Y') + timedelta(days=float(no_of_days))

        elif date_format == DateFormat.DD_MM_YYYY:
            converted_date = ISODateTime.strptime(start_date, '%d/%m/%Y')

        elif date_format == DateFormat.MM_DD_YYYY:
            converted_date = ISODateTime.strptime(start_date, '%m/%d/%Y')

        return converted_date
