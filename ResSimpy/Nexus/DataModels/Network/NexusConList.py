"""Holds a class for representing a single ConList or group for the Nexus model."""
from dataclasses import dataclass

from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping
from ResSimpy.DataModelBaseClasses.NetworkList import NetworkList


@dataclass(kw_only=True, init=False)
class NexusConList(NetworkList):
    """Class for representing a single ConList or group for the Nexus model."""

    def __init__(self, name: str, elements_in_the_list: list[str], date: str, date_format: DateFormat) -> None:
        """Initialises the NexusConList class.

        Args:
            name (str): Name of the conlist.
            elements_in_the_list (list[str]): List of connection names in the conlist.
            date (str): Date when the conlist is defined. Persists until the next date is defined.
            date_format (Optional[DateFormat]): The date format of the object.
        """
        super().__init__(name=name, elements_in_the_list=elements_in_the_list, date=date, date_format=date_format)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Returns mapping of keywords."""
        return {}

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(None)

    @property
    def connections(self) -> list[str]:
        """Returns the list of connections in the conlist."""
        return self.elements_in_the_list
