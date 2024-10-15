"""Abstract base class for aquifer inputs."""
from dataclasses import dataclass
from abc import ABC
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class Aquifer(ABC):
    """The abstract base class for a collection of aquifer inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of aquifer inputs, as a dictionary.
    """

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of aquifer inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
