from dataclasses import dataclass
from abc import ABC

from ResSimpy.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class Rock(ABC):
    """The abstract base class for a collection of rock property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of rock property inputs, as a dictionary.
    """

    @property
    def inputs(self) -> dict[int, DynamicProperty]:
        """A Collection of rock property inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")

    def to_string(self) -> str:
        raise NotImplementedError('Implement this in the derived class.')
