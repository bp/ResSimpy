"""Class representing Drill Parameters in a Nexus Network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.Drill import Drill
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@dataclass(kw_only=True)
class NexusDrill(Drill):
    """Class representing Drill Parameters in a Nexus Network.

    Attributes:
        drillsite (Optional[str]): The name of the site from which the well will be drilled.
        drill_time (Optional[int]): The amount of time before the rig is released.
        completion_time (Optional[int]): Time needed to complete the well.
        workover_time (Optional[int]): Amount of time needed to workover the well.
        rigs (Optional[str]): Rigs that can be used to drill the well.
        replacement(Optional[str]): Wells that could be used as a replacement for the well.
    """

    drill_site: Optional[str] = None
    drill_time: Optional[float] = None
    completion_time: Optional[float] = None
    workover_time: Optional[float] = None
    rigs: Optional[str] = None
    replacement: Optional[str] = None

    def __init__(self, unit_system: Optional[UnitSystem] = None, name: Optional[str] = None, date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 drillsite: Optional[str] = None, drill_time: Optional[float] = None,
                 completion_time: float = 0, workover_time: float = 0, rigs: str = 'ALL',
                 replacement: Optional[str] = None,
                 properties_dict: Optional[dict[str, None | int | str | float]] = None) -> None:
        """Initialises the NexusDrill class.

        Args:
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the well / will list the drill relates to.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            drillsite (Optional[str]): The name of the site from which the well will be drilled.
            drill_time (Optional[float]): The amount of time before the rig is released.
            completion_time (Optional[float]): Time needed to complete the well.
            workover_time (Optional[float]): Amount of time needed to workover the well.
            rigs (Optional[str]): Rigs that can be used to drill the well.
            replacement(Optional[str]): Wells that could be used as a replacement for the well.
            properties_dict (dict): dict of the properties to set on the object.
        """

        self.drill_site = drillsite
        self.drill_time = drill_time
        self.completion_time = completion_time
        self.workover_time = workover_time
        self.rigs = rigs
        self.replacement = replacement

        super().__init__(unit_system=unit_system, name=name, date_format=date_format, start_date=start_date, date=date,
                         properties_dict=properties_dict)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping = {
            'WELL': ('name', str),
            'DRILLSITE': ('drill_site', str),
            'DRILLTIME': ('drill_time', float),
            'CMPLTIME': ('completion_time', float),
            'WORKTIME': ('workover_time', float),
            'RIGS': ('rigs', str),
            'REPLACEMENT': ('replacement', str),
        }

        return nexus_mapping

    @property
    def total_drill_time(self) -> float:
        """The total time to drill the well."""
        drill_time = self.drill_time if self.drill_time is not None else 0
        completion_time = self.completion_time if self.completion_time is not None else 0
        return drill_time + completion_time
