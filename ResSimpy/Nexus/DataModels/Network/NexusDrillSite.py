"""Class representing DrillSite Parameters in a Nexus Network."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.DrillSite import DrillSite
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@dataclass(kw_only=True)
class NexusDrillSite(DrillSite):
    """Class representing DrillSite Parameters in a Nexus Network.

    Attributes:
        max_rigs (int):  The maximum number of rigs allowed at the drill site.
    """

    def __init__(self, unit_system: Optional[UnitSystem] = None, name: Optional[str] = None, date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 max_rigs: int = 1, properties_dict: Optional[dict[str, None | int | str | float]] = None)\
            -> None:
        """Initialises the NexusDrill class.

        Args:
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the well / will list the drill relates to.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            max_rigs (Optional[int]): The maximum number of rigs allowed at the drill site.
            properties_dict (dict): dict of the properties to set on the object.
        """

        super().__init__(unit_system=unit_system, name=name, date_format=date_format, start_date=start_date, date=date,
                         max_rigs=max_rigs, properties_dict=properties_dict)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping = {
            'NAME': ('name', str),
            'MAXRIGS': ('max_rigs', int)
        }

        return nexus_mapping
