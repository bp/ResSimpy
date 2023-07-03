"""The abstract base class for all simulators."""

from abc import ABC, abstractmethod
from typing import Optional
from ResSimpy.Wells import Wells


class Simulator(ABC):

    def __init__(self, start_date: str = '') -> None:
        self.__start_date: str = start_date
        self.__wells: Wells = Wells()

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

    """ Class Methods """

    @abstractmethod
    def model_location(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")
