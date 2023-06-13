from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Gaslift(ABC):
    """The abstract base class for a collection of gaslift property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of gaslift property inputs, as a dictionary.
    """

    @property
    def inputs(self):
        raise NotImplementedError("Implement this in the derived class")
