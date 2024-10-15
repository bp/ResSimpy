"""This module contains the abstract base class for a collection of equilibration inputs."""
from dataclasses import dataclass
from abc import ABC
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass(kw_only=True)
class Equilibration(ABC):
    """The abstract base class for a collection of equilibration inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of equilibration inputs, as a dictionary.
    """

    @property
    def summary(self) -> str:
        """Returns string summary of Equilibration properties."""
        raise NotImplementedError("Implement this in derived class")

    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """Returns a mapping of equilibration inputs."""
        raise NotImplementedError("Implement this in the derived class")

    def to_string(self) -> str:
        """Create string with equilibration data in Nexus file format."""
        raise NotImplementedError('Implement this in the derived class.')
