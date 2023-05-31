from dataclasses import dataclass
from abc import ABC




@dataclass(kw_only=True)
class WaterMethods(ABC):
    """The abstract base class for a collection of water property methods
    Attributes:
        water_methods (dict[int, WaterMethod]): Collection of water property methods, as a dictionary.
    """

    @property
    def water_methods(self):  # -> MutableMapping[int, WaterMethod]:
        raise NotImplementedError("Implement this in the derived class")
