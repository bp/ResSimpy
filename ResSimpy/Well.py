"""The abstract base class for all wells"""

from abc import ABC
from dataclasses import dataclass

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
