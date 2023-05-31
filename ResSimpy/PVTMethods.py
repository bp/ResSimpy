from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class PVTMethods(ABC):
    """The abstract base class for a collection of PVT methods
    Attributes:
        pvt_methods (dict[int, PVTMethod]): Collection of PVT methods, as a dictionary.
    """

    @property
    def pvt_methods(self):  # -> MutableMapping[int, PVTMethod]:
        raise NotImplementedError("Implement this in the derived class")
