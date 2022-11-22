"""The abstract base class for all simulators"""

from abc import ABC, abstractmethod


class Simulator(ABC):

    def __init__(self, start_date=''):
        self.__start_date = start_date

    """Class Properties"""
    @property
    def start_date(self) -> str:
        return self.__start_date

    def start_date_set(self, value) -> None:
        self.__start_date = value

    """ Class Methods """
    @staticmethod
    @abstractmethod
    def get_fluid_type(surface_file_name: str) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def get_simulation_status(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def get_simulation_progress(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")

    @abstractmethod
    def get_model_location(self) -> str:
        raise NotImplementedError("This method has not been implemented for this simulator yet")
