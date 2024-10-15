from dataclasses import dataclass
from abc import ABC
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class Gaslift(ABC):
    """The abstract base class for a collection of gaslift property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of gaslift property inputs, as a dictionary.
    """

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """Returns mapping of gaslift property inputs."""
        raise NotImplementedError("Implement this in the derived class")
