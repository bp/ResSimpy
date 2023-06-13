from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Hydraulics(ABC):
    """The abstract base class for a collection of hydraulics inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of hydraulics inputs, as a dictionary.
    """

    @property
    def inputs(self):
        raise NotImplementedError("Implement this in the derived class")
