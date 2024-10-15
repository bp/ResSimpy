"""Holds a class for representing a single WellList or group for the Nexus model."""
from dataclasses import dataclass

from ResSimpy.DataModelBaseClasses.NetworkList import NetworkList
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True, init=False)
class NexusWellList(NetworkList):
    """Class for representing a single WellList or group for the Nexus model."""

    def __init__(self, name: str, elements_in_the_list: list[str], date: str, date_format: DateFormat) -> None:
        """Initialises the NexusWellList class.

        Args:
            name (str): Name of the welllist.
            elements_in_the_list (list[str]): List of well names in the welllist.
            date (str): Date when the welllist is defined. Persists until the next date is defined.
            date_format (Optional[DateFormat]): The date format of the object.
        """
        super().__init__(name=name, elements_in_the_list=elements_in_the_list, date=date, date_format=date_format)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Returns keyword mapping from well list of the Nexus model."""
        return {}

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(None)

    @property
    def wells(self) -> list[str]:
        """Returns the list of wells in the welllist."""
        return self.elements_in_the_list
