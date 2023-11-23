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
    __well_name: str
    __unit_system: UnitSystem

    def __init__(self, well_name: str, completions: list[Completion], unit_system: UnitSystem) -> None:
        self.__well_name = well_name
        self._completions = completions
        self.__unit_system = unit_system

    @property
    def completions(self) -> list[Completion]:
        return self._completions

    @property
    def well_name(self) -> str:
        return self.__well_name

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
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def completion_events(self) -> list[tuple[str, Union[int, tuple[float, float]]]]:
        """Returns a list of dates and values representing either the layer, or the depths of each perforation."""
        raise NotImplementedError("This method has not been implemented for this simulator yet")
