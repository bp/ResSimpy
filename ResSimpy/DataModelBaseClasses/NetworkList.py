from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.DataObjectMixin import DataObjectMixin
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@dataclass(kw_only=True)
class NetworkList(DataObjectMixin, ABC):
    """Abstract Base Class for representing a single NetworkList or group for the model."""
    elements_in_the_list: list[str]

    def __init__(self, date: str, elements_in_the_list: list[str], name: str, date_format: Optional[DateFormat] = None,
                 start_date: Optional[str] = None) -> None:
        """Initialises the NetworkList class.

        Args:
            date (str): Date that the con list is created.
            elements_in_the_list (list[str]): A list of the names of the objects in the list.
            name ([str]): The name of the NetworkList.
            date_format (Optional[DateFormat]): The date format of the object.
            start_date (Optional[str]): The start date of the model (required if the date is in numerical format).
        """

        super().__init__(date=date, date_format=date_format, start_date=start_date, name=name)

        self.elements_in_the_list = elements_in_the_list
