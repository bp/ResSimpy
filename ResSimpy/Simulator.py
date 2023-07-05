"""The abstract base class for all simulators."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy.Aquifer import Aquifer
from ResSimpy.Equilibration import Equilibration
from ResSimpy.Gaslift import Gaslift
from ResSimpy.Hydraulics import Hydraulics
from ResSimpy.PVT import PVT
from ResSimpy.RelPerm import RelPerm
from ResSimpy.Rock import Rock
from ResSimpy.Separator import Separator
from ResSimpy.Valve import Valve
from ResSimpy.Water import Water
from ResSimpy.Wells import Wells


@dataclass(kw_only=True)
class Simulator(ABC):

    def __init__(self, start_date: str = '') -> None:
        self.__start_date: str = start_date
        self._wells: Wells = Wells()
        self._pvt: PVT = PVT()
        self._separator: Separator = Separator()
        self._water: Water = Water()
        self._equil: Equilibration = Equilibration()
        self._rock: Rock = Rock()
        self._relperm: RelPerm = RelPerm()
        self._valve: Valve = Valve()
        self._aquifer: Aquifer = Aquifer()
        self._hydraulics: Hydraulics = Hydraulics()
        self._gaslift: Gaslift = Gaslift()

    """Class Properties"""

    @property
    def start_date(self) -> str:
        return self.__start_date

    def start_date_set(self, value) -> None:
        self.__start_date = value

    @property
    def wells(self) -> Wells:
        return self._wells

    @property
    def pvt(self) -> PVT:
        return self._pvt

    @property
    def separator(self) -> Separator:
        return self._separator

    @property
    def water(self) -> Water:
        return self._water

    @property
    def equil(self) -> Equilibration:
        return self._equil

    @property
    def rock(self) -> Rock:
        return self._rock

    @property
    def relperm(self) -> RelPerm:
        return self._relperm

    @property
    def valve(self) -> Valve:
        return self._valve

    @property
    def aquifer(self) -> Aquifer:
        return self._aquifer

    @property
    def hydraulics(self) -> Hydraulics:
        return self._hydraulics

    @property
    def gaslift(self) -> Gaslift:
        return self._gaslift

    """ Class Methods """

    @staticmethod
    @abstractmethod
    def get_fluid_type(surface_file_name: str) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def model_location(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")
