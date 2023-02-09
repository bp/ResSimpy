"""The abstract base class for all simulators"""

from abc import ABC, abstractmethod
from typing import Optional
from ResSimpy.Wells import Wells


class Simulator(ABC):

    def __init__(self, start_date=''):
        self.__start_date = start_date
        self.__Wells: Wells = Wells()
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
    def get_model_location(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")
