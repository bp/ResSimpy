from dataclasses import dataclass
from abc import ABC
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class PVT(ABC):
    """The abstract base class for a collection of PVT inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of PVT inputs, as a dictionary.
    """

    @property
    def summary(self) -> str:
        """Returns string summary of PVT properties."""
        raise NotImplementedError("Implement this in the derived class")

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of PVT inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
