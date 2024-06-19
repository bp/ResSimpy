from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataObjectMixin import DataObjectMixin
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@dataclass(kw_only=True)
class WellList(DataObjectMixin):
    """Class for representing a single WellList or group for the model."""
    wells: list[str]

    def __init__(self, date: str, wells: list[str], name: str, date_format: Optional[DateFormat] = None,
                 start_date: Optional[str] = None) -> None:
        """Initialises the WellList class.

        Args:
            date (str): Date that the well list is created.
            wells (list[str]): A list of the well names in the Welllist.
            name ([str]): The name of the Welllist.
            date_format (Optional[DateFormat]): The date format of the object.
            start_date (Optional[str]): The start date of the model (required if the date is in numerical format).
        """

        super().__init__(date=date, date_format=date_format, start_date=start_date, name=name)

        self.wells = wells
