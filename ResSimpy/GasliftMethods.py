from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class GasliftMethods(ABC):
    """The abstract base class for a collection of gaslift property methods
    Attributes:
        gaslift_methods (dict[int, GasliftMethod]): Collection of gaslift property methods, as a dictionary.
    """

    @property
    def gaslift_methods(self):  # -> MutableMapping[int, GasliftMethod]:
        raise NotImplementedError("Implement this in the derived class")
