from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Aquifer(ABC):
    """The abstract base class for a collection of aquifer inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of aquifer inputs, as a dictionary.
    """

    @property
    def inputs(self):
        raise NotImplementedError("Implement this in the derived class")
