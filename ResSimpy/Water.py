from dataclasses import dataclass
from abc import ABC
from typing import Mapping

from ResSimpy.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class Water(ABC):
    """The abstract base class for a collection of water property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of water property methods, as a dictionary.
    """

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of water property methods, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
