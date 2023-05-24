from dataclasses import dataclass
from abc import ABC
# from typing import MutableMapping
# from ResSimpy.RelPermMethod import RelPermMethod


@dataclass(kw_only=True)
class RelPermMethods(ABC):
    """The abstract base class for a collection of relative permeability and capillary pressure property methods
    Attributes:
        relperm_methods (dict[int, RelPermMethod]): Dictionary collection of relperm and cap pressure property methods
    """

    @property
    def relperm_methods(self):  # -> MutableMapping[int, RelPermMethod]:
        raise NotImplementedError("Implement this in the derived class")
