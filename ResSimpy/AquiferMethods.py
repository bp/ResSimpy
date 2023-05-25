from dataclasses import dataclass
from abc import ABC
# from typing import MutableMapping
# from ResSimpy.AquiferMethod import AquiferMethod


@dataclass(kw_only=True)
class AquiferMethods(ABC):
    """The abstract base class for a collection of aquifer methods
    Attributes:
        aquifer_methods (dict[int, AquiferMethod]): Collection of aquifer methods, as a dictionary
    """

    @property
    def aquifer_methods(self):  # -> MutableMapping[int, AquiferMethod]:
        raise NotImplementedError("Implement this in the derived class")
