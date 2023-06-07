from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class HydraulicsMethods(ABC):
    """The abstract base class for a collection of hydraulics methods
    Attributes:
        hydraulics_methods (dict[int, HydraulicsMethod]): Collection of hydraulics methods, as a dictionary.
    """

    @property
    def hydraulics_methods(self):  # -> MutableMapping[int, HydraulicsMethod]:
        raise NotImplementedError("Implement this in the derived class")
