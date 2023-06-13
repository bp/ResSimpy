from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class RelPerm(ABC):
    """The abstract base class for a collection of relative permeability and capillary pressure property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Dictionary collection of relperm and capillary pressure property inputs.
    """

    @property
    def inputs(self):
        raise NotImplementedError("Implement this in the derived class")
