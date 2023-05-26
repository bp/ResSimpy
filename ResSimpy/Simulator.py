"""The abstract base class for all simulators."""

from abc import ABC, abstractmethod
from typing import Optional
from ResSimpy.Wells import Wells
from ResSimpy.RockMethods import RockMethods


class Simulator(ABC):

    def __init__(self, start_date: str = '') -> None:
        self.__start_date: str = start_date
        self.__Wells: Wells = Wells()
        self.__RockMethods: RockMethods = RockMethods()

    """Class Properties"""

    @property
    def start_date(self) -> str:
        return self.__start_date

    def start_date_set(self, value) -> None:
        self.__start_date = value

    @property
    def Wells(self) -> Wells:
        return self.__Wells

    @Wells.setter
    def Wells(self, cls):
        if not isinstance(cls, Wells):
            raise ValueError(f"Wells must take a valid Wells type. Instead got provided class of {type(cls)}")
        self.__Wells = cls

    @property
    def RockMethods(self) -> RockMethods:
        return self.__RockMethods

    @RockMethods.setter
    def RockMethods(self, cls):
        if not isinstance(cls, RockMethods):
            raise ValueError(
                f"RockMethods must take a valid RockMethods type. Instead got provided class of {type(cls)}")
        self.__RockMethods = cls

    """ Class Methods """

    @staticmethod
    @abstractmethod
    def get_fluid_type(surface_file_name: str) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def get_simulation_status(self) -> Optional[str]:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def get_simulation_progress(self) -> float:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def model_location(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")
