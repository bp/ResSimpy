"""The abstract base class for all wells."""
from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from typing import Optional, Sequence, Union

from ResSimpy.Completion import Completion
from ResSimpy.Enums.UnitsEnum import UnitSystem


@dataclass
class Well(ABC):
    _completions: list[Completion]
    _well_name: str
    __unit_system: UnitSystem

    def __init__(self, well_name: str, completions: list[Completion], unit_system: UnitSystem) -> None:
        self._well_name = well_name
        self._completions = completions
        self.__unit_system = unit_system

    @property
    def completions(self) -> list[Completion]:
        return self._completions

    @property
    def well_name(self) -> str:
        return self._well_name

    @property
    def unit_system(self) -> UnitSystem:
        return self.__unit_system

    @property
    def dates_of_completions(self) -> list[str]:
        """Returns a list of dates that the well was changed using a completion."""

        dates_changed: list[str] = []
        for completion in self._completions:
            if completion.date not in dates_changed:
                dates_changed.append(completion.date)

        return dates_changed

    @property
    def perforations(self) -> Sequence[Completion]:
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
        """Returns a list of all of the shut-ins for the well."""

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
    def open_and_shut_events(self) -> list[tuple[str, Union[int, tuple[float, float]]]]:
        """Returns a list of dates and values representing either the layer, or the depths of each perforation."""
        events = []
        using_k_values: Optional[bool] = None

        for completion in self._completions:
            is_perforation = completion.completion_is_perforation
            if not is_perforation:
                continue
            if completion.k is not None and using_k_values is not False:
                using_k_values = True
                events.append((completion.date, completion.k))
            elif completion.depth_to_top is not None and using_k_values is not True:
                using_k_values = False
                events.append((completion.date, (completion.depth_to_top, completion.depth_to_bottom)))

        return events
