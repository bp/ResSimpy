from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True, repr=True)
class NexusActivationChange(NetworkObject):
    change: ActivationChangeEnum
    is_constraint_change: bool

    def __init__(self, change: ActivationChangeEnum, date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 name: Optional[str] = None, is_constraint_change: bool = False) -> None:
        """Initialises the NexusTarget class.

        Args:
            change: ActivationChangeEnum: The change in activation (i.e. whether it has been activated or deactivated).
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            name (Optional[str]): The name of the object that is being activated / deactivated.
            is_constraint_change (bool): Whether the activation change is the result of a constraint block or not.
        """
        self.change = change
        self.is_constraint_change = is_constraint_change
        super().__init__(date_format=date_format, start_date=start_date, name=name, date=date)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of keywords to attribute definitions."""
        raise NotImplementedError("Not relevant for this class")

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        raise NotImplementedError("Not relevant for this class")
