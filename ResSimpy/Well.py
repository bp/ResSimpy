"""The abstract base class for all wells"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy import Completion


@dataclass
class Well(ABC):
    __completions: list[Completion]
    __well_name: str

    def __init__(self, well_name, completions):
        self.__well_name = well_name
        self.__completions = completions

    @property
    def completions(self) -> list[Completion]:
        return self.__completions

    @property
    def well_name(self) -> str:
        return self.__well_name
