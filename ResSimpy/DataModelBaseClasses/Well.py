"""The abstract base class for all wells."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional, Sequence

from ResSimpy.DataModelBaseClasses.Completion import Completion
from ResSimpy.Enums.UnitsEnum import UnitSystem
from ResSimpy.Enums.WellTypeEnum import WellType


@dataclass
class Well(ABC):
    _completions: list[Completion]
    _well_name: str
    __unit_system: UnitSystem
    _well_type: Optional[WellType]

    def __init__(self, well_name: str, completions: list[Completion], unit_system: UnitSystem,
                 well_type: Optional[WellType] = None) -> None:
        """Initialises the ConstraintUnits class.

        Args:
            well_name (str): The name of the well.
            completions (list[Completion]): A list of all the completions on the well.
            unit_system (None | UnitSystem): The unit system associated with the properties on this well.
            well_type (Optional[WellType]): The type of the well represented by a WellType Enum.
        """
        self._well_name = well_name
        self._completions = completions
        self.__unit_system = unit_system
        self._well_type = well_type

    @property
    def completions(self) -> list[Completion]:
        """A list of all the completions on the well."""
        return self._completions

    @property
    def well_name(self) -> str:
        """The well name."""
        return self._well_name

    @property
    def unit_system(self) -> UnitSystem:
        """The unit system associated with the properties on this well."""
        return self.__unit_system

    @property
    def well_type(self) -> WellType | None:
        """The type of the well."""
        return self._well_type

    @well_type.setter
    def well_type(self, val: WellType) -> None:
        """Sets the well type."""
        if not isinstance(val, WellType):
            raise ValueError(f"Invalid well type: {val}")

        self._well_type = val

    @property
    def dates_of_completions(self) -> list[str]:
        """Returns a list of dates that the well was changed using a completion."""

        dates_changed: list[str] = []
        for completion in self._completions:
            if completion.date not in dates_changed and completion.date is not None:
                dates_changed.append(completion.date)

        return dates_changed

    @property
    def perforations(self) -> list[Completion]:
        """Returns a list of all of the perforations for the well."""

        activations = filter(lambda x: x.completion_is_perforation, self._completions)
        return list(activations)

    @property
    def first_perforation(self) -> Optional[Completion]:
        """Returns the first perforation for the well."""
        if len(self.perforations) == 0:
            return None

        return self.perforations[0]

    @property
    def shutins(self) -> Sequence[Completion]:
        """Returns a list of all the shut-ins for the well."""

        shutins = filter(lambda x: x.completion_is_shutin, self._completions)
        return list(shutins)

    @property
    def last_shutin(self) -> Optional[Completion]:
        """Returns the last shut-in for the well in the Wellspec file."""
        if len(self.shutins) == 0:
            return None

        return self.shutins[-1]

    @property
    def printable_well_info(self) -> str:
        """Returns some printable well information in string format."""
        printable_dates_of_completions = ", ".join(self.dates_of_completions)
        well_info = \
            f"""
    Well Name: {self.well_name}
    First Perforation: {'N/A' if self.first_perforation is None else self.first_perforation.date}
    Last Shut-in: {'N/A' if self.last_shutin is None else self.last_shutin.date}
    Dates Changed: {'N/A' if len(self.dates_of_completions) == 0 else printable_dates_of_completions}
    """

        return well_info

    @property
    def open_and_shut_events(self) -> list[tuple[str, int | tuple[float, float]]]:
        """Returns a list of dates and values representing either the layer, or the depths of each perforation."""
        events: list[tuple[str, int | tuple[float, float]]] = []
        using_k_values: Optional[bool] = None

        for completion in self._completions:
            is_perforation = completion.completion_is_perforation
            if not is_perforation:
                continue
            if completion.k is not None and using_k_values is not False:
                using_k_values = True
                if completion.date is not None:
                    events.append((completion.date, completion.k))
            elif completion.depth_to_top is not None and using_k_values is not True \
                    and completion.depth_to_bottom is not None:
                using_k_values = False
                if completion.date is not None:
                    events.append((completion.date, (completion.depth_to_top, completion.depth_to_bottom)))

        return events
