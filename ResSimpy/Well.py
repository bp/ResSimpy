"""The abstract base class for all wells"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ResSimpy import Completion


class Well(ABC):
    def __init__(self, completions: list[Completion], well_name: str):
        self.__completions: list[Completion] = completions
        self.__well_name: str = well_name

    @property
    def completions(self) -> list[Completion]:
        return self.__completions

    @property
    def well_name(self) -> str:
        return self.__well_name
