"""The abstract base class for all wells"""

from abc import ABC
from dataclasses import dataclass
from typing import Optional

from ResSimpy.Completion import Completion
from ResSimpy.UnitsEnum import Units


@dataclass
class Well(ABC):
    __completions: list[Completion]
    __well_name: str
    __units: Units

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
    def units(self) -> Units:
        return self.__units

    @property
    def perforations(self) -> list[Completion]:
        """Returns a list of all of the perforations for the well"""
        return NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def first_perforation(self) -> Optional[str]:
        """Returns the first perforation for the well"""
        return NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def shutins(self) -> list[Completion]:
        """Returns a list of all of the perforations for the well"""
        return NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def last_shutin(self) -> Optional[str]:
        """Returns the first perforation for the well"""
        return NotImplementedError("This method has not been implemented for this simulator yet")

    @property
    def printable_well_info(self) -> str:
        """Returns some printable well information in string format"""
        return NotImplementedError("This method has not been implemented for this simulator yet")