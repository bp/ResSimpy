"""Holds a class for representing a single WellList or group for the Nexus model."""
from dataclasses import dataclass

from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.WellLists import WellList


@dataclass(kw_only=True, init=False)
class NexusWellList(WellList):
    """Class for representing a single WellList or group for the Nexus model."""

    def __init__(self, name: str, wells: list[str], date: str, date_format: DateFormat) -> None:
        """Initialises the NexusWellList class.

        Args:
            name (str): Name of the welllist.
            wells (list[str]): List of well names in the welllist.
            date (str): Date when the welllist is defined. Persists until the next date is defined.
            date_format (Optional[DateFormat]): The date format of the object.
        """
        super().__init__(name=name, wells=wells, date=date, date_format=date_format)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        return {}

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(None)
