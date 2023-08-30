from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class PVT(ABC):
    """The abstract base class for a collection of PVT inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of PVT inputs, as a dictionary.
    """

    @property
    def inputs(self):
        raise NotImplementedError("Implement this in the derived class")
