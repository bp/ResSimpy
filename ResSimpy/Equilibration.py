"""This module contains the abstract base class for a collection of equilibration inputs."""
from dataclasses import dataclass
from abc import ABC


@dataclass(kw_only=True)
class Equilibration(ABC):
    """The abstract base class for a collection of equilibration inputs.

    Attributes:
        inputs (dict[int, DynamicProperty]): Collection of equilibration inputs, as a dictionary.
    """

    @property
    def inputs(self):
        raise NotImplementedError("Implement this in the derived class")

    def to_string(self):
        raise NotImplementedError('Implement this in the derived class.')
