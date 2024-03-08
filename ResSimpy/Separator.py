from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Separator(ABC):
    """The abstract base class for a collection of separator property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of separator property inputs, as a dictionary.
    """

    @property
    def inputs(self):
        """A Collection of separator property inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class.")

    def to_string(self):
        raise NotImplementedError('Implement this in the derived class.')
