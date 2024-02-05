from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Valve(ABC):
    """The abstract base class for a collection of valve property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of valve property inputs, as a dictionary.
    """

    @property
    def inputs(self):
        """A Collection of valve property inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
