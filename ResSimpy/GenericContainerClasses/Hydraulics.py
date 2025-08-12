from dataclasses import dataclass
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty
from ResSimpy.DataModelBaseClasses.DynamicPropertyContainer import DynamicPropertyContainer


@dataclass(kw_only=True)
class Hydraulics(DynamicPropertyContainer):
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

    def add_method(self, method: DynamicProperty, new_file_name: str,
                   create_new_file: bool = False) -> None:
        """Adds a new hydraulics method to the collection.

        Args:
            method (Hydraulics): The hydraulics method to add.
            new_file_name (str): The name of the file to save the method to.
            create_new_file (bool): Whether to create a new file for the method.
        """
        raise NotImplementedError("Implement this in the derived class")
