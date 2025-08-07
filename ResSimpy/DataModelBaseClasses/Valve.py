from dataclasses import dataclass
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.DataModelBaseClasses.DynamicPropertyContainer import DynamicPropertyContainer


@dataclass(kw_only=True)
class Valve(DynamicPropertyContainer):
    """The abstract base class for a collection of valve property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of valve property inputs, as a dictionary.
    """

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of valve property inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
