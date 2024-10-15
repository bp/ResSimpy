from dataclasses import dataclass
from abc import ABC
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class Hydraulics(ABC):
    """The abstract base class for a collection of hydraulics inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of hydraulics inputs, as a dictionary.
    """

    @property
    def summary(self) -> str:
        """Returns string summary of Hydraulics properties."""
        raise NotImplementedError("Implement this in a derived class")

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of hydraulics inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
