from dataclasses import dataclass
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.DataModelBaseClasses.DynamicPropertyContainer import DynamicPropertyContainer


@dataclass(kw_only=True)
class Separator(DynamicPropertyContainer):
    """The abstract base class for a collection of separator property inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of separator property inputs, as a dictionary.
    """

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of separator property inputs, as a dictionary."""
        raise NotImplementedError("Implement this in the derived class.")

    def to_string(self) -> str:
        """Writes dynamic property data to string."""
        raise NotImplementedError('Implement this in the derived class.')
