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
        self.__wells: Wells = Wells()
        self.pvt: PVT = PVT()
        self.separator: Separator = Separator()
        self.water: Water = Water()
        self.equil: Equilibration = Equilibration()
        self.rock: Rock = Rock()
        self.relperm: RelPerm = RelPerm()
        self.valve: Valve = Valve()
        self.aquifer: Aquifer = Aquifer()
        self.hydraulics: Hydraulics = Hydraulics()
        self.gaslift: Gaslift = Gaslift()

    """Class Properties"""

    @property
    def start_date(self) -> str:
        return self.__start_date

    def start_date_set(self, value) -> None:
        self.__start_date = value

    @property
    def wells(self) -> Wells:
        return self.__wells

    @wells.setter
    def wells(self, cls):
        if not isinstance(cls, Wells):
            raise ValueError(f"Wells must take a valid Wells type. Instead got provided class of {type(cls)}")
        self.__wells = cls

    @property
    def pvt(self) -> PVT:
        return self.pvt

    @pvt.setter
    def pvt(self, cls):
        if not isinstance(cls, PVT):
            raise ValueError(f"pvt must take a valid pvt type."
                             f"Instead got provided class of {type(cls)}")
        self.pvt = cls

    @property
    def separator(self) -> Separator:
        return self.separator

    @separator.setter
    def separator(self, cls):
        if not isinstance(cls, Separator):
            raise ValueError(f"separator must take a valid separator type."
                             F"Instead got provided class of {type(cls)}")
        self.separator = cls

    @property
    def water(self) -> Water:
        return self.water

    @water.setter
    def water(self, cls):
        if not isinstance(cls, Water):
            raise ValueError(f"water must take a valid water type."
                             f"Instead got provided class of {type(cls)}")
        self.water = cls

    @property
    def equil(self) -> Equilibration:
        return self.equil

    @equil.setter
    def equil(self, cls):
        if not isinstance(cls, Equilibration):
            raise ValueError(f"equil must take a valid equil type."
                             f"Instead got provided class of {type(cls)}")
        self.equil = cls

    @property
    def rock(self) -> Rock:
        return self.rock

    @rock.setter
    def rock(self, cls):
        if not isinstance(cls, Rock):
            raise ValueError(f"rock must take a valid rock type."
                             f"Instead got provided class of {type(cls)}")
        self.rock = cls

    @property
    def relperm(self) -> RelPerm:
        return self.relperm

    @relperm.setter
    def relperm(self, cls):
        if not isinstance(cls, RelPerm):
            raise ValueError(f"relperm must take a valid relperm type."
                             f"Instead got provided class of {type(cls)}")
        self.relperm = cls

    @property
    def valve(self) -> Valve:
        return self.valve

    @valve.setter
    def valve(self, cls):
        if not isinstance(cls, Valve):
            raise ValueError(f"valve must take a valid valve type."
                             f"Instead got provided class of {type(cls)}")
        self.valve = cls

    @property
    def aquifer(self) -> Aquifer:
        return self.aquifer

    @aquifer.setter
    def aquifer(self, cls):
        if not isinstance(cls, Aquifer):
            raise ValueError(f"aquifer must take a valid aquifer type."
                             f"Instead got provided class of {type(cls)}")
        self.aquifer = cls

    @property
    def hydraulics(self) -> Hydraulics:
        return self.hydraulics

    @hydraulics.setter
    def hydraulics(self, cls):
        if not isinstance(cls, Hydraulics):
            raise ValueError(f"hydraulics must take a valid hydraulics type. Instead got provided class of {type(cls)}")
        self.hydraulics = cls

    @property
    def gaslift(self) -> Gaslift:
        return self.gaslift

    @gaslift.setter
    def gaslift(self, cls):
        if not isinstance(cls, Gaslift):
            raise ValueError(f"gaslift must take a valid gaslift type. Instead got provided class of {type(cls)}")
        self.gaslift = cls

    """ Class Methods """

    @staticmethod
    @abstractmethod
    def get_fluid_type(surface_file_name: str) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def model_location(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")


