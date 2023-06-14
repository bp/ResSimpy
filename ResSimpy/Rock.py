from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Rock(ABC):
    """The abstract base class for a collection of rock property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of rock property inputs, as a dictionary.
    """

    @property
    def inputs(self):
        raise NotImplementedError("Implement this in the derived class")
