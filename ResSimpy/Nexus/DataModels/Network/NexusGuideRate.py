"""Class representing formula Parameters for guide rates in a Nexus Network."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.GuideRate import GuideRate
from ResSimpy.Enums.FluidTypeEnums import PhaseType
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat


@dataclass(kw_only=True)
class NexusGuideRate(GuideRate):
    """Class representing formula Parameters for guide rates in a Nexus Network."""

    def __init__(self, unit_system: Optional[UnitSystem] = None, name: Optional[str] = None, date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 time_interval: Optional[float] = 0, phase: Optional[PhaseType] = PhaseType.OIL, a: Optional[float] = 0,
                 b: Optional[float] = 0, c: Optional[float] = 0, d: Optional[float] = 0,
                 e: Optional[float] = 0, f: Optional[float] = 0, increase_permitted: Optional[bool] = True,
                 damping_factor: Optional[float] = 1.0,
                 properties_dict: Optional[dict[str, None | int | str | float]] = None) -> None:
        """Initialises the NexusDrill class.

        Args:
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the well / will list the drill relates to.
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            time_interval (Optional[Float]): The minimum time interval between calculations.
            phase(Optional[PhaseType]): The phase used for the calculation e.g. OIL.
            a (Optional[float]): parameter a in the guide rate formula.
            b (Optional[float]): parameter b in the guide rate formula.
            c (Optional[float]): parameter c in the guide rate formula.
            d (Optional[float]): parameter d in the guide rate formula.
            e (Optional[float]): parameter e in the guide rate formula.
            f (Optional[float]): parameter f in the guide rate formula.
            increase_permitted(Optional[bool]): Whether guide rate is allowed to increase or not.
            damping_factor(Optional[float]): The dame factor.
            properties_dict (dict): dict of the properties to set on the object.
        """

        super().__init__(unit_system=unit_system, name=name, date_format=date_format, start_date=start_date, date=date,
                         properties_dict=properties_dict, time_interval=time_interval, phase=phase, a=a, b=b, c=c, d=d,
                         e=e, f=f, increase_permitted=increase_permitted, damping_factor=damping_factor)

    @staticmethod
    def get_keyword_mapping() -> dict[str, tuple[str, type]]:
        """Gets the mapping of nexus keywords to attribute definitions."""
        nexus_mapping = {
            'TARGET': ('name', str),
            'DTMIN': ('time_interval', float),
            'PHASE': ('phase', str),
            'A': ('a', float),
            'B': ('b', float),
            'C': ('c', float),
            'D': ('d', float),
            'E': ('e', float),
            'F': ('f', float),
            'INCREASE': ('increase_permitted', bool),
            'DAMP': ('damping_factor', float)
        }

        return nexus_mapping
