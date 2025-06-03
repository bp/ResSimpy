from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.DataModelBaseClasses.NetworkObject import NetworkObject
from ResSimpy.Enums.FluidTypeEnums import PhaseType
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Nexus.NexusEnums.DateFormatEnum import DateFormat
from ResSimpy.Units.AttributeMappings.NetworkUnitMapping import NetworkUnits


@dataclass(repr=False)
class GuideRate(NetworkObject, ABC):
    time_interval: Optional[float]
    phase: Optional[PhaseType]
    a: Optional[float]
    b: Optional[float]
    c: Optional[float]
    d: Optional[float]
    e: Optional[float]
    f: Optional[float]
    increase_permitted: Optional[bool]
    damping_factor: Optional[float]

    def __init__(self, unit_system: Optional[UnitSystem] = None, name: Optional[str] = None, date: Optional[str] = None,
                 date_format: Optional[DateFormat] = None, start_date: Optional[str] = None,
                 properties_dict: Optional[dict[str, None | int | str | float]] = None,
                 time_interval: Optional[float] = None, phase: Optional[PhaseType] = None, a: Optional[float] = None,
                 b: Optional[float] = None, c: Optional[float] = None, d: Optional[float] = None,
                 e: Optional[float] = None, f: Optional[float] = None, increase_permitted: Optional[bool] = None,
                 damping_factor: Optional[float] = None) -> None:
        """Initialises the GuideRate class.

        Args:
            date (Optional[str]): The date of the object.
            date_format (Optional[DateFormat]): The date format that the object uses.
            start_date (Optional[str]): The start date of the model. Required if the object uses a decimal TIME.
            unit_system (Optional[UnitSystem]): The unit system of the object e.g. ENGLISH, METRIC.
            name (Optional[str]): The name of the object.
            properties_dict (dict): dict of the properties to set on the object.
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
        """
        self.time_interval = time_interval
        self.phase = phase
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.increase_permitted = increase_permitted
        self.damping_factor = damping_factor

        super().__init__(unit_system=unit_system, name=name, date=date, date_format=date_format, start_date=start_date,
                         properties_dict=properties_dict)

    @property
    def units(self) -> NetworkUnits:
        """Returns the attribute to unit map for the Drill."""
        return NetworkUnits(self.unit_system)
