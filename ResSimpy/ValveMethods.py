from dataclasses import dataclass
from abc import ABC




@dataclass(kw_only=True)
class ValveMethods(ABC):
    """The abstract base class for a collection of valve property methods
    Attributes:
        valve_methods (dict[int, ValveMethod]): Collection of valve property methods, as a dictionary.
    """

    @property
    def valve_methods(self):  # -> MutableMapping[int, ValveMethod]:
        raise NotImplementedError("Implement this in the derived class")
