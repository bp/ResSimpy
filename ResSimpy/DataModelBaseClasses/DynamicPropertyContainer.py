from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping

from ResSimpy.DataModelBaseClasses.DynamicProperty import DynamicProperty


@dataclass
class DynamicPropertyContainer(ABC):

    @abstractmethod
    @property
    def inputs(self) -> Mapping[int, DynamicProperty]:
        raise NotImplementedError("Implement this in the derived class.")