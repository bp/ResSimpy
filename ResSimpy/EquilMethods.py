from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class EquilMethods(ABC):
    """The abstract base class for a collection of equilibration methods
    Attributes:
        equil_methods (dict[int, EquilMethod]): Collection of equilibration methods, as a dictionary.
    """

    @property
    def equil_methods(self):  # -> MutableMapping[int, EquilMethod]:
        raise NotImplementedError("Implement this in the derived class")
