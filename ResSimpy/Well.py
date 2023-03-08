"""The abstract base class for all wells"""
from abc import ABC
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, Union

from ResSimpy.Completion import Completion
from ResSimpy.Nexus.NexusEnums.UnitsEnum import UnitSystem


@dataclass
class Well(ABC):
    __completions: list[Completion]
    __well_name: str
    __units: UnitSystem

    def __init__(self, well_name, completions, units):
        self.__well_name = well_name
        self.__completions = completions
        self.__units = units

    @property
    def completions(self) -> list[Completion]:
        return self.__completions

    @property
    def well_name(self) -> str:
        return self.__well_name

    @property
    def units(self) -> UnitSystem:
        return self.__units

    @property
    def perforations(self) -> Sequence[Completion]:
        """Returns a list of all of the perforations for the well"""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def first_perforation(self) -> Optional[Completion]:
        """Returns the first perforation for the well"""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def shutins(self) -> Sequence[Completion]:
        """Returns a list of all of the perforations for the well"""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def last_shutin(self) -> Optional[Completion]:
        """Returns the first perforation for the well"""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def printable_well_info(self) -> str:
        """Returns some printable well information in string format"""
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def completion_events(self) -> list[Tuple[str, Union[int, Tuple[float, float]]]]:
        """Returns a list of dates and values representing either the layer, or the depths of each perforation"""
        raise NotImplementedError("This method has not been implemented for this simulator yet")
