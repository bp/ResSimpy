from dataclasses import dataclass
from typing import Optional

from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Nexus.NexusEnums.ActivationChangeEnum import ActivationChangeEnum
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.BaseUnitMapping import BaseUnitMapping


@dataclass(kw_only=True, repr=True)
class NexusAction(NetworkObject):
    """A class representing a single Nexus action."""

    action_time: float  # don't assume it is an int just yet
    change: ActivationChangeEnum
    connection: str

    def __init__(self, properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None,
                 start_date: Optional[str] = None, unit_system: Optional[UnitSystem] = None) -> None:
        """Initializes the Nexus Action attributes."""

        # the fact that date is being explicitly set in the super call means that it would
        # technically be an unused parameter, but date is a requirement in the __init__ so we cannot
        # just get rid of it. So we implement a quick hack below.
        # This IF statement is necessary to pass the ruff check
        if date is None:
            pass

        # the action_time in the properties dict is the DATE
        action_time = ''  # expecting a float
        connection = ''

        if isinstance(properties_dict, dict):
            if isinstance(properties_dict['action_time'], float):
                action_time = str(properties_dict['action_time'])
            if isinstance(properties_dict['connection'], str):
                connection = properties_dict['connection']
        super().__init__(properties_dict=properties_dict, date=action_time,
                         date_format=date_format, start_date=start_date,
                         unit_system=unit_system, name=connection)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of keywords to attribute definitions."""
        keywords = {
            'ACTIONTIME': ('action_time', float),
            'ACTION': ('change', ActivationChangeEnum),
            'CONNECTION': ('connection', str),
        }
        return keywords

    @property
    def units(self) -> BaseUnitMapping:
        """Returns the attribute to unit map for the data object."""
        return BaseUnitMapping(unit_system=self.unit_system)
