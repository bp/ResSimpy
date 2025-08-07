from dataclasses import dataclass
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.DataModelBaseClasses.DynamicPropertyContainer import DynamicPropertyContainer


@dataclass(kw_only=True)
class Water(DynamicPropertyContainer):
    """The abstract base class for a collection of water property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of water property methods, as a dictionary.
    """

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of water property methods, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class")
