from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass
class DynamicPropertyContainer(ABC):
    """Class for handling a collection of dynamic properties, such as PVT, relperm, etc."""

    @property
    @abstractmethod
    def inputs(self) -> Mapping[int, DynamicProperty]:
        """A Collection of dynamic properties, as a dictionary, keyed by method number."""
        raise NotImplementedError("Implement this in the derived class.")
