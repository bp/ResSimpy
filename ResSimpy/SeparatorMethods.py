from dataclasses import dataclass
from abc import ABC


# from typing import MutableMapping
# from ResSimpy.SeparatorMethod import SeparatorMethod


@dataclass(kw_only=True)
class SeparatorMethods(ABC):
    """The abstract base class for a collection of separator property methods
    Attributes:
        separator_methods (dict[int, SeparatorMethod]): Collection of separator property methods, as a dictionary.
    """

    @property
    def separator_methods(self):  # -> MutableMapping[int, SeparatorMethod]:
        raise NotImplementedError("Implement this in the derived class")
