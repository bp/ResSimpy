from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Water(ABC):
    """The abstract base class for a collection of water property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of water property methods, as a dictionary.
    """

    @property
    def inputs(self):
        """A Collection of water property methods, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
