from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class RockMethods(ABC):
    """The abstract base class for a collection of rock property methods
    Attributes:
        rock_methods (dict[int, RockMethod]): Collection of rock property methods, as a dictionary.
    """

    @property
    def rock_methods(self):  # -> MutableMapping[int, RockMethod]:
        raise NotImplementedError("Implement this in the derived class")
