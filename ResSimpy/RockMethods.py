from dataclasses import dataclass
from abc import ABC
from typing import Optional
from ResSimpy.RockMethod import RockMethod


@dataclass(kw_only=True)
class RockMethods(ABC):
    """The abstract base class for a collection of rock property methods
    Attributes:
        rock_methods (dict[int, RockMethod]): Collection of rock property methods, as a dictionary
    """

    __rock_methods: dict[int, RockMethod]

    def __init__(self, rock_methods: Optional[dict[int, RockMethod]] = None):
        if rock_methods:
            self.__rock_methods = rock_methods
        else:
            self.__rock_methods = {}

    @property
    def rock_methods(self) -> dict[int, RockMethod]:
        raise NotImplementedError("Implement this in the derived class")
