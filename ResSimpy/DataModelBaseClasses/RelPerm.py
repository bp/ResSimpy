from dataclasses import dataclass
from abc import ABC
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class RelPerm(ABC):
    """The abstract base class for a collection of relative permeability and capillary pressure property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Dictionary collection of relperm and capillary pressure property inputs.
    """

    @property
    def summary(self) -> str:
        """Returns string summary of RelPerm properties."""
        raise NotImplementedError("Implement this in the derived class")

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """Returns mapping of dynamic property instance as an int."""
        raise NotImplementedError("Implement this in the derived class")
