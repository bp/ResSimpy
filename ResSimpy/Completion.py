"""The abstract base class for all wells"""

from dataclasses import dataclass


@dataclass
class Completion():
    def __init__(self, i: int, j: int, k: int, well_radius: float, date: str):
        self.__i: int = i
        self.__j: int = j
        self.__k: int = k
        self.__well_radius: float = well_radius
        self.__date: str = date

    @property
    def well_radius(self):
        return self.__well_radius
